from pydantic import BaseModel
from typing import Optional

class TranscribeRequest(BaseModel):
    file_path: str
    language: Optional[str] = "ro"
    model_size: Optional[str] = "base"

class TranscriptionResponse(BaseModel):
    status: str
    transcript: Optional[str] = None
    message: Optional[str] = None