"""
Data models for the Resume Parser application.

This package contains dataclass definitions for:
- Candidate: Represents a parsed resume
- Job: Represents a job posting with requirements
- MatchConfig: Configuration for candidate-job matching
"""

from src.models.candidate import Candidate
from src.models.job import Job
from src.models.match_config import MatchConfig

__all__ = ["Candidate", "Job", "MatchConfig"]
