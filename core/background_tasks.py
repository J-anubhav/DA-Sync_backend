import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))

# Reload .env
env_file = parent_dir / ".env"
print(f"🔄 Background task reloading .env from: {env_file}")
load_dotenv(dotenv_path=env_file, override=True)

import cloudinary
import cloudinary.uploader
from datetime import datetime, timezone

from config import settings
from database import prescription_collection
from core.preprocess import preprocess_text
from core.getGeminiJson import get_gemini_analysis_from_image

# Configure Cloudinary
print(f"☁️ Cloudinary config: {settings.cloudinary_cloud_name}")
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)

def process_prescription_image(image_bytes: bytes, filename: str):
    document_id = None
    try:
        print(f"--- 🚀 Processing started for: {filename} ---")
        initial_doc = {
            "filename": filename,
            "status": "processing",
            "received_at": datetime.now(timezone.utc)
        }
        result = prescription_collection.insert_one(initial_doc)
        document_id = result.inserted_id

        # Step 1: Upload original image
        original_upload = cloudinary.uploader.upload(
            image_bytes,
            folder="original_prescriptions",
            resource_type="image"
        )
        original_image_url = original_upload.get("secure_url")
        original_public_id = original_upload.get("public_id")
        print("Step 1/5: Original image uploaded.")

        # Step 2: Preprocess image
        preprocessed_image_bytes = preprocess_text(image_bytes)
        print("Step 2/5: Image preprocessing complete.")

        # Step 3: Upload preprocessed image
        processed_upload = cloudinary.uploader.upload(
            preprocessed_image_bytes,
            folder="processed_prescriptions",
            resource_type="image"
        )
        processed_image_url = processed_upload.get("secure_url")
        processed_public_id = processed_upload.get("public_id")
        print("Step 3/5: Preprocessed image uploaded.")

        # Step 4: Get Gemini analysis
        print("Step 4/5: Calling Gemini API...")
        gemini_json_data = get_gemini_analysis_from_image(processed_image_url)
        print("Step 4/5: Gemini analysis complete.")

        if "error" in gemini_json_data:
            raise Exception(f"Gemini API Error: {gemini_json_data['error']}")

        gemini_json_data['scribePrescription'] = {
            "scribeId": "AI_SCRIBE_V1",
            "imageUrl": processed_image_url,
            "publicId": processed_public_id,
            "date": datetime.now(timezone.utc).isoformat()
        }

        # Step 5: Save to MongoDB
        update_data = {
            "$set": {
                "status": "completed",
                "processed_at": datetime.now(timezone.utc),
                "original_image": {
                    "url": original_image_url,
                    "public_id": original_public_id
                },
                "processed_image": {
                    "url": processed_image_url,
                    "public_id": processed_public_id
                },
                "analysis_data": gemini_json_data
            }
        }
        prescription_collection.update_one({"_id": document_id}, update_data)
        print("Step 5/5: ✅ Data successfully saved to MongoDB.")
        print(f"--- 🎉 Processing Finished for: {filename} ---")

    except Exception as e:
        print(f"❌ Error in background task: {e}")
        import traceback
        traceback.print_exc()
        if document_id:
            prescription_collection.update_one(
                {"_id": document_id},
                {"$set": {
                    "status": "failed",
                    "error_message": str(e)
                }}
            )