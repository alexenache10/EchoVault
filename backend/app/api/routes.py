import os
import uuid
from pathlib import Path
from collections import deque
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import torch

from app.core.config import settings
from app.services.audio_processor import AudioProcessor
from app.services.transcriber import transcriber
from app.utils.logger import logger
from app.models.database import SessionLocal, TranscriptionRecord

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def resolve_secure_path(raw_path: str) -> Path:
    target = Path(raw_path).expanduser().resolve()
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Requested file does not exist")
    return target


@router.websocket("/ws/transcribe")
async def websocket_transcription(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()
    session_id = str(uuid.uuid4())
    temp_audio = str(settings.TEMP_DIR / f"{session_id}.wav")

    try:
        data = await websocket.receive_json()
        
        raw_file_path = data.get("file_path")
        language = data.get("language", "ro")
        model_size = data.get("model_size", "base")
        device = data.get("device", "cuda")

        if not raw_file_path:
            await websocket.send_json({"event": "error", "payload": "Path not provided"})
            return

        try:
            secure_path = resolve_secure_path(raw_file_path)
        except HTTPException:
            await websocket.send_json({"event": "error", "payload": "Invalid or inaccessible file path"})
            return

        await websocket.send_json({"event": "status", "payload": "Extracting audio..."})
        await AudioProcessor.extract_audio(str(secure_path), temp_audio)

        await websocket.send_json({"event": "status", "payload": "Processing AI..."})
        
        async for packet in transcriber.transcribe_stream(
            temp_audio, 
            db=db, 
            model_size=model_size, 
            language=language,
            device=device,
            original_path=str(secure_path),
            session_id=session_id
        ):
            await websocket.send_json(packet)

        await websocket.send_json({"event": "completed", "payload": "Success"})

    except WebSocketDisconnect:
        logger.info(f"Client disconnected for session {session_id}. Triggering termination.")
        transcriber.stop_session(session_id)
    except Exception as e:
        logger.error(f"WS Error in session {session_id}: {str(e)}")
        try:
            await websocket.send_json({"event": "error", "payload": str(e)})
        except Exception:
            pass
    finally:
        db.close()
        AudioProcessor.cleanup(temp_audio)
        try:
            await websocket.close()
        except Exception:
            pass

@router.get("/logs")
async def get_logs(lines: int = Query(default=100, ge=1, le=1000)):
    log_file = Path("logs/app.log")
    if not log_file.is_file():
        return {"status": "error", "message": "Log file not found"}
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            last_lines = deque(f, maxlen=lines)
            return {"status": "success", "logs": "".join(last_lines)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    return db.query(TranscriptionRecord).order_by(TranscriptionRecord.timestamp.desc()).all()

@router.get("/hardware")
async def get_hardware_status():
    status = {"device": "cpu", "vram_usage": 0.0, "vram_total": 1.0}
    if torch.cuda.is_available():
        free, total = torch.cuda.mem_get_info()
        status["device"] = "cuda"
        status["vram_usage"] = (total - free) / (1024 ** 3)
        status["vram_total"] = total / (1024 ** 3)
    return status

@router.post("/transcribe/stop")
async def stop_transcription(session_id: str = Query(...)):
    transcriber.stop_session(session_id)
    return {"status": "stop_signal_sent", "session_id": session_id}