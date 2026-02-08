import csv
import json
from datetime import datetime
from pathlib import Path

from src.matching.matcher import RuleBasedCandidateMatcher
from src.models.job import Job
from src.utils.matcher_utils import normalize_list


class JobReport:
    def __init__(self, job: Job):
        self.job = job
        self.results = []
        self.base_path = Path("src/storage")
        self.matcher = RuleBasedCandidateMatcher()

    def add_candidate(self, candidate):
        """Calculates score and prepares data for export."""
        match_result = self.matcher.match(candidate, self.job)
        score = match_result["score"]
        match_status = match_result["level"]

        # Identify missing required skills for better reporting
        cand_skills = set(normalize_list(candidate.skills))
        req_skills = set(normalize_list(self.job.required_skills))
        missing = list(req_skills - cand_skills)

        self.results.append(
            {
                "candidate_name": candidate.name,
                "score": score,
                "match_level": match_status,
                "missing_required_skills": missing,
                "years_exp": candidate.experience,
            }
        )
        # Keep results sorted by highest score
        self.results.sort(key=lambda x: x["score"], reverse=True)

    def save_json(self, folder_path: str, filename: str):
        """Saves JSON to a specific directory, creating it if necessary."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        file_path = self.base_path / f"{filename}_{timestamp}.json"
        with open(file_path, "w") as f:
            json.dump({"job": self.job.title, "rankings": self.results}, f, indent=4)

    def to_csv(self, filename: str = "job_report"):
        """Writes the report to src/storage/filename.csv."""
        if not self.results:
            return "No data to export."

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        if filename.endswith(".csv"):
            filename = filename[:-4]

        final_filename = f"{filename}_{timestamp}.csv"

        file_path = self.base_dir / final_filename

        # 2. Create the folder if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 3. Write the data
        keys = self.results[0].keys()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(self.results)
            return f"Report successfully saved to {file_path}"
        except Exception as e:
            return f"Failed to save report: {str(e)}"
