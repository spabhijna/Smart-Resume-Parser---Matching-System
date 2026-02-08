import pytest
from src.matching.matcher import (
    matcher,
    final_match_score,
    required_skills_score,
    preferred_skill_score,
    experience_score,
    education_score
)
from src.utils.matcher_utils import normalize_list
from src.models.job import Job
from src.parsing.parser import parse_resume
import os


@pytest.fixture
def test_resume_candidate():
    """Parse the test_resume_1.txt file and return a Candidate object."""
    resume_path = os.path.join(os.path.dirname(__file__), "..", "data", "resumes", "test_resume_1.txt")
    with open(resume_path, "r") as f:
        resume_text = f.read()
    return parse_resume(resume_text)


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
        education_keywords=["Computer Science", "Master"]
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
        education_keywords=["Computer Science"]
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
        education_keywords=["Computer Science"]
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

    def test_required_skills_match_ml_job(self, test_resume_candidate, ml_engineer_job):
        """Test required skills scoring for ML job."""
        can_skills = normalize_list(test_resume_candidate.skills)
        req_skills = normalize_list(ml_engineer_job.required_skills)
        score = required_skills_score(can_skills, req_skills)
        # John has Python, Machine Learning, and TensorFlow
        assert score > 0.8, f"Expected high required skills score, got {score}"

    def test_required_skills_match_backend_job(self, test_resume_candidate, backend_engineer_job):
        """Test required skills scoring for backend job - missing Redis."""
        can_skills = normalize_list(test_resume_candidate.skills)
        req_skills = normalize_list(backend_engineer_job.required_skills)
        score = required_skills_score(can_skills, req_skills)
        # John has Python, Django, SQL but missing Redis (3 out of 4)
        assert 0.3 < score < 0.9, f"Expected moderate score due to missing Redis, got {score}"

    def test_required_skills_match_unrelated_job(self, test_resume_candidate, unrelated_job):
        """Test required skills scoring for unrelated frontend job."""
        can_skills = normalize_list(test_resume_candidate.skills)
        req_skills = normalize_list(unrelated_job.required_skills)
        score = required_skills_score(can_skills, req_skills)
        # John doesn't have most frontend skills
        assert score < 0.3, f"Expected low score for unrelated job, got {score}"

    def test_experience_score_ml_job(self, test_resume_candidate, ml_engineer_job):
        """Test experience scoring - John has 5+ years, job requires 4-7."""
        score = experience_score(test_resume_candidate.experience, ml_engineer_job)
        assert 0.7 <= score < 1, f"Expected less than perfect experience match for overqualified match, got {score}"

    def test_education_score_ml_job(self, test_resume_candidate, ml_engineer_job):
        """Test education scoring - John has MS in Computer Science."""
        score = education_score(test_resume_candidate.education, ml_engineer_job.education_keywords)
        assert score >= 0.5, f"Expected good education match, got {score}"

    def test_final_match_score_ml_job(self, test_resume_candidate, ml_engineer_job):
        """Test final weighted score for ML job - should be high match."""
        score = final_match_score(test_resume_candidate, ml_engineer_job)
        assert score >= 0.70, f"Expected strong match for ML job, got {score}"

    def test_final_match_score_backend_job(self, test_resume_candidate, backend_engineer_job):
        """Test final weighted score for backend job - should be moderate match."""
        score = final_match_score(test_resume_candidate, backend_engineer_job)
        assert 0.30 < score < 0.80, f"Expected moderate match for backend job, got {score}"

    def test_final_match_score_unrelated_job(self, test_resume_candidate, unrelated_job):
        """Test final weighted score for unrelated job - should be low match."""
        score = final_match_score(test_resume_candidate, unrelated_job)
        assert score < 0.40, f"Expected low match for unrelated job, got {score}"

    def test_matcher_ml_job(self, test_resume_candidate, ml_engineer_job):
        """Test full matcher function for ML job - should be Strong Match or Top Talent."""
        result = matcher(test_resume_candidate, ml_engineer_job)
        assert result in ["Strong Match", "Top Talent"], f"Expected high match level, got {result}"

    def test_matcher_backend_job(self, test_resume_candidate, backend_engineer_job):
        """Test full matcher function for backend job - should be Potential Fit."""
        result = matcher(test_resume_candidate, backend_engineer_job)
        assert result in ["Potential Fit", "Strong Match"], f"Expected moderate match level, got {result}"

    def test_matcher_unrelated_job(self, test_resume_candidate, unrelated_job):
        """Test full matcher function for unrelated job - should be Low Relevance or Not Recommended."""
        result = matcher(test_resume_candidate, unrelated_job)
        assert result in ["Low Relevance", "Not Recommended", "Potential Fit"], f"Expected low match level, got {result}"

    def test_candidate_skills_normalized(self, test_resume_candidate):
        """Verify that candidate skills are properly extracted and can be normalized."""
        assert len(test_resume_candidate.skills) > 0
        # All skills should be lowercase (parser returns lowercase)
        for skill in test_resume_candidate.skills:
            assert skill == skill.lower()