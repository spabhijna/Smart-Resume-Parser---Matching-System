"""
Sample job postings for testing and demonstration.

This module contains predefined Job instances used for:
- Testing the resume parser and matching system
- Demonstrating functionality in CLI tools
- Running examples and demos

These are not production data - they're fixtures for development and testing.
"""

from src.models.job import Job

# Machine Learning Engineer position - senior IC role
ml_job = Job(
    title="Machine Learning Engineer",
    company="NeuralNet Labs",
    location="San Francisco (Hybrid)",
    description="Developing NLP and Computer Vision models for healthcare.",
    hard_required_skills=["Python"],
    soft_required_skills=["PyTorch", "TensorFlow", "SQL", "Scikit-Learn"],
    preferred_skills=["Docker", "Kubernetes", "HuggingFace", "CUDA"],
    min_experience=3,
    max_experience=7,
    role_type="IC_SENIOR",
    min_salary=140000,
    max_salary=190000,
    education_keywords=["Master's", "PhD", "Computer Science", "Mathematics"],
)

# Junior Web Developer - entry-level IC role
junior_job = Job(
    title="Junior Web Developer",
    company="GreenSeed Startups",
    location="Remote",
    description="Maintaining frontend components and simple Python backends.",
    hard_required_skills=["Python"],
    soft_required_skills=["HTML", "CSS", "JavaScript"],
    preferred_skills=["Git", "Django", "Tailwind"],
    min_experience=0,
    max_experience=2,
    role_type="IC",
    min_salary=60000,
    max_salary=85000,
    education_keywords=["Bachelor's", "Bootcamp"],
)

# Engineering Manager - leadership role
manager_job = Job(
    title="Engineering Manager",
    company="Global Fintech",
    location="New York",
    description="Leading a team of 10 backend engineers in the payments space.",
    hard_required_skills=["System Design", "Project Management"],
    soft_required_skills=["Python"],
    preferred_skills=["Agile", "Mentorship", "Fintech Experience", "AWS"],
    min_experience=8,
    max_experience=None,  # No upper limit for leadership
    role_type="LEADERSHIP",
    min_salary=180000,
    max_salary=250000,
    education_keywords=["Business", "Computer Science", "Management"],
)
