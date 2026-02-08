"""
Google Gemini client implementation.
Provides AI content generation using Google's Gemini API.
"""

from typing import Optional

import google.generativeai as genai


class GeminiClient:
    """
    Client for Google Gemini API.

    Implements the BaseLLMClient protocol for compatibility with
    the HiringAIAssistant service.
    """

    def __init__(self, api_key: str, model: str, timeout: int = 10):
        """
        Initialize Gemini client.

        Args:
            api_key: Google AI API key
            model: Model name (e.g., "gemini-flash-latest", "gemini-2.5-flash")
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model_name = model
        self.timeout = timeout
        self._model: Optional[genai.GenerativeModel] = None

        # Configure and initialize
        try:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            print(f"⚠️  Failed to initialize Gemini client: {e}")
            self._model = None

    def generate_content(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """
        Generate content using Gemini API.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Generated text

        Raises:
            Exception: If content generation fails
        """
        if not self._model:
            raise Exception("Gemini client not properly initialized")

        response = self._model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        return response.text

    def is_available(self) -> bool:
        """
        Check if Gemini client is available.

        Returns:
            True if client is properly initialized with valid API key
        """
        return self._model is not None and bool(self.api_key)
