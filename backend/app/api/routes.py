import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.audio_processor import AudioProcessor
from app.services.transcriber import transcriber
from app.utils.logger import logger

router = APIRouter()

@router.websocket("/ws/transcribe")
async def websocket_transcription(websocket: WebSocket):
    """
    Handles stateful WebSocket connection for real-time transcription streaming.
    Client sends a JSON containing the 'file_path' to begin the pipeline.
    """
    await websocket.accept()
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"New WebSocket session established: {client_id}")
    
    temp_audio = f"temp_ws_{os.getpid()}.wav"
    full_transcript_buffer = [] # Prepared for future DB persistence

    try:
        # Expecting JSON: {"file_path": "/absolute/path/to/media.mp4"}
        raw_input = await websocket.receive_text()
        data = json.loads(raw_input)
        file_path = data.get("file_path")

        if not file_path:
            logger.warning(f"Client {client_id} sent empty file_path")
            await websocket.send_json({"event": "error", "payload": "Missing file_path"})
            return

        # Phase 1: Signal Extraction
        await websocket.send_json({"event": "status", "payload": "Extracting audio signal..."})
        AudioProcessor.extract_audio(file_path, temp_audio)

        # Phase 2: Neural Inference
        await websocket.send_json({"event": "status", "payload": "AI model is processing..."})
        async for packet in transcriber.transcribe_stream(temp_audio):
            if packet["event"] == "segment":
                full_transcript_buffer.append(packet["payload"]["text"])
            await websocket.send_json(packet)

        # TODO: Trigger Database Persistence Layer here
        # Example: await db.save_transcription(file_path, " ".join(full_transcript_buffer))
        logger.info(f"Transcription completed for {client_id}. Buffer size: {len(full_transcript_buffer)} segments.")
        
        await websocket.send_json({"event": "completed", "payload": "Process finished successfully"})

    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected prematurely.")
    except Exception as e:
        logger.error(f"Pipeline failure for {client_id}: {str(e)}")
        await websocket.send_json({"event": "error", "payload": f"Internal Error: {str(e)}"})
    finally:
        AudioProcessor.cleanup(temp_audio)
        await websocket.close()