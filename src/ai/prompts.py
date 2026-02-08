"""
Prompt templates for AI-powered insights.
These templates guide the AI to provide consistent, recruiter-friendly explanations.
"""

from src.models.candidate import Candidate
from src.models.job import Job


def get_candidate_summary_prompt(candidate: Candidate) -> str:
    """
    Generate a prompt for AI to summarize a candidate profile.

    Focus: Professional strengths, career trajectory, and specializations.
    """
    education_str = ", ".join([e.get("degree", "Unknown") for e in candidate.education])
    skills_str = ", ".join(candidate.skills[:10])  # Top 10 skills

    return f"""Analyze this candidate profile and provide a concise professional summary (3-4 sentences).
Focus on: career level, key strengths, technical expertise, and leadership potential.

Candidate: {candidate.name}
Experience: {candidate.experience} years
Skills: {skills_str}{"..." if len(candidate.skills) > 10 else ""}
Education: {education_str}

Provide a recruiter-friendly summary that highlights:
1. Seniority level and career trajectory
2. Core technical strengths
3. Domain expertise or specialization
4. Any notable qualifications

Keep it concise and professional. No bullet points."""


def get_match_explanation_prompt(
    candidate: Candidate,
    job: Job,
    score: float,
    breakdown: dict,
    missing_hard: list,
    missing_soft: list,
) -> str:
    """
    Generate a prompt for AI to explain why a candidate received a particular match score.

    Focus: Clear reasoning, gap analysis, and actionable insights.
    """
    candidate_skills = ", ".join(candidate.skills[:15])
    required_hard = ", ".join(job.hard_required_skills)
    required_soft = ", ".join(job.soft_required_skills)
    preferred = ", ".join(job.preferred_skills)

    missing_hard_str = ", ".join(missing_hard) if missing_hard else "None"
    missing_soft_str = ", ".join(missing_soft) if missing_soft else "None"

    return f"""Explain why this candidate received a match score of {score:.2f} for this job position.
Provide a clear, recruiter-friendly explanation (3-4 sentences).

JOB: {job.title} at {job.company}
Required Hard Skills: {required_hard}
Required Soft Skills: {required_soft}
Preferred Skills: {preferred}
Experience Required: {job.min_experience}+ years

CANDIDATE: {candidate.name}
Experience: {candidate.experience} years
Skills: {candidate_skills}
Missing Hard Required: {missing_hard_str}
Missing Soft Required: {missing_soft_str}

Score Breakdown:
- Required Skills Score: {breakdown.get("required_skills", 0):.2f}
- Preferred Skills Score: {breakdown.get("preferred_skills", 0):.2f}
- Experience Score: {breakdown.get("experience", 0):.2f}
- Education Score: {breakdown.get("education", 0):.2f}

Provide explanation that:
1. Summarizes why the score is appropriate
2. Highlights key strengths that match the role
3. Identifies critical gaps if any
4. Gives a recommendation (Strong Match, Interview, Pass, etc.)

Keep it concise and actionable. No bullet points."""


def get_feedback_analysis_prompt(feedback_batch: list) -> str:
    """
    Generate a prompt for AI to analyze hiring feedback and suggest improvements.

    Focus: Pattern recognition, rule refinement suggestions, and skill categorization.
    """
    feedback_items = []
    for i, fb in enumerate(feedback_batch, 1):
        feedback_items.append(
            f"\n{i}. Candidate: {fb['candidate_name']} | Job: {fb['job_title']}\n"
            f"   Decision: {fb['decision']} | Score: {fb['score']:.2f}\n"
            f"   Recruiter Notes: {fb['notes']}"
        )

    feedback_text = "\n".join(feedback_items)

    return f"""Analyze these hiring decisions and suggest improvements to the matching system.
Focus on identifying patterns where the scoring system may need refinement.

HIRING FEEDBACK:
{feedback_text}

Based on this feedback, suggest:
1. Skill groupings that should be treated similarly (e.g., "PyTorch and TensorFlow are interchangeable for senior ML roles")
2. Experience requirements that may need adjustment
3. Skills that should be reclassified (hard required → soft required, or vice versa)
4. Penalty adjustments for missing skills based on role type

Provide 3-5 specific, actionable suggestions for improving the matching rules.
Format as numbered recommendations."""
