from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class TranscriptionRecord(Base):
    __tablename__ = 'transcriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    model_size = Column(String, nullable=False)

    # Audio Hash column meant to represent inference caching feature
    audio_hash = Column(String, nullable=False, index=True)
    language = Column(String, nullable=False)
    transcript_json = Column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint('audio_hash', 'model_size', name='_audio_model_uc'),
    )

DATABASE_URL = "sqlite:///./echo_vault.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)