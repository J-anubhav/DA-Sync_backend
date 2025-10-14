import sys
import os
from pathlib import Path

# Add current directory AND parent to path
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

print(f"🔧 Current directory: {current_dir}")
print(f"🔧 Parent directory: {parent_dir}")

# Load .env from PARENT directory
from dotenv import load_dotenv
env_file = parent_dir / ".env"
print(f"📄 Loading .env from: {env_file}")
print(f"✅ .env exists: {env_file.exists()}")
load_dotenv(dotenv_path=env_file, override=True)

# Now import everything
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from config import settings
from database import get_db
from core.background_tasks import process_prescription_image

app = FastAPI(title=settings.app_name)

@app.get("/")
def home():
    return {"message": "Welcome to the Prescription Analyzer API!"}

@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.env,
        "gemini_configured": bool(settings.gemini_api_key)
    }

@app.get("/db/ping")
async def db_ping(db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await db.command("ping")
    return JSONResponse(result)

@app.post("/upload-and-process-prescription/")
async def upload_prescription(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        background_tasks.add_task(process_prescription_image, image_bytes, file.filename)
        return {
            "message": "Prescription received. Processing has started in the background.",
            "filename": file.filename
        }
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )