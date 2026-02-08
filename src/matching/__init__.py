"""
Candidate-job matching module.

This package contains the rule-based matching system that scores
candidates against job requirements.
"""

from src.matching.matcher import RuleBasedCandidateMatcher

__all__ = ["RuleBasedCandidateMatcher"]
