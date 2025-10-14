import os
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the same directory as this file (same level as main.py)
CURRENT_DIR = Path(__file__).parent
load_dotenv(dotenv_path=CURRENT_DIR / ".env", override=True)

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "prescription-analyzer")
    env: str = os.getenv("ENV", "development")
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "prescriptions")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    cloudinary_cloud_name: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY", "")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", "")

settings = Settings()

# Back-compat uppercase constants (some modules may reference these)
GEMINI_API_KEY = settings.gemini_api_key
CLOUDINARY_CLOUD_NAME = settings.cloudinary_cloud_name
CLOUDINARY_API_KEY = settings.cloudinary_api_key
CLOUDINARY_API_SECRET = settings.cloudinary_api_secret