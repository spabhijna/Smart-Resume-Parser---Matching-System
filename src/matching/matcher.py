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
        self,
        candidate: Set[str],
        hard: Set[str],
        soft: Set[str],
        candidate_exp: int,
        role_type: str,
        is_junior: bool,
    ) -> float:
        """
        Score required skills with separate handling for hard vs soft requirements.

        Hard required skills: Must-have, heavy penalty if missing
        Soft required skills: Important but more forgiving, especially for seniors
        """
        if not hard and not soft:
            return 1.0

        # Apply skill groups for seniors and leadership roles
        if candidate_exp >= 10 or role_type == "LEADERSHIP":
            candidate = self._expand_with_skill_groups(candidate)

        # Score hard required skills (critical)
        hard_score = 1.0
        if hard:
            hard_matched = len(candidate & hard)
            hard_missing = len(hard) - hard_matched
            hard_ratio = hard_matched / len(hard)

            # Heavy penalty for missing hard required skills
            # Double penalty
            hard_penalty = self.config.required_decay ** (hard_missing * 2)
            hard_score = hard_ratio * hard_penalty

            # Set a lower floor for hard requirements
            hard_score = max(0.1, hard_score)

        # Score soft required skills (important but flexible)
        soft_score = 1.0
        if soft:
            soft_matched = len(candidate & soft)
            soft_missing = len(soft) - soft_matched
            soft_ratio = soft_matched / len(soft)

            # Apply forgiveness based on experience and role
            forgiveness = 0

            # Senior IC roles: forgive missing soft skills
            if role_type == "IC_SENIOR":
                # Forgive up to 2 missing soft skills
                forgiveness = min(2, soft_missing)

            # Leadership roles: concepts and experience matter more
            elif role_type == "LEADERSHIP":
                # Forgive up to 3 missing soft skills
                forgiveness = min(3, soft_missing)

            # Junior roles: forgive 1 missing web basic
            elif is_junior:
                web_basics = {"html", "css", "javascript", "js"}
                missing_soft = soft - candidate
                if missing_soft & web_basics:
                    forgiveness = 1  # Forgive 1 missing web basic

            soft_missing = max(0, soft_missing - forgiveness)

            # Milder penalty for missing soft skills
            soft_penalty = self.config.required_decay**soft_missing
            soft_score = soft_ratio * soft_penalty

            # Higher floor for soft requirements
            soft_score = max(self.config.min_required_floor, soft_score)

        # Combine hard and soft scores
        # Hard requirements are 70% of the score, soft are 30%
        if hard and soft:
            final_score = 0.7 * hard_score + 0.3 * soft_score
        elif hard:
            final_score = hard_score
        else:
            final_score = soft_score

        return final_score

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
        hard_req_skills = set(normalize_list(job.hard_required_skills))
        soft_req_skills = set(normalize_list(job.soft_required_skills))
        pref_skills = set(normalize_list(job.preferred_skills))

        # Determine if this is a junior role
        is_junior = job.min_experience <= 1

        breakdown = {
            "required": self._required_skill_score(
                cand_skills,
                hard_req_skills,
                soft_req_skills,
                candidate.experience,
                job.role_type,
                is_junior,
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
