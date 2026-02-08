from pathlib import Path
from typing import List, Optional

from data.jobs.Jobs import junior_job, manager_job, ml_job
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
        storage_directory: str = "src/storage",
        match_config: Optional[MatchConfig] = None,
    ):
        self.resume_directory = Path(resume_directory)
        self.storage_directory = Path(storage_directory)

        self.resumes_raw: List[tuple[str, str]] = []
        self.candidates: List[Candidate] = []
        self.jobs: List[Job] = []
        self.reports: List[JobReport] = []

        self.parser = ResumeParser()
        self.matcher = RuleBasedCandidateMatcher(config=match_config)

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

            except Exception as e:
                print(f"✗ Failed to parse {filename}: {e}")

        return len(self.candidates)



    def load_jobs(self, jobs: Optional[List[Job]] = None) -> int:
        self.jobs = jobs if jobs is not None else [
            ml_job, junior_job, manager_job
        ]
        return len(self.jobs)



    def match_candidates_to_job(self, job: Job) -> JobReport:
        report = JobReport(job)

        print(f"\n{'=' * 60}")
        print(f"MATCHING: {job.title} at {job.company}")
        print(f"{'=' * 60}")

        for candidate in self.candidates:
            try:
                match_result = self.matcher.match(candidate, job)
                report.add_candidate(candidate)  # Remove match_result parameter

                print(f"\n{candidate.name}")
                print(f"  Score: {match_result['score']:.2f}")
                print(f"  Match Level: {match_result['level']}")
                print(f"  Breakdown:")
                for k, v in match_result["breakdown"].items():
                    print(f"    - {k}: {v:.2f}")

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

        return len(self.reports)



    def display_top_candidates(self, report: JobReport, top_n: int = 3):
        print(f"\n{'=' * 60}")
        print(f"TOP {top_n} CANDIDATES FOR: {report.job.title}")
        print(f"{'=' * 60}")

        for i, result in enumerate(report.results[:top_n], 1):
            print(f"\n{i}. {result['candidate_name']}")
            print(
                f"   Score: {result['score']:.2f} "
                f"({result['match_level']})"
            )
            print(f"   Experience: {result['years_exp']} years")

            if result["missing_required_skills"]:
                print(
                    f"   Missing Skills: "
                    f"{', '.join(result['missing_required_skills'])}"
                )
            else:
                print(f"   ✓ Has all required skills")



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

        print(f"\n{'=' * 60}")
        print(" PIPELINE COMPLETE")
        print(f"{'=' * 60}\n")
        print("Summary:")
        print(f"  - Processed {parsed} candidates")
        print(f"  - Matched against {jobs_loaded} jobs")
        print(f"  - Generated {reports_generated} reports")
        print(f"  - Saved {reports_saved} reports")
        print(f"  - Reports saved to: {self.storage_directory.absolute()}")

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


def main():
    pipeline = ResumeParserPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
