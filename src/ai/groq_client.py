"""
Groq client implementation.
Provides AI content generation using Groq's cloud API.
"""

from typing import Optional

from groq import Groq


class GroqClient:
    """
    Client for Groq API.

    Implements the BaseLLMClient protocol for compatibility with
    the HiringAIAssistant service.
    """

    def __init__(self, api_key: str, model: str, timeout: int = 10):
        """
        Initialize Groq client.

        Args:
            api_key: Groq API key (get from console.groq.com)
            model: Model name (e.g., "llama-3.2-3b-preview", "mixtral-8x7b-32768")
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model_name = model
        self.timeout = timeout
        self._client: Optional[Groq] = None

        # Initialize client
        try:
            self._client = Groq(api_key=self.api_key, timeout=self.timeout)
            # Test connection by listing models
            self._client.models.list()
        except Exception as e:
            print(f"⚠️  Failed to initialize Groq client: {e}")
            print("   Get your API key from: https://console.groq.com/keys")
            self._client = None

    def generate_content(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """
        Generate content using Groq API.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Generated text

        Raises:
            Exception: If content generation fails
        """
        if not self._client:
            raise Exception("Groq client not properly initialized")

        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {e}")

    def is_available(self) -> bool:
        """
        Check if Groq client is available.

        Returns:
            True if client is properly initialized with valid API key
        """
        if not self._client or not self.api_key:
            return False

        try:
            # Quick health check
            self._client.models.list()
            return True
        except Exception:
            return False
