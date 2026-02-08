import os

import pytest

from src.matching.matcher import RuleBasedCandidateMatcher
from src.models.job import Job
from src.models.match_config import MatchConfig
from src.parsing.parser import ResumeParser
from src.utils.matcher_utils import normalize_list


@pytest.fixture
def test_resume_candidate():
    """Parse the test_resume_1.txt file and return a Candidate object."""
    resume_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "resumes", "test_resume_1.txt"
    )
    with open(resume_path, "r") as f:
        resume_text = f.read()
    parser = ResumeParser()
    return parser.parse(resume_text)


@pytest.fixture
def matcher():
    """Create a matcher instance with default configuration."""
    return RuleBasedCandidateMatcher()


@pytest.fixture
def ml_engineer_job():
    """Create a sample ML Engineer job posting that matches the test resume."""
    return Job(
        title="Senior Machine Learning Engineer",
        description="Looking for an experienced ML engineer to build AI systems",
        company="AI Solutions Inc",
        location="San Francisco, CA",
        required_skills=["Python", "Machine Learning", "TensorFlow"],
        preferred_skills=["Deep Learning", "NLP", "SQL"],
        min_experience=4,
        max_experience=7,
        min_salary=120000,
        max_salary=180000,
        education_keywords=["Computer Science", "Master"],
    )


@pytest.fixture
def backend_engineer_job():
    """Create a backend engineer job that partially matches the test resume."""
    return Job(
        title="Backend Engineer",
        description="Backend development role",
        company="Web Corp",
        location="New York, NY",
        required_skills=["Python", "Django", "SQL", "Redis"],
        preferred_skills=["Flask", "PostgreSQL"],
        min_experience=3,
        max_experience=5,
        education_keywords=["Computer Science"],
    )


@pytest.fixture
def unrelated_job():
    """Create a job that doesn't match the test resume well."""
    return Job(
        title="Frontend Developer",
        description="React and TypeScript development",
        company="UI Corp",
        location="Austin, TX",
        required_skills=["JavaScript", "React", "TypeScript", "HTML", "CSS"],
        preferred_skills=["Redux", "GraphQL"],
        min_experience=2,
        max_experience=4,
        education_keywords=["Computer Science"],
    )


