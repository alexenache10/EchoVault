import logging
import sys
from pathlib import Path

# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_app_logging():
    """Configures multi-handler logging for console and file output."""
    logger = logging.getLogger("EchoVault")
    logger.setLevel(logging.INFO)

    # Clean format for production-grade traceability
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler for real-time terminal monitoring
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File Handler for persistent debugging and audit trail
    file_handler = logging.FileHandler(LOG_DIR / "app.log")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_app_logging()