import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from app.models.database import TranscriptionRecord

class CacheManager:
    @staticmethod
    def get_audio_hash(file_path: str, block_size: int = 65536) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                sha256.update(block)
        return sha256.hexdigest()

    @staticmethod
    def get_cached_transcription(db: Session, audio_hash: str, model_size: str) -> Optional[TranscriptionRecord]:
        return db.query(TranscriptionRecord).filter(
            TranscriptionRecord.audio_hash == audio_hash,
            TranscriptionRecord.model_size == model_size
        ).first()

    @staticmethod
    def save_transcription(db: Session, record_data: dict):
        new_record = TranscriptionRecord(**record_data)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record