import time
from faster_whisper import WhisperModel
from app.core.config import settings
from app.utils.logger import logger
from app.services.model_manager import ModelManager

class TranscriberService:
    _instance = None
    _current_model_size = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranscriberService, cls).__new__(cls)
        return cls._instance

    def _get_model(self, model_size: str) -> WhisperModel:
        if self._model is None or self._current_model_size != model_size:
            local_model_path = ModelManager.ensure_model(model_size)
            
            logger.info(f"Loading local AI model from {local_model_path} on {settings.COMPUTE_DEVICE}")
            self._model = WhisperModel(
                model_size_or_path=local_model_path,
                device=settings.COMPUTE_DEVICE,
                compute_type=settings.COMPUTE_TYPE,
                local_files_only=True
            )
            self._current_model_size = model_size
        return self._model

    async def transcribe_stream(self, audio_path: str, model_size: str = "base", language: str = "ro"):
        start_time = time.time()
        logger.info(f"Initiating inference | Model: [{model_size}] | Target Lang: [{language}] | Target File: {audio_path}")
        
        model = self._get_model(model_size)
        
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True
        )

        yield {"event": "info", "payload": {"language": info.language, "model": model_size}}

        for segment in segments:
            yield {
                "event": "segment",
                "payload": {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip()
                }
            }
        
        duration = round(time.time() - start_time, 2)
        logger.info(f"Inference completed | Model: [{model_size}] | Processing Time: {duration} seconds")

transcriber = TranscriberService()