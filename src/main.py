from pathlib import Path
from typing import List, Optional

from src.ai.ai_service import HiringAIAssistant
from src.fixtures import junior_job, manager_job, ml_job
from src.matching.matcher import RuleBasedCandidateMatcher
from src.models.candidate import Candidate
from src.models.job import Job
from src.models.match_config import MatchConfig
from src.parsing.parser import ResumeParser
from src.reporting.report_generator import JobReport


class ResumeParserPipeline:
    """
    Main pipeline class for processing resumes and matching candidates to jobs.
    Matcher is the single source of truth for scoring and reasoning.
    """

    def __init__(
        self,
        resume_directory: str = "data/resumes",
        storage_directory: str = "output",
        match_config: Optional[MatchConfig] = None,
    ):
        self.resume_directory = Path(resume_directory)
        self.storage_directory = Path(storage_directory)

        self.resumes_raw: List[tuple[str, str]] = []
        self.candidates: List[Candidate] = []
        self.jobs: List[Job] = []
        self.reports: List[JobReport] = []
        self.feedback: List[dict] = []  # Collect recruiter feedback

        self.parser = ResumeParser()
        self.matcher = RuleBasedCandidateMatcher(config=match_config)
        self.ai_assistant = HiringAIAssistant()  # AI for explanations

        self.storage_directory.mkdir(parents=True, exist_ok=True)

    def load_resumes(self) -> int:
        self.resumes_raw = []

        if not self.resume_directory.exists():
            print(f"Warning: Directory {self.resume_directory} does not exist")
            return 0

        for file_path in self.resume_directory.glob("*.txt"):
            try:
                content = file_path.read_text(encoding="utf-8")
                self.resumes_raw.append((file_path.name, content))
                print(f"✓ Loaded: {file_path.name}")
            except Exception as e:
                print(f"✗ Failed to load {file_path.name}: {e}")

        return len(self.resumes_raw)

    def parse_resumes(self) -> int:
        self.candidates = []

        print(f"\n{'=' * 60}")
        print("PARSING RESUMES")
        print(f"{'=' * 60}")

        for filename, resume_text in self.resumes_raw:
            try:
                candidate = self.parser.parse(resume_text)
                candidate.resume_link = filename

                # AI Integration Point 1: Generate candidate summary
                try:
                    ai_summary = self.ai_assistant.summarize_candidate(candidate)
                    if ai_summary:
                        candidate.ai_summary = ai_summary
                except Exception as ai_error:
                    print(f"  ⚠️  AI summary failed: {ai_error}")

                self.candidates.append(candidate)

                print(f"\n✓ Parsed: {candidate.name}")
                print(f"  Email: {candidate.email}")
                print(f"  Phone: {candidate.phone}")
                print(f"  Experience: {candidate.experience} years")
                print(
                    f"  Skills: {', '.join(candidate.skills[:5])}"
                    f"{'...' if len(candidate.skills) > 5 else ''}"
                )
                print(f"  Education: {len(candidate.education)} degree(s)")

                # Display AI summary if available
                if candidate.ai_summary:
                    print(f"  💡 AI Summary: {candidate.ai_summary}")

            except Exception as e:
                print(f"✗ Failed to parse {filename}: {e}")

        return len(self.candidates)

    def load_jobs(self, jobs: Optional[List[Job]] = None) -> int:
        self.jobs = jobs if jobs is not None else [ml_job, junior_job, manager_job]
        return len(self.jobs)

    def match_candidates_to_job(self, job: Job) -> JobReport:
        report = JobReport(job)

        print(f"\n{'=' * 60}")
        print(f"MATCHING: {job.title} at {job.company}")
        print(f"{'=' * 60}")

        for candidate in self.candidates:
            try:
                match_result = self.matcher.match(candidate, job)

                # Extract missing skills for AI context
                from src.utils.matcher_utils import normalize_list

                cand_skills = normalize_list(candidate.skills)
                hard_req = normalize_list(job.hard_required_skills)
                soft_req = normalize_list(job.soft_required_skills)
                missing_hard = list(hard_req - cand_skills)
                missing_soft = list(soft_req - cand_skills)

                # AI Integration Point 2: Generate match explanation
                ai_explanation = None
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
                        match_result["ai_explanation"] = ai_explanation
                except Exception as ai_error:
                    print(f"  ⚠️  AI explanation failed: {ai_error}")

                report.add_candidate(
                    candidate, ai_explanation, missing_hard, missing_soft
                )

                print(f"\n{candidate.name}")
                print(f"  Score: {match_result['score']:.2f}")
                print(f"  Match Level: {match_result['level']}")
                print("  Breakdown:")
                for k, v in match_result["breakdown"].items():
                    print(f"    - {k}: {v:.2f}")

                # Display AI explanation if available
                if ai_explanation:
                    print(f"\n  💡 AI Explanation:\n  {ai_explanation}")

            except Exception as e:
                print(f"✗ Failed to match {candidate.name}: {e}")

        return report

    def match_all_jobs(self) -> int:
        self.reports = []

        print("\nMatching candidates to jobs...")

        for job in self.jobs:
            report = self.match_candidates_to_job(job)

            # Enforce stable ranking
            report.results.sort(key=lambda r: r["score"], reverse=True)

            self.reports.append(report)
            self.display_top_candidates(report, top_n=3)

            # AI Integration Point 4: Collect feedback after displaying results
            self.collect_feedback_for_job(report)

        return len(self.reports)

    def display_top_candidates(self, report: JobReport, top_n: int = 3):
        print(f"\n{'=' * 60}")
        print(f"TOP {top_n} CANDIDATES FOR: {report.job.title}")
        print(f"{'=' * 60}")

        for i, result in enumerate(report.results[:top_n], 1):
            print(f"\n{i}. {result['candidate_name']}")
            print(f"   Score: {result['score']:.2f} ({result['match_level']})")
            print(f"   Experience: {result['years_exp']} years")

            if result["missing_hard_required_skills"]:
                print(
                    f"   Missing Hard Required: "
                    f"{', '.join(result['missing_hard_required_skills'])}"
                )
            if result["missing_soft_required_skills"]:
                print(
                    f"   Missing Soft Required: "
                    f"{', '.join(result['missing_soft_required_skills'])}"
                )
            if (
                not result["missing_hard_required_skills"]
                and not result["missing_soft_required_skills"]
            ):
                print("   ✓ Has all required skills")

    def save_reports(self) -> int:
        print(f"\n{'=' * 60}")
        print("SAVING REPORTS")
        print(f"{'=' * 60}")

        saved = 0
        for report in self.reports:
            try:
                slug = report.job.title.lower().replace(" ", "_")
                report.save_json(str(self.storage_directory), slug)
                print(f"✓ Saved JSON report for: {report.job.title}")
                saved += 1
            except Exception as e:
                print(f"✗ Failed to save report for {report.job.title}: {e}")

        return saved

    def run(self, jobs: Optional[List[Job]] = None):
        print("\n" + "=" * 60)
        print(" RESUME PARSER PIPELINE - STARTING")
        print("=" * 60 + "\n")

        print("Step 1: Loading resumes...")
        resumes_loaded = self.load_resumes()
        print(f"\nLoaded {resumes_loaded} resume(s)")
        if resumes_loaded == 0:
            return

        print("\nStep 2: Parsing resumes...")
        parsed = self.parse_resumes()
        print(f"\nSuccessfully parsed {parsed} candidate(s)")
        if parsed == 0:
            return

        jobs_loaded = self.load_jobs(jobs)
        print(f"\nStep 3: Loaded {jobs_loaded} job(s)")

        print("\nStep 4: Matching candidates to jobs...")
        reports_generated = self.match_all_jobs()

        print("\nStep 5: Saving reports...")
        reports_saved = self.save_reports()

        # AI Integration Point 5: Analyze feedback if collected
        if self.feedback:
            print("\nStep 6: Analyzing feedback with AI...")
            self.analyze_feedback()

        print(f"\n{'=' * 60}")
        print(" PIPELINE COMPLETE")
        print(f"{'=' * 60}\n")
        print("Summary:")
        print(f"  - Processed {parsed} candidates")
        print(f"  - Matched against {jobs_loaded} jobs")
        print(f"  - Generated {reports_generated} reports")
        print(f"  - Saved {reports_saved} reports")
        print(f"  - Reports saved to: {self.storage_directory.absolute()}")

    # Feedback collection and learning
    # -------------------------------------------------

    def collect_feedback_for_job(self, report: JobReport):
        """
        AI Integration Point 3: Collect interactive feedback from recruiters.
        This enables the learning loop where AI suggests improvements.
        """
        if not self.ai_assistant.enabled:
            return  # Skip feedback if AI is disabled

        print(f"\n{'=' * 60}")
        print(f"FEEDBACK COLLECTION: {report.job.title}")
        print(f"{'=' * 60}")
        print(
            "Would you like to provide feedback on candidates? (helps improve matching)"
        )
        collect = input("Collect feedback? (y/n): ").strip().lower()

        if collect != "y":
            print("Skipping feedback collection.")
            return

        # Collect feedback for top candidates
        for i, result in enumerate(report.results[:3], 1):
            print(f"\n{i}. {result['candidate_name']} - Score: {result['score']:.2f}")
            decision = input("   Decision (interview/pass/skip): ").strip().lower()

            if decision == "skip":
                continue

            notes = input("   Notes (optional): ").strip()

            self.feedback.append(
                {
                    "candidate_name": result["candidate_name"],
                    "job_title": report.job.title,
                    "score": result["score"],
                    "decision": decision,
                    "notes": notes or "No additional notes",
                }
            )

        print(
            f"\n✓ Collected {len([f for f in self.feedback if f['job_title'] == report.job.title])} feedback items"
        )

    def analyze_feedback(self):
        """
        AI Integration Point 6: Analyze collected feedback and suggest improvements.
        This is the "learning" component where AI identifies patterns.
        """
        if not self.feedback:
            print("No feedback to analyze.")
            return

        print(f"\n{'=' * 60}")
        print("AI FEEDBACK ANALYSIS")
        print(f"{'=' * 60}")
        print(f"Analyzing {len(self.feedback)} feedback items...\n")

        try:
            suggestions = self.ai_assistant.suggest_refinements(self.feedback)

            if suggestions:
                print("🎯 AI RECOMMENDATIONS FOR MATCHING SYSTEM:\n")
                print(suggestions)

                # Optionally save to file
                suggestions_file = self.storage_directory / "ai_suggestions.txt"
                with open(suggestions_file, "a") as f:
                    from datetime import datetime

                    f.write(f"\n\n{'=' * 60}\n")
                    f.write(
                        f"Feedback Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    f.write(f"{'=' * 60}\n\n")
                    f.write(suggestions)
                    f.write("\n")

                print(f"\n✓ Suggestions saved to: {suggestions_file}")
            else:
                print("⚠️  AI analysis did not return suggestions.")

        except Exception as e:
            print(f"✗ Failed to analyze feedback: {e}")

    # Lookup helpers
    # -------------------------------------------------

    def get_report_by_job_title(self, job_title: str) -> Optional[JobReport]:
        return next(
            (r for r in self.reports if r.job.title.lower() == job_title.lower()),
            None,
        )

    def get_candidate_by_name(self, name: str) -> Optional[Candidate]:
        return next(
            (c for c in self.candidates if c.name.lower() == name.lower()),
            None,
        )
