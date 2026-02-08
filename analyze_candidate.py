"""
One-on-One Resume Analyzer
Analyze a single candidate's resume against a specific job posting.
Provides detailed matching insights and AI-powered recommendations.
"""

import sys
from pathlib import Path

from src.ai.ai_service import HiringAIAssistant
from src.matching.matcher import RuleBasedCandidateMatcher
from src.models.candidate import Candidate
from src.models.job import Job
from src.parsing.parser import ResumeParser
from src.utils.matcher_utils import normalize_list


class OneOnOneAnalyzer:
    """
    Focused analyzer for single candidate-job pairing.
    Provides comprehensive analysis with AI insights.
    """

    def __init__(self):
        self.parser = ResumeParser()
        self.matcher = RuleBasedCandidateMatcher()
        self.ai_assistant = HiringAIAssistant()

    def analyze_resume(self, resume_path: str, job: Job) -> dict:
        """
        Analyze a single resume against a job posting.

        Args:
            resume_path: Path to resume text file
            job: Job object to match against

        Returns:
            Comprehensive analysis dictionary
        """
        print(f"\n{'=' * 70}")
        print(" ONE-ON-ONE RESUME ANALYSIS")
        print(f"{'=' * 70}\n")

        # Step 1: Load and parse resume
        print("📄 Step 1: Parsing Resume...")
        print(f"   File: {resume_path}")

        try:
            resume_text = Path(resume_path).read_text(encoding="utf-8")
            candidate = self.parser.parse(resume_text)
            candidate.resume_link = Path(resume_path).name
        except Exception as e:
            print(f"❌ Error parsing resume: {e}")
            return {}

        print(f"   ✓ Parsed: {candidate.name}")
        print(f"   ✓ Experience: {candidate.experience} years")
        print(f"   ✓ Skills: {len(candidate.skills)} identified\n")

        # Step 2: Generate AI summary
        if self.ai_assistant.enabled:
            print("🤖 Step 2: Generating AI Profile Summary...")
            try:
                ai_summary = self.ai_assistant.summarize_candidate(candidate)
                if ai_summary:
                    candidate.ai_summary = ai_summary
                    print(f"   {ai_summary}\n")
                else:
                    print("   ⚠️  AI summary not available\n")
            except Exception as e:
                print(f"   ⚠️  AI summary failed: {e}\n")
        else:
            print("⚠️  Step 2: AI features disabled (no API key)\n")

        # Step 3: Match against job
        print(f"💼 Step 3: Matching Against Job: {job.title}")
        print(f"   Company: {job.company}")
        print(f"   Location: {job.location}\n")

        try:
            match_result = self.matcher.match(candidate, job)
        except Exception as e:
            print(f"❌ Error during matching: {e}")
            return {}

        # Calculate skill gaps
        cand_skills = normalize_list(candidate.skills)
        hard_req = normalize_list(job.hard_required_skills)
        soft_req = normalize_list(job.soft_required_skills)
        preferred = normalize_list(job.preferred_skills)

        matched_hard = list(hard_req & cand_skills)
        missing_hard = list(hard_req - cand_skills)
        matched_soft = list(soft_req & cand_skills)
        missing_soft = list(soft_req - cand_skills)
        matched_preferred = list(preferred & cand_skills)
        missing_preferred = list(preferred - cand_skills)

        # Display results
        self._display_match_results(
            candidate=candidate,
            job=job,
            match_result=match_result,
            matched_hard=matched_hard,
            missing_hard=missing_hard,
            matched_soft=matched_soft,
            missing_soft=missing_soft,
            matched_preferred=matched_preferred,
            missing_preferred=missing_preferred,
        )

        # Step 4: AI explanation
        if self.ai_assistant.enabled:
            print("\n🤖 AI Match Explanation:")
            print(f"   {'─' * 66}")
            try:
                ai_explanation = self.ai_assistant.explain_match(
                    candidate=candidate,
                    job=job,
                    score=match_result["score"],
                    breakdown=match_result["breakdown"],
                    missing_hard=missing_hard,
                    missing_soft=missing_soft,
                )
                if ai_explanation:
                    # Format explanation with proper indentation
                    lines = ai_explanation.split(". ")
                    for line in lines:
                        if line.strip():
                            print(f"   {line.strip()}.")
                else:
                    print("   ⚠️  AI explanation not available")
            except Exception as e:
                print(f"   ⚠️  AI explanation failed: {e}")

        # Generate recommendation
        print(f"\n{'=' * 70}")
        self._display_recommendation(match_result["score"], missing_hard)
        print(f"{'=' * 70}\n")

        return {
            "candidate": candidate,
            "job": job,
            "match_result": match_result,
            "skill_analysis": {
                "matched_hard": matched_hard,
                "missing_hard": missing_hard,
                "matched_soft": matched_soft,
                "missing_soft": missing_soft,
                "matched_preferred": matched_preferred,
                "missing_preferred": missing_preferred,
            },
        }

    def _display_match_results(
        self,
        candidate: Candidate,
        job: Job,
        match_result: dict,
        matched_hard: list,
        missing_hard: list,
        matched_soft: list,
        missing_soft: list,
        matched_preferred: list,
        missing_preferred: list,
    ):
        """Display detailed match results."""
        score = match_result["score"]
        level = match_result["level"]
        breakdown = match_result["breakdown"]

        print("📊 Match Results:")
        print(f"   {'─' * 66}")
        print(f"   Overall Score: {score:.2f} ({level})")
        print(f"   {'─' * 66}")
        print("\n   Component Breakdown:")
        for component, value in breakdown.items():
            bar_length = int(value * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            print(f"   {component:20} [{bar}] {value:.2f}")

        # Experience analysis
        print(f"\n   📅 Experience Analysis:")
        exp_diff = candidate.experience - job.min_experience
        if job.max_experience:
            if candidate.experience < job.min_experience:
                print(
                    f"   ⚠️  Below minimum: {candidate.experience} years "
                    f"(need {job.min_experience}+)"
                )
            elif candidate.experience > job.max_experience:
                print(
                    f"   ⚠️  Above maximum: {candidate.experience} years "
                    f"(range {job.min_experience}-{job.max_experience})"
                )
            else:
                print(
                    f"   ✓ Within range: {candidate.experience} years "
                    f"(range {job.min_experience}-{job.max_experience})"
                )
        else:
            if exp_diff >= 0:
                print(
                    f"   ✓ Meets requirement: {candidate.experience} years "
                    f"({exp_diff} above minimum)"
                )
            else:
                print(
                    f"   ⚠️  Below minimum: {candidate.experience} years "
                    f"(need {job.min_experience}+)"
                )

        # Hard required skills
        total_hard = len(matched_hard) + len(missing_hard)
        print(f"\n   🎯 Hard Required Skills ({len(matched_hard)}/{total_hard}):")
        if matched_hard:
            print(f"   ✓ Matched: {', '.join(matched_hard)}")
        if missing_hard:
            print(f"   ✗ Missing: {', '.join(missing_hard)}")

        # Soft required skills
        total_soft = len(matched_soft) + len(missing_soft)
        print(f"\n   🔧 Soft Required Skills ({len(matched_soft)}/{total_soft}):")
        if matched_soft:
            print(f"   ✓ Matched: {', '.join(matched_soft)}")
        if missing_soft:
            print(f"   ⚠️  Missing: {', '.join(missing_soft)}")

        # Preferred skills
        total_pref = len(matched_preferred) + len(missing_preferred)
        print(f"\n   ⭐ Preferred Skills ({len(matched_preferred)}/{total_pref}):")
        if matched_preferred:
            print(f"   ✓ Matched: {', '.join(matched_preferred)}")
        if missing_preferred:
            print(f"   • Not Found: {', '.join(missing_preferred)}")

    def _display_recommendation(self, score: float, missing_hard: list):
        """Display hiring recommendation based on score."""
        print("💡 RECOMMENDATION:")
        print()

        if score >= 0.85:
            print("   🌟 STRONG CANDIDATE - Highly Recommended")
            print("   → Schedule interview immediately")
            print("   → Candidate exceeds requirements")
        elif score >= 0.70:
            print("   ✅ GOOD FIT - Recommended for Interview")
            print("   → Schedule screening interview")
            print("   → Strong match with minor gaps")
        elif score >= 0.50:
            print("   ⚠️  POTENTIAL FIT - Consider with Reservations")
            print("   → Review missing requirements carefully")
            if missing_hard:
                print(f"   → Key gaps: {', '.join(missing_hard[:3])}")
            print("   → May need additional training/support")
        else:
            print("   ❌ WEAK MATCH - Not Recommended")
            print("   → Significant gaps in required qualifications")
            if missing_hard:
                print(f"   → Critical missing: {', '.join(missing_hard)}")
            print("   → Consider other candidates")


def main():
    """Interactive CLI for one-on-one resume analysis."""
    print("\n" + "=" * 70)
    print(" ONE-ON-ONE RESUME ANALYZER")
    print("=" * 70)

    analyzer = OneOnOneAnalyzer()

    # Get resume path
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
    else:
        print("\nEnter resume file path:")
        print("(e.g., data/resumes/Dr_Sarah_Chen_resume.txt)")
        resume_path = input("Resume: ").strip()

    if not Path(resume_path).exists():
        print(f"\n❌ Error: Resume file not found: {resume_path}")
        print("\nAvailable resumes in data/resumes/:")
        resume_dir = Path("data/resumes")
        if resume_dir.exists():
            for file in resume_dir.glob("*.txt"):
                print(f"   - {file.name}")
        return

    # Select job
    print("\nAvailable jobs:")
    from data.jobs.Jobs import junior_job, manager_job, ml_job

    jobs = {
        "1": ("Machine Learning Engineer", ml_job),
        "2": ("Junior Web Developer", junior_job),
        "3": ("Engineering Manager", manager_job),
    }

    print()
    for key, (title, _) in jobs.items():
        print(f"   {key}. {title}")

    print("\nSelect job number (1-3):")
    choice = input("Job: ").strip()

    if choice not in jobs:
        print(f"\n❌ Error: Invalid job selection: {choice}")
        return

    job_title, job = jobs[choice]

    # Run analysis
    result = analyzer.analyze_resume(resume_path, job)

    if result:
        # Offer to save detailed report
        print("\nSave detailed analysis to file? (y/n):")
        save = input("Save: ").strip().lower()

        if save == "y":
            from datetime import datetime
            import json

            candidate_name = result["candidate"].name.replace(" ", "_")
            job_title_slug = job.title.replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{candidate_name}_{job_title_slug}_{timestamp}.json"

            output = {
                "candidate_name": result["candidate"].name,
                "job_title": job.title,
                "score": result["match_result"]["score"],
                "match_level": result["match_result"]["level"],
                "breakdown": result["match_result"]["breakdown"],
                "skill_analysis": result["skill_analysis"],
                "candidate_summary": result["candidate"].ai_summary,
                "timestamp": datetime.now().isoformat(),
            }

            output_path = Path("src/storage") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                json.dump(output, f, indent=2)

            print(f"   ✓ Saved to: {output_path}")


if __name__ == "__main__":
    main()
