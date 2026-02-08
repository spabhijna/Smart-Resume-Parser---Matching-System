"""
Base protocol for LLM client implementations.
Defines the interface that all AI providers must implement.
"""

from typing import Protocol


class BaseLLMClient(Protocol):
    """
    Protocol defining the interface for LLM clients.
    
    All AI provider implementations (Gemini, Ollama, etc.) must implement
    this interface to ensure compatibility with the HiringAIAssistant.
    """

    def generate_content(
        self, 
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """
        Generate content from the LLM based on a prompt.
        
        Args:
            prompt: The input prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0-1.0 for most models)
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If content generation fails
        """
        ...

    def is_available(self) -> bool:
        """
        Check if the LLM service is available and properly configured.
        
        For API-based services (Gemini): Check API key validity
        For local services (Ollama): Check endpoint reachability
        
        Returns:
            True if the service is available, False otherwise
        """
        ...
