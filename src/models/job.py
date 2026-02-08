from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class Job:
    title: str
    description: str
    company: str
    location: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience: int
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    education_keywords: Optional[List[str]] = None

    def to_dict(self):
        """Converts the dataclass instance to a dictionary for JSON exports."""
        return asdict(self)

    def __str__(self):
        # Your existing logic with a small tweak for cleaner formatting
        salary_range = ""
        if self.min_salary or self.max_salary:
            salary_range = f"Salary: ${self.min_salary or 0:,} - ${self.max_salary or 0:,}\n"
        
        experience_range = f"{self.min_experience}+ years"
        if self.max_experience:
            experience_range = f"{self.min_experience}-{self.max_experience} years"
        
        return (
            f"Job Title: {self.title}\n"
            f"Company: {self.company}\n"
            f"Location: {self.location}\n"
            f"Description: {self.description[:100]}...\n" # Truncated for readability
            f"Required Skills: {', '.join(self.required_skills)}\n"
            f"Preferred Skills: {', '.join(self.preferred_skills)}\n"
            f"Experience: {experience_range}\n"
            f"{salary_range}"
            f"Education: {', '.join(self.education_keywords) if self.education_keywords else 'None'}"
        )
