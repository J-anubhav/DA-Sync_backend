#!/usr/bin/env python3
"""Debug script to check if .env is loading correctly"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("🔍 DEBUGGING .env LOADING")
print("=" * 60)

# Check where script is running from
print(f"\n📍 Current working directory: {os.getcwd()}")
print(f"📍 Script location: {Path(__file__).parent.absolute()}")

# Check if .env exists
env_path = Path(__file__).parent / ".env"
print(f"\n🔎 Looking for .env at: {env_path}")
print(f"✅ .env exists: {env_path.exists()}")

if env_path.exists():
    print(f"📄 .env file size: {env_path.stat().st_size} bytes")
    with open(env_path, 'r') as f:
        content = f.read()
        print(f"📝 .env content:\n{content}\n")

# Load .env
print("\n⏳ Loading .env...")
load_dotenv(dotenv_path=env_path, override=True)

# Check all environment variables
print("\n🔑 Environment variables:")
print(f"   GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY', 'NOT FOUND')[:30]}...")
print(f"   CLOUDINARY_CLOUD_NAME: {os.getenv('CLOUDINARY_CLOUD_NAME', 'NOT FOUND')}")
print(f"   MONGO_URI: {os.getenv('MONGO_URI', 'NOT FOUND')}")

# Try importing config
print("\n⏳ Trying to import config...")
try:
    from config import settings
    print(f"✅ Config imported successfully")
    print(f"   settings.gemini_api_key: {settings.gemini_api_key[:30] if settings.gemini_api_key else 'EMPTY'}...")
    print(f"   settings.cloudinary_cloud_name: {settings.cloudinary_cloud_name}")
except Exception as e:
    print(f"❌ Error importing config: {e}")

# Try configuring Gemini
print("\n⏳ Trying to configure Gemini...")
try:
    import google.generativeai as genai
    gemini_key = os.getenv("GEMINI_API_KEY")
    print(f"   Gemini key from os.getenv: {gemini_key[:30] if gemini_key else 'NOT FOUND'}...")
    
    if gemini_key:
        genai.configure(api_key=gemini_key)
        print(f"✅ Gemini configured successfully!")
    else:
        print(f"❌ Gemini key is empty or not found!")
except Exception as e:
    print(f"❌ Error configuring Gemini: {e}")

print("\n" + "=" * 60)