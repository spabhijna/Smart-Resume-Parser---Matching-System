from src.utils.matcher_utils import normalize_list, match_level
from typing import List
from src.models.job import Job
from src.models.candidate import Candidate

# returns in the range of (0-1)
def required_skills_score(candidate_skills: List[str], required_skills) -> float:
    req_set = set(required_skills)
    cand_set = set(candidate_skills)

    if not req_set:
        return 1
    
    matched_count = len(req_set.intersection(cand_set))
    missing_count = len(req_set) - matched_count

    ratio = matched_count/ len(req_set)

    decay_factor = 0.5
    penalty = decay_factor ** missing_count

    return round(ratio * penalty, 3)

def preferred_skill_score(candidate_skills: List[str], preferred_skills) -> float:
    if not preferred_skills:
        return 1.0
    matched = candidate_skills.intersection(preferred_skills)

    return len(matched) / len(preferred_skills)

def experience_score(candidate_exp: int, job: Job) -> float:
    if candidate_exp < job.min_experience:
        if candidate_exp >= job.min_experience - 1:
            return 0.5  
        return 0.0

    if not job.max_experience or (job.min_experience <= candidate_exp <= job.max_experience):
        return 1.0

    if candidate_exp > job.max_experience:
        years_over = candidate_exp - job.max_experience
        penalty = years_over * 0.05
        return max(0.7, 1.0 - penalty)

    return 1.0

def education_score(candidate_edu: list[dict], keywords: list[str] | None) -> float:
    if not keywords:
        return 1.0

    text = " ".join(
        e.get("raw", "").lower() for e in candidate_edu
    )

    matches = sum(1 for k in keywords if k.lower() in text)
    return matches / len(keywords)

def final_match_score(candidate, job) -> float:
    candidate_skills = normalize_list(candidate.skills)
    required = normalize_list(job.required_skills)
    preferred = normalize_list(job.preferred_skills)

    req_skill_score = required_skills_score(candidate_skills, required)

    pref_skill_score = preferred_skill_score(candidate_skills, preferred)
    exp_score = experience_score(candidate.experience, job)
    edu_score = education_score(candidate.education, job.education_keywords)

    return round(
    0.60 * req_skill_score +  # Required skills are 60% of the total
    0.15 * pref_skill_score + # Preferred skills are 15%
    0.15 * exp_score +        # Experience is 15%
    0.10 * edu_score,         # Education is 10%
    2
)

def matcher(candidate: Candidate, job: Job) -> str:
    score = final_match_score(candidate, job)

    return match_level(score)
