from faster_whisper import WhisperModel
from app.core.config import settings
from app.utils.logger import logger

class TranscriberService:
    _instance = None
    _model = None

    def __new__(cls):
        # Singleton pattern prevents redundant model loading into VRAM/RAM
        if cls._instance is None:
            cls._instance = super(TranscriberService, cls).__new__(cls)
        return cls._instance

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            logger.info(f"Loading AI model [{settings.WHISPER_MODEL}] on {settings.COMPUTE_DEVICE}")
            self._model = WhisperModel(
                settings.WHISPER_MODEL,
                device=settings.COMPUTE_DEVICE,
                compute_type=settings.COMPUTE_TYPE,
                download_root="./models"
            )
            logger.info("Model weights loaded into memory successfully.")
        return self._model

    async def transcribe_stream(self, audio_path: str, language: str = None):
        logger.info(f"Beginning inference on: {audio_path} with language: {language or 'auto-detect'}")
        
        segments, info = self.model.transcribe(
            audio_path, 
            beam_size=5, 
            vad_filter=True,
            language=language
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
        
        logger.info("Inference stream reached EOF (End of File).")

transcriber = TranscriberService()