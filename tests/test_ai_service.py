"""Tests for AI service integration.

Uses mocking to avoid actual API calls during testing.
Tests both Gemini and Groq providers.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.ai.ai_service import HiringAIAssistant
from src.ai.gemini_client import GeminiClient
from src.ai.groq_client import GroqClient
from src.config import AIConfig
from src.models.candidate import Candidate
from src.models.job import Job


@pytest.fixture
def test_candidate():
    """Create a test candidate for AI testing."""
    return Candidate(
        name="Test Candidate",
        email="test@example.com",
        phone="1234567890",
        skills=["python", "machine learning", "pytorch"],
        education=[{"degree": "MSC", "raw": "Master of Science", "year": "2020"}],
        experience=5,
        resume_link="test_resume.txt",
        ai_summary=None,
    )


@pytest.fixture
def test_job():
    """Create a test job for AI testing."""
    return Job(
        title="ML Engineer",
        company="Test Corp",
        location="Remote",
        description="Machine learning position",
        hard_required_skills=["python"],
        soft_required_skills=["pytorch", "tensorflow"],
        preferred_skills=["docker"],
        min_experience=3,
        role_type="IC_SENIOR",
    )


@pytest.fixture
def mock_ai_config_gemini():
    """Create a mock AI config for Gemini provider."""
    config = AIConfig()
    config.provider = "gemini"
    config.api_key = "test-api-key"
    config.gemini_model = "gemini-flash-latest"
    return config


@pytest.fixture
def mock_ai_config_groq():
    """Create a mock AI config for Groq provider."""
    config = AIConfig()
    config.provider = "groq"
    config.groq_api_key = "test-groq-api-key"
    config.groq_model = "llama-3.2-3b-preview"
    return config


@pytest.fixture
def mock_genai_response():
    """Create a mock response from Gemini API."""
    mock_response = MagicMock()
    mock_response.text = "This is a mock AI response."
    return mock_response


class TestHiringAIAssistant:
    """Test suite for HiringAIAssistant class."""

    @patch("src.ai.gemini_client.genai")
    def test_initialization_with_gemini(self, mock_genai, mock_ai_config_gemini):
        """Test that AI assistant initializes correctly with Gemini provider."""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock(return_value=MagicMock())

        assistant = HiringAIAssistant(config=mock_ai_config_gemini)

        assert assistant.enabled is True
        assert isinstance(assistant.client, GeminiClient)
        mock_genai.configure.assert_called_once()

    @patch("src.ai.groq_client.Groq")
    def test_initialization_with_groq(self, mock_groq_class, mock_ai_config_groq):
        """Test that AI assistant initializes correctly with Groq provider."""
        # Mock Groq client instance
        mock_groq_instance = MagicMock()
        mock_groq_instance.models.list.return_value = []
        mock_groq_class.return_value = mock_groq_instance

        assistant = HiringAIAssistant(config=mock_ai_config_groq)

        assert assistant.enabled is True
        assert isinstance(assistant.client, GroqClient)
        mock_groq_class.assert_called_once()

    def test_initialization_with_invalid_config(self):
        """Test that AI assistant gracefully handles missing API key for Gemini."""
        config = AIConfig()
        config.provider = "gemini"
        config.api_key = ""

        assistant = HiringAIAssistant(config=config)

        assert assistant.enabled is False

    @patch("src.ai.gemini_client.genai")
    def test_summarize_candidate_success_gemini(
        self, mock_genai, mock_ai_config_gemini, test_candidate, mock_genai_response
    ):
        """Test successful candidate summarization with Gemini."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_genai_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()

        assistant = HiringAIAssistant(config=mock_ai_config_gemini)
        summary = assistant.summarize_candidate(test_candidate)

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0
        mock_model.generate_content.assert_called_once()

    @patch("src.ai.groq_client.Groq")
    def test_summarize_candidate_success_groq(
        self, mock_groq_class, mock_ai_config_groq, test_candidate
    ):
        """Test successful candidate summarization with Groq."""
        # Mock Groq client and response
        mock_groq_instance = MagicMock()
        mock_groq_instance.models.list.return_value = []

        # Mock chat completion response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "This is a Groq response."
        mock_groq_instance.chat.completions.create.return_value = mock_completion

        mock_groq_class.return_value = mock_groq_instance

        assistant = HiringAIAssistant(config=mock_ai_config_groq)
        summary = assistant.summarize_candidate(test_candidate)

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0
        mock_groq_instance.chat.completions.create.assert_called_once()

    def test_summarize_candidate_when_disabled(self, test_candidate):
        """Test that summarization returns None when AI is disabled."""
        config = AIConfig()
        config.provider = "gemini"
        config.api_key = ""

        assistant = HiringAIAssistant(config=config)
        summary = assistant.summarize_candidate(test_candidate)

        assert summary is None

    @patch("src.ai.gemini_client.genai")
    def test_explain_match_success(
        self,
        mock_genai,
        mock_ai_config_gemini,
        test_candidate,
        test_job,
        mock_genai_response,
    ):
        """Test successful match explanation generation."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_genai_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()

        assistant = HiringAIAssistant(config=mock_ai_config_gemini)

        explanation = assistant.explain_match(
            candidate=test_candidate,
            job=test_job,
            score=0.75,
            breakdown={"required_skills": 0.8, "experience": 0.7},
            missing_hard=[],
            missing_soft=["tensorflow"],
        )

        assert explanation is not None
        assert isinstance(explanation, str)
        mock_model.generate_content.assert_called_once()

    def test_explain_match_when_disabled(self, test_candidate, test_job):
        """Test that match explanation returns None when AI is disabled."""
        config = AIConfig()
        config.provider = "gemini"
        config.api_key = ""

        assistant = HiringAIAssistant(config=config)

        explanation = assistant.explain_match(
            candidate=test_candidate,
            job=test_job,
            score=0.75,
            breakdown={"required_skills": 0.8},
            missing_hard=[],
            missing_soft=[],
        )

        assert explanation is None

    @patch("src.ai.gemini_client.genai")
    def test_suggest_refinements_success(
        self, mock_genai, mock_ai_config_gemini, mock_genai_response
    ):
        """Test successful feedback analysis and refinement suggestions."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_genai_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()

        assistant = HiringAIAssistant(config=mock_ai_config_gemini)

        feedback = [
            {
                "candidate_name": "Test Candidate",
                "job_title": "ML Engineer",
                "score": 0.75,
                "decision": "interviewed",
                "notes": "Strong systems thinker",
            }
        ]

        suggestions = assistant.suggest_refinements(feedback)

        assert suggestions is not None
        assert isinstance(suggestions, str)
        mock_model.generate_content.assert_called_once()

    @patch("src.ai.gemini_client.genai")
    def test_suggest_refinements_empty_feedback(
        self, mock_genai, mock_ai_config_gemini
    ):
        """Test that empty feedback returns appropriate message."""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock(return_value=MagicMock())

        assistant = HiringAIAssistant(config=mock_ai_config_gemini)
        suggestions = assistant.suggest_refinements([])

        assert suggestions == "No feedback provided for analysis."

    @patch("src.ai.gemini_client.genai")
    def test_api_error_graceful_degradation(
        self, mock_genai, mock_ai_config_gemini, test_candidate
    ):
        """Test that API errors are handled gracefully without crashing."""
        # Setup mock to raise exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()

        assistant = HiringAIAssistant(config=mock_ai_config_gemini)
        summary = assistant.summarize_candidate(test_candidate)

        # Should return None instead of crashing
        assert summary is None

    @patch("src.ai.gemini_client.genai")
    @patch("src.ai.ai_service.time.sleep")  # Mock sleep to speed up tests
    def test_retry_logic_on_failure(
        self, mock_sleep, mock_genai, mock_ai_config_gemini, test_candidate
    ):
        """Test that retry logic attempts multiple times before giving up."""
        # Setup mock to fail twice then succeed
        mock_model = MagicMock()

        # Create a response object with .text attribute
        mock_response = MagicMock()
        mock_response.text = "Success after retries"

        mock_model.generate_content.side_effect = [
            Exception("Fail 1"),
            Exception("Fail 2"),
            mock_response,  # Return response object, not string
        ]
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()

        assistant = HiringAIAssistant(config=mock_ai_config_gemini)
        summary = assistant.summarize_candidate(test_candidate)

        assert summary == "Success after retries"
        assert mock_model.generate_content.call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep between retries


