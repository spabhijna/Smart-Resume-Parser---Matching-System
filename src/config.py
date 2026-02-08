"""
Configuration management for AI integration.
Loads settings from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class AIConfig:
    """Configuration for AI service integration."""

    api_key: str = os.getenv("GEMINI_API_KEY", "")
    model: str = os.getenv("AI_MODEL", "gemini-flash-latest")
    max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "2000"))
    temperature: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    timeout: int = 10  # seconds

    def is_enabled(self) -> bool:
        """Check if AI service is properly configured."""
        return bool(self.api_key and self.api_key != "your-api-key-here")

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.is_enabled():
            print("⚠️  AI service disabled: GEMINI_API_KEY not configured")
            print("   Set your API key in .env to enable AI features")
        else:
            print(f"✓ AI service enabled: {self.model}")
