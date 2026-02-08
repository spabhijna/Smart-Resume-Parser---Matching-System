import math
from typing import Dict, List, Set, Tuple

from src.models.candidate import Candidate
from src.models.job import Job
from src.models.match_config import MatchConfig
from src.utils.matcher_utils import SKILL_GROUPS, match_level, normalize_list


class RuleBasedCandidateMatcher:
    """
    Fully rule-based candidate matcher.

    Characteristics:
    - Deterministic
    - Explainable
    - Configurable
    - No ML assumptions
    """

    def __init__(self, config: MatchConfig | None = None):
        self.config = config or MatchConfig()

    def _required_skill_score(
        self, candidate: Set[str], required: Set[str], candidate_exp: int
    ) -> float:
        if not required:
            return 1.0

        # Apply skill groups ONLY for seniors
        if candidate_exp >= 10:
            candidate = self._expand_with_skill_groups(candidate)

        matched = len(candidate & required)
        missing = len(required) - matched

        ratio = matched / len(required)

        # Seniors get one missing skill forgiven
        if candidate_exp >= 10:
            missing = max(0, missing - 1)

        penalty = self.config.required_decay**missing
        score = ratio * penalty

        return max(self.config.min_required_floor, score)

    def _preferred_skill_score(self, candidate: Set[str], preferred: Set[str]) -> float:
        if not preferred:
            return 0.0

        return len(candidate & preferred) / len(preferred)

    def _experience_score(self, candidate_exp: int, job: Job) -> float:
        min_exp = job.min_experience or 0
        max_exp = job.max_experience

        if candidate_exp < min_exp:
            gap = min_exp - candidate_exp
            return max(0.0, 1.0 - self.config.under_exp_penalty * gap)

        if max_exp and candidate_exp > max_exp:
            over = candidate_exp - max_exp
            decay = math.exp(-self.config.over_exp_decay * over)
            return max(self.config.over_exp_floor, decay)

        return 1.0

    def _education_score(
        self, education: List[dict], keywords: List[str] | None
    ) -> float:
        if not keywords:
            return 0.0

        text = " ".join(e.get("raw", "").lower() for e in education)

        matches = sum(1 for k in keywords if f" {k.lower()} " in f" {text} ")

        return matches / len(keywords)

    def score(self, candidate: Candidate, job: Job) -> Tuple[float, Dict[str, float]]:
        cand_skills = set(normalize_list(candidate.skills))
        req_skills = set(normalize_list(job.required_skills))
        pref_skills = set(normalize_list(job.preferred_skills))

        breakdown = {
            "required": self._required_skill_score(
                cand_skills, req_skills, candidate.experience
            ),
            "preferred": self._preferred_skill_score(cand_skills, pref_skills),
            "experience": self._experience_score(candidate.experience, job),
            "education": self._education_score(
                candidate.education, job.education_keywords
            ),
        }

        cfg = self.config
        final_score = (
            cfg.required_weight * breakdown["required"]
            + cfg.preferred_weight * breakdown["preferred"]
            + cfg.experience_weight * breakdown["experience"]
            + cfg.education_weight * breakdown["education"]
        )

        return round(final_score, 3), breakdown

    def match(self, candidate: Candidate, job: Job) -> Dict:
        score, breakdown = self.score(candidate, job)

        return {
            "score": score,
            "level": match_level(score),
            "breakdown": breakdown,
        }

    def _expand_with_skill_groups(self, skills: Set[str]) -> Set[str]:
        expanded = set(skills)

        for group_skills in SKILL_GROUPS.values():
            if skills & group_skills:
                expanded |= group_skills

        return expanded
