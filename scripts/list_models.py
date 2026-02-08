"""#!/usr/bin/env python3List available Gemini models to find the correct model name."""

import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Gemini models:\n")

try:
    for model in genai.list_models():
        if "generateContent" in model.supported_generation_methods:
            print(f"✓ {model.name}")
            print(f"  Display name: {model.display_name}")
            print(f"  Description: {model.description[:100]}...")
            print()
except Exception as e:
    print(f"Error listing models: {e}")
