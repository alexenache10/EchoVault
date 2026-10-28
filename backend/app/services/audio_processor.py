#import subprocess
import os
from pathlib import Path
from app.utils.logger import logger
import asyncio

class AudioProcessor:
    @staticmethod
    async def extract_audio(input_path: str, output_path: str) -> str:
        """
        Extracts audio stream and normalizes it to 16kHz mono PCM.
        This ensures compatibility with the Whisper model architecture.
        """
        if not os.path.exists(input_path):
            logger.error(f"Input file validation failed: {input_path}")
            raise FileNotFoundError(f"Source file not found: {input_path}")

        logger.info(f"Starting FFmpeg extraction for: {Path(input_path).name}")

        # FFmpeg utilitary needs to be installed already
        # Flags: -vn removes video, -ac 1 forces mono, -ar 16000 sets sample rate
        command = [
            "ffmpeg", "-i", input_path, "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1", "-y", output_path
        ]

        #try:
            # Running with capture_output to log internal FFmpeg errors if they occur
            #result = subprocess.run(
            #    command,
            #    capture_output=True,
            #    text=True,
            #    check=True
            #)

        process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )


        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode().strip()
            logger.error(f"FFmpeg process failed with exit code {process.returncode}: {error_message}")
            raise RuntimeError(f"Audio extraction failed: {error_message}")

        logger.info(f"Audio normalized successfully: {output_path}")
        return str(Path(output_path).resolve())


        
        # except subprocess.CalledProcessError as e:
        #     logger.error(
        #         f"FFmpeg failed with exit code {e.returncode}: {e.stderr}"
        #     )
        #     raise RuntimeError("Audio extraction failed.") from e

    @staticmethod
    def cleanup(*file_paths: str):
        """Removes temporary files to prevent storage leakage."""
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Temporary file cleaned: {path}")