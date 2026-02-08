from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Candidate:
    name: str
    email: Optional[str]
    phone: Optional[str]
    skills: List[str]
    education: List[dict]
    experience: int
    resume_link: Optional[str] = None
    ai_summary: Optional[str] = None  # AI-generated professional summary

    def __str__(self) -> str:
        return f"Candidate(name={self.name}, email={self.email}, skills={self.skills}, phone={self.phone}, resume_link={self.resume_link}, experience={self.experience}, education={self.education})"
