from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from DAsync_backend.config import settings  # type: ignore
from DAsync_backend.database import get_db  # type: ignore
from motor.motor_asyncio import AsyncIOMotorDatabase

app = FastAPI(title=settings.app_name)

@app.get("/")
def home():
    return {"message": "Welcome to the Prescription Analyzer API!"}

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.env}

@app.get("/db/ping")
async def db_ping(db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await db.command("ping")
    return JSONResponse(result)

@app.post("/upload-and-process-prescription/")
async def upload_prescription(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Lazy import to avoid startup failure if optional deps (e.g., cloudinary) are missing
    try:
        from DAsync_backend.core.background_tasks import process_prescription_image  # type: ignore
    except Exception as e:
        return JSONResponse({"error": f"Background task unavailable: {e}"}, status_code=500)

    image_bytes = await file.read()
    background_tasks.add_task(process_prescription_image, image_bytes, file.filename)
    return {
        "message": "Prescription received. Processing has started in the background.",
        "filename": file.filename
    }

