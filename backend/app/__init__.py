from faster_whisper import WhisperModel
from app.core.config import settings
import asyncio

class TranscriberService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranscriberService, cls).__new__(cls)
        return cls._instance

    @property
    def engine(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                settings.WHISPER_MODEL,
                device=settings.COMPUTE_DEVICE,
                compute_type=settings.COMPUTE_TYPE,
                download_root="./models"
            )
        return self._model

    async def run_inference(self, audio_path: str):
        segments, info = self.engine.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        yield {"event": "metadata", "data": {"language": info.language, "duration": info.duration}}

        for segment in segments:
            yield {
                "event": "segment",
                "data": {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip()
                }
            }

transcriber = TranscriberService()