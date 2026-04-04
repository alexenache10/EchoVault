import os
from pathlib import Path
from faster_whisper import download_model
from app.utils.logger import logger

class ModelManager:
    BASE_DIR = Path(os.getcwd()) / "models"

    @classmethod
    def get_model_dir(cls, model_size: str) -> Path:
        return cls.BASE_DIR / model_size

    @classmethod
    def is_model_local(cls, model_size: str) -> bool:
        model_dir = cls.get_model_dir(model_size)
        return model_dir.exists() and any(model_dir.iterdir())

    @classmethod
    def ensure_model(cls, model_size: str) -> str:
        model_dir = cls.get_model_dir(model_size)
        
        if not cls.is_model_local(model_size):
            logger.warning(f"Model '{model_size}' not found locally. Initiating download...")
            model_dir.mkdir(parents=True, exist_ok=True)
            download_model(model_size, output_dir=str(model_dir))
            logger.info(f"Model '{model_size}' successfully downloaded to {model_dir}")
        else:
            logger.info(f"Model '{model_size}' verified locally at {model_dir}")

        return str(model_dir)