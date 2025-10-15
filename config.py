import os
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the PROJECT ROOT (parent of this file's directory)
CURRENT_DIR = Path(__file__).parent
PARENT_DIR = CURRENT_DIR.parent
ROOT_ENV = PARENT_DIR / ".env"
LOCAL_ENV = CURRENT_DIR / ".env"

# Load from root first
if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV, override=True)
# Then load from local without overriding already-set values
if LOCAL_ENV.exists():
    load_dotenv(dotenv_path=LOCAL_ENV, override=True)

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