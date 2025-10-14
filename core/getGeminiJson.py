import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))

# Load .env
env_file = parent_dir / ".env"
load_dotenv(dotenv_path=env_file, override=True)

import google.generativeai as genai
import json
import requests
from PIL import Image
import io

from config import settings

# Get API key
api_key = os.getenv("GEMINI_API_KEY") or settings.gemini_api_key

print(f"🔑 Gemini API Key available: {bool(api_key)}")
if not api_key:
    print("❌ WARNING: GEMINI_API_KEY not found!")
else:
    print(f"✅ API Key found: {api_key[:20]}...")

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    print("✅ Gemini API configured successfully.")
except Exception as e:
    print(f"❌ Error configuring Gemini: {e}")

def get_gemini_prompt() -> str:
    """Returns the standardized system prompt for the Gemini vision model."""
    prompt = """
    #*SYSTEM PERSONA AND MISSION*
    You are an expert AI medical scriber. Your sole mission is to transcribe medical prescription images into a structured JSON format with 100% accuracy. PATIENT SAFETY IS THE ABSOLUTE PRIORITY. Be systematic, precise, and transparent about any uncertainty.
    
    #*PROCESSING PROTOCOL*
    1.  **Analyze the Entire Image**: Before extracting, understand the layout, handwriting style, and context.
    2.  **Field-by-Field Extraction**: Go through each field in the JSON structure below and find the corresponding information in the image.
    3.  **Handle Missing Information**: If a field is not present in the image, leave its value as an empty string `""` or an empty list `[]`. DO NOT HALLUCINATE OR GUESS.
    4.  **Handle Illegible Text**: If text for a field is present but you cannot read it with high confidence, use the format `"[ILLEGIBLE: description of location/context]"`. Example: `"[ILLEGIBLE: Doctor's signature]"`.
    5.  **Date/Time Formatting**: Standardize dates to `YYYY-MM-DD` and time to `HH:MM:SS` (24-hour format) if possible.
    6.  **Medication Parsing**: For each medication, create a separate object in the `medication` array with dose, dosage form, route, frequency, duration, and timing.
    
    JSON OUTPUT STRUCTURE
    {
    "name": "", "date": "", "time": "", "doctorUsername": "", "patientUsername": "", "hospitalName": "", "hospitalId": "", "clinicalNote": "", "diagnosis": [], "complaints": [], "notes": [], "medication": [{"name": "", "medicationDetails": [{"dose": "", "dosage": "", "route": "", "freq": "", "dur": "", "class": "", "when": ""}]}], "test": [{"name": "", "instruction": "", "date": ""}], "followup": {"date": "", "reason": ""}, "vitals": {"BP": "", "Heartrate": "", "RespiratoryRate": "", "temp": "", "spO2": "", "weight": "", "height": "", "BMI": "", "waist_hips": ""}, "nursing": [{"instruction": "", "priority": ""}], "discharge": {"planned_date": "", "instruction": "", "Home_Care": "", "Recommendations": ""}, "icdCode": [], "medicalHistory": [], "labScanPdf": [], "systematicExamination": {"General": [], "CVS": [], "RS": [], "CNS": [], "PA": [], "ENT": []}, "assessmentPlan": "", "nutritionAssessment": [], "referredTo": {"doctorName": "", "doctorUsername": "", "phoneNumber": "", "email": "", "hospitalId": "", "hospitalName": "", "speciality": ""}, "scribePrescription": {"scribeId": "", "imageUrl": "", "publicId": "", "date": ""}
    }
    """
    return prompt

def get_gemini_analysis_from_image(image_url: str) -> dict:
    """Takes an image URL, processes it with Gemini Vision, and returns structured JSON data."""
    try:
        print(f"🤖 Creating Gemini model...")
        model = genai.GenerativeModel(
            'gemini-2.0-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        
        print(f"📥 Downloading image from: {image_url}")
        response = requests.get(image_url)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        print(f"✅ Image loaded successfully")
        
        prompt = get_gemini_prompt()
        
        print("📤 Sending to Gemini API...")
        response = model.generate_content([prompt, img])
        
        print("✅ Gemini analysis complete.")
        result = json.loads(response.text)
        return result

    except Exception as e:
        print(f"❌ Error processing image with Gemini: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "url": image_url}