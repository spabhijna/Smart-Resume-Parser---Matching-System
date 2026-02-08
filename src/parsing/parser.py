import re
from datetime import datetime
from typing import List, Optional

import spacy
from spacy.matcher import Matcher

from src.models.candidate import Candidate


class ResumeParser:
    DATE_PATTERN = re.compile(
        r"(?P<start>(19|20)\d{2})\s*[-–to]+\s*(?P<end>PRESENT|CURRENT|(19|20)\d{2})",
        re.I,
    )

    YEAR_PATTERN = re.compile(r"(?:19|20)\d{2}")

    SKILLS_DB = {
        # Languages
        "python", "java", "c++", "go",

        # Web / Backend
        "django", "flask", "fastapi",

        # ML / AI
        "machine learning", "deep learning", "nlp",
        "computer vision", "tensorflow", "pytorch", "scikit-learn",

        # Data
        "sql", "nosql", "mongodb", "mysql",

        # Cloud / Infra
        "docker", "kubernetes", "terraform",
        "aws", "gcp", "azure",

        # Engineering concepts
        "system design", "distributed systems",
        "microservices", "architecture",

        # Process / leadership
        "project management", "agile", "mentorship",

        # Tools
        "git", "github",
    }


    DEGREE_MAP = {
        "BSC": ["BACHELOR OF SCIENCE", "B.SC", "BSC"],
        "MSC": ["MASTER OF SCIENCE", "M.SC", "MSC"],
        "BTECH": ["BACHELOR OF TECHNOLOGY", "B.TECH", "BTECH"],
        "MTECH": ["MASTER OF TECHNOLOGY", "M.TECH", "MTECH"],
        "MBA": ["MASTER OF BUSINESS ADMINISTRATION", "MBA"],
        "PHD": ["PHD", "PH.D", "DOCTORATE"],
    }

    SECTION_HEADERS = {
        "experience": {"experience", "work experience", "professional experience"},
        "education": {"education", "academic"},
        "skills": {"skills", "technical skills"},
        "summary": {"summary", "profile"},
    }

    def __init__(self, model: str = "en_core_web_sm"):
        self.nlp = spacy.load(model)
        self.name_matcher = Matcher(self.nlp.vocab)
        self.name_matcher.add("NAME", [[{"POS": "PROPN"}, {"POS": "PROPN"}]])

    # ---------------------------
    # Public API
    # ---------------------------

    def parse(self, text: str) -> Candidate:
        self.text = text
        self.doc = self.nlp(text)
        self.sections = self._segment_resume()

        name = self._extract_name() or "Unknown"

        emails = self._get_email()
        phones = self._get_phone()

        skills = self._extract_skills()


        education = self._extract_education()

        experience_blocks = self._extract_experience()
        experience_years = self._compute_total_experience(experience_blocks)
        skills = self._extract_skills()

        # ---- Senior inference rules ----
        if experience_years >= 10:
            text_lower = text.lower()

            if any(k in text_lower for k in ["architect", "designed", "architecture"]):
                skills.append("system design")

            if any(k in text_lower for k in ["led", "managed", "director", "mentored"]):
                skills.append("project management")


        return Candidate(
            name=name,
            email=emails[0] if emails else None,
            phone=phones[0] if phones else None,
            skills=skills,
            education=education,
            experience=experience_years,
            resume_link=None,
        )

    # ---------------------------
    # NLP + Sectioning (ML-assisted)
    # ---------------------------

    def _segment_resume(self) -> dict:
        sections = {k: [] for k in self.SECTION_HEADERS}
        current = None

        for line in self.text.splitlines():
            clean = line.strip().lower()

            for section, aliases in self.SECTION_HEADERS.items():
                if clean in aliases:
                    current = section
                    break
            else:
                if current:
                    sections[current].append(line)

        return {k: "\n".join(v) for k, v in sections.items()}

    # ---------------------------
    # Name
    # ---------------------------

    def _extract_name(self) -> Optional[str]:
        # Rule-based first (top of resume)
        head = self.doc[:300]
        matches = self.name_matcher(head)

        for _, start, end in matches:
            return head[start:end].text

        # ML fallback
        for ent in self.doc.ents:
            if ent.label_ == "PERSON":
                return ent.text

        return None

    # ---------------------------
    # Contact
    # ---------------------------

    def _get_email(self) -> List[str]:
        return re.findall(r"[\w\.-]+@[\w\.-]+", self.text)

    def _get_phone(self) -> List[str]:
        phones = re.findall(r"(\+?\d[\d\s\-\(\)]{8,}\d)", self.text)
        return [re.sub(r"\D", "", p) for p in phones]

    # ---------------------------
    # Skills
    # ---------------------------

    def _extract_skills(self) -> List[str]:
        text = self.text.lower()
        found = set()

        for skill in self.SKILLS_DB:
            # whole-word or phrase match
            pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, text):
                found.add(skill)

        return sorted(found)


    # ---------------------------
    # Education
    # ---------------------------

    def _normalize_degree(self, line: str) -> Optional[str]:
        clean = re.sub(r"[.,]", "", line.upper())
        for canon, aliases in self.DEGREE_MAP.items():
            for a in aliases:
                if a in clean:
                    return canon
        return None

    def _extract_education(self) -> List[dict]:
        text = self.sections.get("education", "")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        results = []

        for i, line in enumerate(lines):
            degree = self._normalize_degree(line)
            if degree:
                year = None
                for j in range(i, min(i + 3, len(lines))):
                    m = re.search(r"(19|20)\d{2}", lines[j])
                    if m:
                        year = m.group()
                        break
                results.append({"degree": degree, "raw": line, "year": year})
        return results

    # ---------------------------
    # Experience
    # ---------------------------

    def _extract_experience(self) -> List[dict]:
        text = self.sections.get("experience", "")
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        experiences = []
        current = None

        for line in lines:
            date_match = self.DATE_PATTERN.search(line)

            if date_match:
                if current:
                    experiences.append(current)

                current = {
                    "header": line,
                    "start": date_match.group("start"),
                    "end": date_match.group("end"),
                    "responsibilities": [],
                }

            elif current and line.startswith(("-", "•", "*")):
                current["responsibilities"].append(line.lstrip("-•* ").strip())

        if current:
            experiences.append(current)

        return experiences

    def _compute_total_experience(self, experiences: List[dict]) -> int:
        intervals = []
        current_year = datetime.now().year

        for exp in experiences:
            years = self.YEAR_PATTERN.findall(exp["header"])
            if not years:
                continue

            start = int(years[0])
            if re.search(r"PRESENT|CURRENT", exp["header"], re.I):
                end = current_year
            else:
                end = int(years[-1])

            if end >= start:
                intervals.append((start, end))

        if not intervals:
            return 0

        # --- merge overlapping intervals ---
        intervals.sort()
        merged = [intervals[0]]

        for start, end in intervals[1:]:
            last_start, last_end = merged[-1]

            if start <= last_end:  # overlap or touch
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))

        # --- compute total ---
        total = sum(end - start for start, end in merged)
        return total
