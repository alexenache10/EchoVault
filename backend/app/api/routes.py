import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.audio_processor import AudioProcessor
from app.services.transcriber import transcriber
from app.utils.logger import logger
from app.models.schemas import TranscribeRequest

router = APIRouter()

@router.websocket("/ws/transcribe")
async def websocket_transcription(websocket: WebSocket):
    await websocket.accept()
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"New WebSocket session: {client_id}")
    
    temp_audio = f"temp_ws_{os.getpid()}.wav"
    full_transcript_buffer = []

    try:
        raw_input = await websocket.receive_text()
        data = json.loads(raw_input)
        
        file_path = data.get("file_path")
        language = data.get("language", "ro")
        model_size = data.get("model_size", "base")

        if not file_path or not os.path.exists(file_path):
            await websocket.send_json({"event": "error", "payload": "Invalid file path"})
            return

        await websocket.send_json({"event": "status", "payload": "Extracting audio..."})
        AudioProcessor.extract_audio(file_path, temp_audio)

        await websocket.send_json({"event": "status", "payload": "Processing AI..."})
        async for packet in transcriber.transcribe_stream(temp_audio, model_size=model_size, language=language):
            if packet["event"] == "segment":
                full_transcript_buffer.append(packet["payload"]["text"])
            await websocket.send_json(packet)

        logger.info(f"WS Completed for {client_id}")
        await websocket.send_json({"event": "completed", "payload": "Success"})

    except Exception as e:
        logger.error(f"WS Error: {str(e)}")
        await websocket.send_json({"event": "error", "payload": str(e)})
    finally:
        AudioProcessor.cleanup(temp_audio)
        await websocket.close()

@router.post("/transcribe/sync")
async def manual_transcription(payload: TranscribeRequest):
    temp_audio = f"temp_sync_{os.getpid()}.wav"
    full_text = []
    
    try:
        AudioProcessor.extract_audio(payload.file_path, temp_audio)
        
        async for packet in transcriber.transcribe_stream(
            temp_audio, 
            model_size=payload.model_size, 
            language=payload.language
        ):
            if packet["event"] == "segment":
                full_text.append(packet["payload"]["text"])
        
        return {
            "status": "success",
            "transcript": " ".join(full_text)
        }
    except Exception as e:
        logger.error(f"Sync test failed: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        AudioProcessor.cleanup(temp_audio)