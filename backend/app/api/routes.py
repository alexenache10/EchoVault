import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.models.schemas import TranscriptionRequest, TranscriptionResponse
from app.services.audio_processor import AudioProcessor
from app.services.transcriber import transcriber

router = APIRouter()

@router.websocket("/ws/transcribe")
async def websocket_transcription(websocket: WebSocket):
    """Handles real-time bi-directional streaming for frontend feedback."""
    await websocket.accept()
    temp_audio = f"temp_ws_{os.getpid()}.wav"
    
    try:
        # Expecting JSON: {"file_path": "C:/path/to/video.mp4"}
        raw_data = await websocket.receive_text()
        data = json.loads(raw_data)
        file_path = data.get("file_path")

        await websocket.send_json({"event": "status", "payload": "Normalizing audio..."})
        AudioProcessor.extract_audio(file_path, temp_audio)

        await websocket.send_json({"event": "status", "payload": "AI Inferencing..."})
        async for packet in transcriber.transcribe_stream(temp_audio):
            await websocket.send_json(packet)

        await websocket.send_json({"event": "completed", "payload": "Success"})
    except Exception as e:
        await websocket.send_json({"event": "error", "payload": str(e)})
    finally:
        AudioProcessor.cleanup(temp_audio)
        await websocket.close()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def rest_transcription(request: TranscriptionRequest):
    """Simple REST endpoint for batch processing and Postman testing."""
    temp_audio = f"temp_rest_{os.getpid()}.wav"
    try:
        AudioProcessor.extract_audio(request.file_path, temp_audio)
        full_text = []
        # Consume the generator fully for a single REST response
        async for packet in transcriber.transcribe_stream(temp_audio):
            if packet["event"] == "segment":
                full_text.append(packet["payload"]["text"])
        
        return TranscriptionResponse(text=" ".join(full_text), status="completed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        AudioProcessor.cleanup(temp_audio)