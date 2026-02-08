"""
AI service for providing human-readable insights on candidate matching.
Supports both Google Gemini and Groq cloud LLM providers.
"""

import time
from typing import Optional

from src.ai.base_client import BaseLLMClient
from src.ai.gemini_client import GeminiClient
from src.ai.groq_client import GroqClient
from src.ai.prompts import (
    get_candidate_summary_prompt,
    get_feedback_analysis_prompt,
    get_match_explanation_prompt,
)
from src.config import AIConfig
from src.models.candidate import Candidate
from src.models.job import Job


class HiringAIAssistant:
    """
    AI assistant for hiring decisions.

    Supports multiple AI providers:
    - Google Gemini: Cloud-based API (requires API key)
    - Groq: Cloud-based API with generous free tier (requires API key)

    Philosophy:
    - AI explains, humans decide
    - Graceful degradation (system works without AI)
    - Non-authoritative insights
    """

    def __init__(self, config: Optional[AIConfig] = None):
        """Initialize AI assistant with configuration."""
        self.config = config or AIConfig()
        self.client: Optional[BaseLLMClient] = None
        self.enabled = False

        # Factory pattern: select client based on provider
        if self.config.is_enabled():
            try:
                if self.config.provider == "gemini":
                    self.client = GeminiClient(
                        api_key=self.config.api_key,
                        model=self.config.gemini_model,
                        timeout=self.config.timeout,
                    )
                elif self.config.provider == "groq":
                    self.client = GroqClient(
                        api_key=self.config.groq_api_key,
                        model=self.config.groq_model,
                        timeout=self.config.timeout,
                    )
                else:
                    print(f"⚠️  Unknown AI provider: {self.config.provider}")
                    self.client = None

                if self.client and self.client.is_available():
                    self.enabled = True
                else:
                    print(f"⚠️  {self.config.provider.title()} client not available")
                    self.enabled = False

            except Exception as e:
                print(f"⚠️  Failed to initialize AI service: {e}")
                self.enabled = False

    def _call_ai_with_retry(
        self, prompt: str, max_retries: int = 3, initial_delay: float = 1.0
    ) -> Optional[str]:
        """
        Call AI with exponential backoff retry logic.

        Works with any LLM provider (Gemini, Ollama, etc.)

        Args:
            prompt: The prompt to send to the AI
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry

        Returns:
            AI response text or None on failure
        """
        if not self.enabled or not self.client:
            return None

        delay = initial_delay
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.generate_content(
                    prompt=prompt,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
                return response

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff

        # All retries failed
        print(f"⚠️  AI call failed after {max_retries} attempts: {last_error}")
        return None

    def summarize_candidate(self, candidate: Candidate) -> Optional[str]:
        """
        Generate a professional summary of a candidate's profile.

        Use after parsing to provide human-readable insights.

        Args:
            candidate: Parsed candidate object

        Returns:
            Professional summary or None on failure
        """
        if not self.enabled:
            return None

        try:
            prompt = get_candidate_summary_prompt(candidate)
            summary = self._call_ai_with_retry(prompt)
            return summary
        except Exception as e:
            print(f"⚠️  Failed to generate summary for {candidate.name}: {e}")
            return None

    def explain_match(
        self,
        candidate: Candidate,
        job: Job,
        score: float,
        breakdown: dict,
        missing_hard: list = None,
        missing_soft: list = None,
    ) -> Optional[str]:
        """
        Generate human-readable explanation of why candidate received a score.

        Use after matching to help recruiters understand the reasoning.

        Args:
            candidate: Candidate object
            job: Job object
            score: Match score (0-1)
            breakdown: Score breakdown by component
            missing_hard: List of missing hard required skills
            missing_soft: List of missing soft required skills

        Returns:
            Match explanation or None on failure
        """
        if not self.enabled:
            return None

        try:
            prompt = get_match_explanation_prompt(
                candidate=candidate,
                job=job,
                score=score,
                breakdown=breakdown,
                missing_hard=missing_hard or [],
                missing_soft=missing_soft or [],
            )
            explanation = self._call_ai_with_retry(prompt)
            return explanation
        except Exception as e:
            print(f"⚠️  Failed to generate explanation for {candidate.name}: {e}")
            return None

    def suggest_refinements(self, feedback_batch: list) -> Optional[str]:
        """
        Analyze hiring feedback and suggest improvements to matching rules.

        Use after collecting recruiter feedback to learn patterns.

        Args:
            feedback_batch: List of feedback dicts with keys:
                - candidate_name: str
                - job_title: str
                - score: float
                - decision: str (e.g., "interviewed", "passed", "hired")
                - notes: str

        Returns:
            Refinement suggestions or None on failure
        """
        if not self.enabled:
            return None

        if not feedback_batch:
            return "No feedback provided for analysis."

        try:
            prompt = get_feedback_analysis_prompt(feedback_batch)
            suggestions = self._call_ai_with_retry(prompt)
            return suggestions
        except Exception as e:
            print(f"⚠️  Failed to analyze feedback: {e}")
            return None
