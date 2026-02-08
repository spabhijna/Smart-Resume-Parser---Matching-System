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

    # Provider selection: "gemini" or "groq" (both cloud APIs)
    provider: str = os.getenv("AI_PROVIDER", "gemini")

    # Google Gemini configuration
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    # Groq configuration
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.2-3b-preview")

    # Shared configuration
    max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "2000"))
    temperature: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    timeout: int = 10  # seconds

    @property
    def model(self) -> str:
        """Get the model name for the current provider."""
        if self.provider == "gemini":
            return self.gemini_model
        elif self.provider == "groq":
            return self.groq_model
        return self.gemini_model

    def is_enabled(self) -> bool:
        """Check if AI service is properly configured."""
        if self.provider == "gemini":
            return bool(self.api_key and self.api_key != "your-api-key-here")
        elif self.provider == "groq":
            return bool(self.groq_api_key and self.groq_api_key != "your-api-key-here")
        return False

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.provider not in ["gemini", "groq"]:
            print(f"⚠️  Invalid AI provider '{self.provider}', defaulting to 'gemini'")
            object.__setattr__(self, "provider", "gemini")

        if not self.is_enabled():
            if self.provider == "gemini":
                print("⚠️  AI service disabled: GEMINI_API_KEY not configured")
                print("   Set your API key in .env to enable AI features")
            elif self.provider == "groq":
                print("⚠️  AI service disabled: GROQ_API_KEY not configured")
                print("   Set your API key in .env to enable AI features")
                print("   Get your API key from: https://console.groq.com/keys")
            else:
                print("⚠️  AI service disabled: Invalid configuration")
        else:
            print(f"✓ AI service enabled: {self.provider} ({self.model})")