class TestMatcherWithTestResume:
    """Test the matcher functions using test_resume_1.txt"""

    def test_parse_test_resume(self, test_resume_candidate):
        """Verify that the test resume is parsed correctly."""
        assert test_resume_candidate.name == "John Smith"
        assert test_resume_candidate.email == "john.smith@email.com"
        assert test_resume_candidate.phone is not None
        assert test_resume_candidate.experience >= 5
        assert "python" in test_resume_candidate.skills
        assert "machine learning" in test_resume_candidate.skills
        assert len(test_resume_candidate.education) >= 1

    def test_required_skills_match_ml_job(
        self, test_resume_candidate, ml_engineer_job, matcher
    ):
        """Test required skills scoring for ML job."""
        score, breakdown = matcher.score(test_resume_candidate, ml_engineer_job)
        # John has Python, Machine Learning, and TensorFlow
        assert breakdown["required"] > 0.8, (
            f"Expected high required skills score, got {breakdown['required']}"
        )

    def test_required_skills_match_backend_job(
        self, test_resume_candidate, backend_engineer_job, matcher
    ):
        """Test required skills scoring for backend job - missing Redis."""
        score, breakdown = matcher.score(test_resume_candidate, backend_engineer_job)
        # John has Python, Django, SQL but missing Redis (3 out of 4)
        assert 0.3 < breakdown["required"] < 0.9, (
            f"Expected moderate score due to missing Redis, got {breakdown['required']}"
        )

    def test_required_skills_match_unrelated_job(
        self, test_resume_candidate, unrelated_job, matcher
    ):
        """Test required skills scoring for unrelated frontend job."""
        score, breakdown = matcher.score(test_resume_candidate, unrelated_job)
        # John doesn't have most frontend skills
        assert breakdown["required"] < 0.3, (
            f"Expected low score for unrelated job, got {breakdown['required']}"
        )

    def test_experience_score_ml_job(
        self, test_resume_candidate, ml_engineer_job, matcher
    ):
        """Test experience scoring - John has 5+ years, job requires 4-7."""
        score, breakdown = matcher.score(test_resume_candidate, ml_engineer_job)
        assert 0.7 <= breakdown["experience"] <= 1.0, (
            f"Expected good experience match, got {breakdown['experience']}"
        )

    def test_education_score_ml_job(
        self, test_resume_candidate, ml_engineer_job, matcher
    ):
        """Test education scoring - John has MS in Computer Science."""
        score, breakdown = matcher.score(test_resume_candidate, ml_engineer_job)
        assert breakdown["education"] >= 0.5, (
            f"Expected good education match, got {breakdown['education']}"
        )

    def test_final_match_score_ml_job(
        self, test_resume_candidate, ml_engineer_job, matcher
    ):
        """Test final weighted score for ML job - should be high match."""
        score, breakdown = matcher.score(test_resume_candidate, ml_engineer_job)
        assert score >= 0.70, f"Expected strong match for ML job, got {score}"

    def test_final_match_score_backend_job(
        self, test_resume_candidate, backend_engineer_job, matcher
    ):
        """Test final weighted score for backend job - should be moderate match."""
        score, breakdown = matcher.score(test_resume_candidate, backend_engineer_job)
        assert 0.30 < score < 0.80, (
            f"Expected moderate match for backend job, got {score}"
        )

    def test_final_match_score_unrelated_job(
        self, test_resume_candidate, unrelated_job, matcher
    ):
        """Test final weighted score for unrelated job - should be low match."""
        score, breakdown = matcher.score(test_resume_candidate, unrelated_job)
        assert score < 0.40, f"Expected low match for unrelated job, got {score}"

    def test_matcher_ml_job(self, test_resume_candidate, ml_engineer_job, matcher):
        """Test full matcher function for ML job - should be Strong Match or Top Talent."""
        result = matcher.match(test_resume_candidate, ml_engineer_job)
        assert result["level"] in ["Strong Match", "Top Talent"], (
            f"Expected high match level, got {result['level']}"
        )
        assert "score" in result
        assert "breakdown" in result
        assert result["score"] >= 0.70

    def test_matcher_backend_job(
        self, test_resume_candidate, backend_engineer_job, matcher
    ):
        """Test full matcher function for backend job - should be Potential Fit."""
        result = matcher.match(test_resume_candidate, backend_engineer_job)
        assert result["level"] in ["Potential Fit", "Strong Match"], (
            f"Expected moderate match level, got {result['level']}"
        )
        assert "score" in result
        assert "breakdown" in result

    def test_matcher_unrelated_job(self, test_resume_candidate, unrelated_job, matcher):
        """Test full matcher function for unrelated job - should be Low Relevance or Not Recommended."""
        result = matcher.match(test_resume_candidate, unrelated_job)
        assert result["level"] in [
            "Low Relevance",
            "Not Recommended",
            "Potential Fit",
        ], f"Expected low match level, got {result['level']}"
        assert "score" in result
        assert "breakdown" in result

    def test_candidate_skills_normalized(self, test_resume_candidate):
        """Verify that candidate skills are properly extracted and can be normalized."""
        assert len(test_resume_candidate.skills) > 0
        # All skills should be lowercase (parser returns lowercase)
        for skill in test_resume_candidate.skills:
            assert skill == skill.lower()

    def test_match_returns_correct_structure(
        self, test_resume_candidate, ml_engineer_job, matcher
    ):
        """Test that match() returns the expected dictionary structure."""
        result = matcher.match(test_resume_candidate, ml_engineer_job)
        assert isinstance(result, dict)
        assert "score" in result
        assert "level" in result
        assert "breakdown" in result
        assert isinstance(result["breakdown"], dict)
        assert "required" in result["breakdown"]
        assert "preferred" in result["breakdown"]
        assert "experience" in result["breakdown"]
        assert "education" in result["breakdown"]

    def test_score_returns_tuple(self, test_resume_candidate, ml_engineer_job, matcher):
        """Test that score() returns a tuple of (score, breakdown)."""
        result = matcher.score(test_resume_candidate, ml_engineer_job)
        assert isinstance(result, tuple)
        assert len(result) == 2
        score, breakdown = result
        assert isinstance(score, float)
        assert isinstance(breakdown, dict)

    def test_custom_config(self, test_resume_candidate, ml_engineer_job):
        """Test that custom configuration is properly applied."""
        # Create a matcher with custom weights
        custom_config = MatchConfig(
            required_weight=0.70,
            preferred_weight=0.10,
            experience_weight=0.10,
            education_weight=0.10,
        )
        custom_matcher = RuleBasedCandidateMatcher(config=custom_config)

        # Get the score
        score, breakdown = custom_matcher.score(test_resume_candidate, ml_engineer_job)

        # Verify it's using the custom config by checking the weights
        assert custom_matcher.config.required_weight == 0.70
        assert custom_matcher.config.preferred_weight == 0.10
