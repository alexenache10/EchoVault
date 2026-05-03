import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.audio_processor import AudioProcessor
from app.services.transcriber import transcriber
from app.utils.logger import logger
from app.models.schemas import TranscribeRequest
from collections import deque
from app.models.database import SessionLocal, TranscriptionRecord
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/ws/transcribe")
async def websocket_transcription(websocket: WebSocket):
    await websocket.accept()
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"New WebSocket session: {client_id}")
    

    db = SessionLocal()
    temp_audio = f"temp_ws_{os.getpid()}.wav"

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
        

        async for packet in transcriber.transcribe_stream(
            temp_audio, 
            db=db, 
            model_size=model_size, 
            language=language
        ):
            await websocket.send_json(packet)

        logger.info(f"WS Completed for {client_id}")
        await websocket.send_json({"event": "completed", "payload": "Success"})

    except Exception as e:
        logger.error(f"WS Error: {str(e)}")
        await websocket.send_json({"event": "error", "payload": str(e)})
    finally:
        db.close()
        AudioProcessor.cleanup(temp_audio)
        try:
            await websocket.close()
        except:
            pass

@router.post("/transcribe/sync")
async def manual_transcription(payload: TranscribeRequest, db: Session = Depends(get_db)):
    temp_audio = f"temp_sync_{os.getpid()}.wav"
    full_text = []
    
    try:
        AudioProcessor.extract_audio(payload.file_path, temp_audio)
        
        async for packet in transcriber.transcribe_stream(
            temp_audio, 
            db=db, 
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

@router.get("/logs")
async def get_logs(lines: int = 100):
    log_file = "logs/app.log"
    if not os.path.exists(log_file):
        return {"status": "error", "message": "Log file not found"}
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:

            last_lines = deque(f, maxlen=lines)
            return {"status": "success", "logs": "".join(last_lines)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    records = db.query(TranscriptionRecord).order_by(TranscriptionRecord.timestamp.desc()).all()
    return records

@router.get("/hardware")
async def get_hardware_status():
    import torch
    return {
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "engine": "faster-whisper",
        "vram_detected": torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 0
    }

@router.get("/stream")
async def stream_media(path: str):
    if not os.path.exists(path):
        return {"error": "File not found"}
    return FileResponse(path)