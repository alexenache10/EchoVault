import torch
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "EchoVault"
    VERSION: str = "0.1.1"
    API_V1_STR: str = "/api/v1"
    
    WHISPER_MODEL: str = "large-v3"
    # Allow CORS for common frontend development ports
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    DATA_DIR: Path = Path("./data").resolve()
    TEMP_DIR: Path = Path("./data/temp").resolve()


    @property
    def COMPUTE_DEVICE(self) -> Literal["cuda", "cpu"]:
        # Auto-detect CUDA availability for hardware acceleration
        return "cuda" if torch.cuda.is_available() else "cpu"
    
    @property
    def COMPUTE_TYPE(self) -> Literal["float16", "int8"]:
        # Use float16 for GPU performance, int8 for CPU efficiency (quantization)
        return "float16" if torch.cuda.is_available() else "int8"

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)