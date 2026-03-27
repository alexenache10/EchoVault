import subprocess
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AudioProcessor:
    @staticmethod
    def extract_audio(input_path: str, output_path: str) -> str:
        """Extracts and normalizes audio to 16kHz mono PCM for Whisper compatibility."""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found at: {input_path}")

        # FFmpeg command: -vn (no video), -ac 1 (mono), -ar 16000 (sample rate)
        command = [
            "ffmpeg", "-i", input_path, "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1", "-y", output_path
        ]

        try:
            # Capture stderr to debug FFmpeg issues in production
            subprocess.run(command, capture_output=True, check=True)
            return str(Path(output_path).absolute())
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg extraction failed: {e.stderr.decode()}")
            raise RuntimeError("Audio signal extraction failed.")

    @staticmethod
    def cleanup(*file_paths: str):
        """Standard cleanup for temporary files to prevent disk bloating."""
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)