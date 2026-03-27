from faster_whisper import WhisperModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TranscriberService:
    _instance = None
    _model = None

    def __new__(cls):
        # Implementation of Singleton pattern to ensure model is loaded only once in memory
        if cls._instance is None:
            cls._instance = super(TranscriberService, cls).__new__(cls)
        return cls._instance

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            logger.info(f"Initializing Whisper model: {settings.WHISPER_MODEL} on {settings.COMPUTE_DEVICE}")
            self._model = WhisperModel(
                settings.WHISPER_MODEL,
                device=settings.COMPUTE_DEVICE,
                compute_type=settings.COMPUTE_TYPE,
                download_root="./models" # Local storage for model weights
            )
        return self._model

    async def transcribe_stream(self, audio_path: str):
        """Asynchronous generator yielding transcription segments in real-time."""
        # beam_size=5 for balanced speed/accuracy; vad_filter=True to skip silence
        segments, info = self.model.transcribe(
            audio_path, beam_size=5, vad_filter=True
        )

        yield {"event": "info", "payload": {"language": info.language, "duration": round(info.duration, 2)}}

        for segment in segments:
            yield {
                "event": "segment",
                "payload": {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip()
                }
            }

transcriber = TranscriberService()