class TestAIConfig:
    """Test suite for AIConfig class."""

    def test_is_enabled_gemini_with_valid_key(self):
        """Test that Gemini config is enabled with valid API key."""
        config = AIConfig()
        config.provider = "gemini"
        config.api_key = "valid-test-key"

        assert config.is_enabled() is True

    def test_is_enabled_gemini_with_empty_key(self):
        """Test that Gemini config is disabled with empty API key."""
        config = AIConfig()
        config.provider = "gemini"
        config.api_key = ""

        assert config.is_enabled() is False

    def test_is_enabled_gemini_with_placeholder_key(self):
        """Test that Gemini config is disabled with placeholder API key."""
        config = AIConfig()
        config.provider = "gemini"
        config.api_key = "your-api-key-here"

        assert config.is_enabled() is False

    def test_is_enabled_ollama(self):
        """Test that Groq config validates API key."""
        config = AIConfig()
        config.provider = "groq"
        config.groq_api_key = "test-key"

        assert config.is_enabled() is True

    def test_is_enabled_groq_with_empty_key(self):
        """Test that Groq config is disabled with empty API key."""
        config = AIConfig()
        config.provider = "groq"
        config.groq_api_key = ""

        assert config.is_enabled() is False

    def test_default_provider(self):
        """Test that default provider is gemini."""
        config = AIConfig()

        assert config.provider == "gemini"

    def test_model_property_gemini(self):
        """Test that model property returns gemini_model when provider is gemini."""
        config = AIConfig()
        config.provider = "gemini"
        config.gemini_model = "gemini-flash-latest"

        assert config.model == "gemini-flash-latest"

    def test_model_property_groq(self):
        """Test that model property returns groq_model when provider is groq."""
        config = AIConfig()
        config.provider = "groq"
        config.groq_model = "llama-3.2-3b-preview"

        assert config.model == "llama-3.2-3b-preview"

    def test_default_values(self):
        """Test that config has sensible default values."""
        config = AIConfig()

        assert config.max_tokens == 2000
        assert config.temperature == 0.7
        assert config.timeout == 10
