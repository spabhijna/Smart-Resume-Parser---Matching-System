"""#!/usr/bin/env python3Quick test to verify AI service can connect to Google Gemini API.
Run this to test your API key and model configuration.
"""

from src.ai.ai_service import HiringAIAssistant
from src.models.candidate import Candidate

# Create test candidate
test_candidate = Candidate(
    name="Test User",
    email="test@example.com",
    phone="1234567890",
    skills=["python", "machine learning", "aws"],
    education=[{"degree": "BSC", "raw": "Bachelor of Science", "year": "2020"}],
    experience=3,
    resume_link="test.txt",
)

# Initialize AI assistant
print("Initializing AI assistant...")
ai_assistant = HiringAIAssistant()

if not ai_assistant.enabled:
    print("❌ AI service is not enabled. Check your GEMINI_API_KEY in .env")
    exit(1)

print(f"✓ AI service enabled with model: {ai_assistant.config.model}\n")

# Test candidate summarization
print("Testing candidate summarization...")
try:
    summary = ai_assistant.summarize_candidate(test_candidate)
    if summary:
        print(f"✓ Success! AI Summary:\n{summary}\n")
    else:
        print("❌ AI returned empty summary\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

print("Test complete!")
