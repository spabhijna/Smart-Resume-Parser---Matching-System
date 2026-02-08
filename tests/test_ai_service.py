"""
Tests for AI service integration.
Uses mocking to avoid actual API calls during testing.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.ai.ai_service import HiringAIAssistant
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
        ai_summary=None
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
        role_type="IC_SENIOR"
    )


@pytest.fixture
def mock_ai_config():
    """Create a mock AI config with enabled status."""
    config = AIConfig()
    config.api_key = "test-api-key"
    config.model = "gemini-1.5-flash"
    return config


@pytest.fixture
def mock_genai_response():
    """Create a mock response from Gemini API."""
    mock_response = MagicMock()
    mock_response.text = "This is a mock AI response."
    return mock_response


class TestHiringAIAssistant:
    """Test suite for HiringAIAssistant class."""

    @patch('src.ai.ai_service.genai')
    def test_initialization_with_valid_config(self, mock_genai, mock_ai_config):
        """Test that AI assistant initializes correctly with valid config."""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()
        
        assistant = HiringAIAssistant(config=mock_ai_config)
        
        assert assistant.enabled is True
        mock_genai.configure.assert_called_once()

    @patch('src.ai.ai_service.genai')
    def test_initialization_with_invalid_config(self, mock_genai):
        """Test that AI assistant gracefully handles missing API key."""
        config = AIConfig()
        config.api_key = ""
        
        assistant = HiringAIAssistant(config=config)
        
        assert assistant.enabled is False

    @patch('src.ai.ai_service.genai')
    def test_summarize_candidate_success(self, mock_genai, mock_ai_config, test_candidate, mock_genai_response):
        """Test successful candidate summarization."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_genai_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()
        
        assistant = HiringAIAssistant(config=mock_ai_config)
        summary = assistant.summarize_candidate(test_candidate)
        
        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0
        mock_model.generate_content.assert_called_once()

    @patch('src.ai.ai_service.genai')
    def test_summarize_candidate_when_disabled(self, mock_genai, test_candidate):
        """Test that summarization returns None when AI is disabled."""
        config = AIConfig()
        config.api_key = ""
        
        assistant = HiringAIAssistant(config=config)
        summary = assistant.summarize_candidate(test_candidate)
        
        assert summary is None

    @patch('src.ai.ai_service.genai')
    def test_explain_match_success(
        self, 
        mock_genai, 
        mock_ai_config, 
        test_candidate, 
        test_job,
        mock_genai_response
    ):
        """Test successful match explanation generation."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_genai_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()
        
        assistant = HiringAIAssistant(config=mock_ai_config)
        
        explanation = assistant.explain_match(
            candidate=test_candidate,
            job=test_job,
            score=0.75,
            breakdown={"required_skills": 0.8, "experience": 0.7},
            missing_hard=[],
            missing_soft=["tensorflow"]
        )
        
        assert explanation is not None
        assert isinstance(explanation, str)
        mock_model.generate_content.assert_called_once()

    @patch('src.ai.ai_service.genai')
    def test_explain_match_when_disabled(self, mock_genai, test_candidate, test_job):
        """Test that match explanation returns None when AI is disabled."""
        config = AIConfig()
        config.api_key = ""
        
        assistant = HiringAIAssistant(config=config)
        
        explanation = assistant.explain_match(
            candidate=test_candidate,
            job=test_job,
            score=0.75,
            breakdown={"required_skills": 0.8},
            missing_hard=[],
            missing_soft=[]
        )
        
        assert explanation is None

    @patch('src.ai.ai_service.genai')
    def test_suggest_refinements_success(self, mock_genai, mock_ai_config, mock_genai_response):
        """Test successful feedback analysis and refinement suggestions."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_genai_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()
        
        assistant = HiringAIAssistant(config=mock_ai_config)
        
        feedback = [
            {
                "candidate_name": "Test Candidate",
                "job_title": "ML Engineer",
                "score": 0.75,
                "decision": "interviewed",
                "notes": "Strong systems thinker"
            }
        ]
        
        suggestions = assistant.suggest_refinements(feedback)
        
        assert suggestions is not None
        assert isinstance(suggestions, str)
        mock_model.generate_content.assert_called_once()

    @patch('src.ai.ai_service.genai')
    def test_suggest_refinements_empty_feedback(self, mock_genai, mock_ai_config):
        """Test that empty feedback returns appropriate message."""
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock()
        
        assistant = HiringAIAssistant(config=mock_ai_config)
        suggestions = assistant.suggest_refinements([])
        
        assert suggestions == "No feedback provided for analysis."

    @patch('src.ai.ai_service.genai')
    def test_api_error_graceful_degradation(self, mock_genai, mock_ai_config, test_candidate):
        """Test that API errors are handled gracefully without crashing."""
        # Setup mock to raise exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()
        
        assistant = HiringAIAssistant(config=mock_ai_config)
        summary = assistant.summarize_candidate(test_candidate)
        
        # Should return None instead of crashing
        assert summary is None

    @patch('src.ai.ai_service.genai')
    @patch('src.ai.ai_service.time.sleep')  # Mock sleep to speed up tests
    def test_retry_logic_on_failure(self, mock_sleep, mock_genai, mock_ai_config, test_candidate):
        """Test that retry logic attempts multiple times before giving up."""
        # Setup mock to fail twice then succeed
        mock_response = MagicMock()
        mock_response.text = "Success after retries"
        
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = [
            Exception("Fail 1"),
            Exception("Fail 2"),
            mock_response
        ]
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        mock_genai.types.GenerationConfig = MagicMock()
        
        assistant = HiringAIAssistant(config=mock_ai_config)
        summary = assistant.summarize_candidate(test_candidate)
        
        assert summary == "Success after retries"
        assert mock_model.generate_content.call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep between retries


class TestAIConfig:
    """Test suite for AIConfig class."""

    def test_is_enabled_with_valid_key(self):
        """Test that config is enabled with valid API key."""
        config = AIConfig()
        config.api_key = "valid-test-key"
        
        assert config.is_enabled() is True

    def test_is_enabled_with_empty_key(self):
        """Test that config is disabled with empty API key."""
        config = AIConfig()
        config.api_key = ""
        
        assert config.is_enabled() is False

    def test_is_enabled_with_placeholder_key(self):
        """Test that config is disabled with placeholder API key."""
        config = AIConfig()
        config.api_key = "your-api-key-here"
        
        assert config.is_enabled() is False

    def test_default_values(self):
        """Test that config has sensible default values."""
        config = AIConfig()
        
        assert config.model == "gemini-1.5-flash"
        assert config.max_tokens == 2000
        assert config.temperature == 0.7
        assert config.timeout == 10
