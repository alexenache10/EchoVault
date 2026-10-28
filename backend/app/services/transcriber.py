import asyncio
import threading
from typing import Set
from faster_whisper import WhisperModel
from sqlalchemy.orm import Session
from app.utils.logger import logger
from app.services.model_manager import ModelManager
from app.services.cache_manager import CacheManager

class TranscriberService:
    _instance = None
    _model = None
    _current_model_size = None
    _current_device = None
    _active_stop_signals: Set[str] = set()
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranscriberService, cls).__new__(cls)
        return cls._instance

    def stop_session(self, session_id: str):
        with self._lock:
            self._active_stop_signals.add(session_id)

    def _is_stopped(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._active_stop_signals

    def _cleanup_session(self, session_id: str):
        with self._lock:
            self._active_stop_signals.discard(session_id)

    def _get_model(self, model_size: str, device: str) -> WhisperModel:
        with self._lock:
            if self._model is None or self._current_model_size != model_size or self._current_device != device:
                local_model_path = ModelManager.ensure_model(model_size)
                compute_type = "float16" if device == "cuda" else "int8"
                logger.info(f"Loading model {model_size} on {device}")
                self._model = WhisperModel(
                    model_size_or_path=local_model_path,
                    device=device,
                    compute_type=compute_type,
                    local_files_only=True
                )
                self._current_model_size = model_size
                self._current_device = device
            return self._model

    async def transcribe_stream(
        self, 
        audio_path: str, 
        db: Session, 
        model_size: str = "base", 
        language: str = "ro", 
        device: str = "cuda", 
        original_path: str = None,
        session_id: str = ""
    ):
        audio_hash = CacheManager.get_audio_hash(audio_path)
        cached = CacheManager.get_cached_transcription(db, audio_hash, model_size)

        if cached:
            logger.info(f"Cache hit for {audio_path} with model {model_size}")
            yield {"event": "info", "payload": {"language": cached.language, "model": cached.model_size, "cached": True}}
            for segment in cached.transcript_json:
                yield {"event": "segment", "payload": segment}
            return

        model = self._get_model(model_size, device)
        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def inference_worker():
            try:
                segments, info = model.transcribe(audio_path, language=language, beam_size=5, vad_filter=True)
                loop.call_soon_threadsafe(
                    queue.put_nowait, 
                    {"event": "info", "payload": {"language": info.language, "model": model_size, "cached": False, "device": device}}
                )

                collected = []
                for segment in segments:
                    if self._is_stopped(session_id):
                        break
                    seg_data = {
                        "start": round(segment.start, 2), 
                        "end": round(segment.end, 2), 
                        "text": segment.text.strip()
                    }
                    collected.append(seg_data)
                    loop.call_soon_threadsafe(queue.put_nowait, {"event": "segment", "payload": seg_data})

                if not self._is_stopped(session_id):
                    CacheManager.save_transcription(db, {
                        "file_path": original_path or audio_path,
                        "audio_hash": audio_hash,
                        "model_size": model_size,
                        "language": info.language,
                        "transcript_json": collected
                    })
            except Exception as e:
                loop.call_soon_threadsafe(queue.put_nowait, {"event": "error", "payload": str(e)})
            finally:
                self._cleanup_session(session_id)
                loop.call_soon_threadsafe(queue.put_nowait, None)

        threading.Thread(target=inference_worker, daemon=True).start()

        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

transcriber = TranscriberService()