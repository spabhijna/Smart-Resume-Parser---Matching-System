import re
from datetime import datetime
import spacy
from spacy.matcher import Matcher
from typing import List, Optional
from src.models.candidate import Candidate

nlp = spacy.load("en_core_web_sm")

def get_email(text: str) -> List[str]:
    return re.findall(r'[\w\.-]+@[\w\.-]+', text)

def get_phone_number(text: str) -> List[str]:
    phone_pattern = r"(\+?\d[\d\s\-\(\)]{8,}\d)"
    phones = re.findall(phone_pattern, text)
    return [re.sub(r"\D", "", p) for p in phones]

def extract_name(text: str) -> Optional[str]:
    doc = nlp(text[:300])  # only top of resume
    matcher = Matcher(nlp.vocab)
    matcher.add("NAME", [[{"POS": "PROPN"}, {"POS": "PROPN"}]])

    matches = matcher(doc)
    for _, start, end in matches:
        return doc[start:end].text
    return None

SKILLS_DB = {
    "python", "java", "c++", "sql", "mongodb", "mysql",
    "machine learning", "deep learning", "nlp",
    "natural language processing", "computer vision",
    "tensorflow", "pytorch", "django", "flask",
    "html", "css", "javascript", "github", "git"
}

def extract_skills(text: str) -> List[str]:
    doc = nlp(text.lower())
    found = set()

    for chunk in doc.noun_chunks:
        if chunk.text in SKILLS_DB:
            found.add(chunk.text)

    for token in doc:
        if token.text in SKILLS_DB:
            found.add(token.text)

    return sorted(found)

DEGREE_MAP = {
    "BSC": ["BACHELOR OF SCIENCE", "B.SC", "BSC"],
    "MSC": ["MASTER OF SCIENCE", "M.SC", "MSC"],
    "BTECH": ["BACHELOR OF TECHNOLOGY", "B.TECH", "BTECH"],
    "MTECH": ["MASTER OF TECHNOLOGY", "M.TECH", "MTECH"],
    "MBA": ["MASTER OF BUSINESS ADMINISTRATION", "MBA"],
    "PHD": ["PHD", "PH.D", "DOCTORATE"]
}

def normalize_degree(line: str) -> Optional[str]:
    clean = re.sub(r"[.,]", "", line.upper())
    for canon, aliases in DEGREE_MAP.items():
        for a in aliases:
            if a in clean:
                return canon
    return None

def extract_education_section(text: str) -> str:
    lines = text.splitlines()
    result = []
    capture = False

    for line in lines:
        if re.search(r"\bEDUCATION|ACADEMIC\b", line, re.I):
            capture = True
            continue
        if capture and re.match(r"^[A-Z\s]{3,}$", line) and "UNIVERSITY" not in line:
            break
        if capture:
            result.append(line)

    return "\n".join(result)

def extract_education(text: str) -> List[dict]:
    section = extract_education_section(text)
    lines = [l.strip() for l in section.splitlines() if l.strip()]
    results = []

    for i, line in enumerate(lines):
        degree = normalize_degree(line)
        if degree:
            year = None
            for j in range(i, min(i + 3, len(lines))):
                m = re.search(r"(19|20)\d{2}", lines[j])
                if m:
                    year = m.group()
                    break
            results.append({
                "degree": degree,
                "raw": line,
                "year": year
            })
    return results

DATE_PATTERN = re.compile(r"(19|20)\d{2}.*?(PRESENT|CURRENT|(19|20)\d{2})", re.I)

def extract_experience_section(text: str) -> str:
    lines = text.splitlines()
    result = []
    capture = False

    for line in lines:
        if re.search(r"\b(EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE)\b", line, re.I):
            capture = True
            continue
        if capture and re.match(r"^[A-Z\s]{3,}$", line):
            break
        if capture:
            result.append(line)

    return "\n".join(result)

def extract_experience(text: str) -> List[dict]:
    section = extract_experience_section(text)
    lines = [l.strip() for l in section.splitlines() if l.strip()]

    experiences = []
    current = None

    for line in lines:
        if DATE_PATTERN.search(line):
            if current:
                experiences.append(current)
            current = {
                "header": line,
                "responsibilities": []
            }
        elif current and line.startswith(("-", "•", "*")):
            current["responsibilities"].append(line.lstrip("-•* ").strip())

    if current:
        experiences.append(current)

    return experiences

YEAR_PATTERN = re.compile(r"(?:19|20)\d{2}")

def compute_total_experience(experiences):
    total = 0
    current_year = datetime.now().year

    for exp in experiences:
        years = YEAR_PATTERN.findall(exp["header"])
        if not years:
            continue

        start = int(years[0])
        if re.search(r"PRESENT|CURRENT", exp["header"], re.I):
            end = current_year
        else:
            end = int(years[-1])

        # guard against bad data
        if end >= start:
            total += end - start

    return total

def parse_resume(text: str) -> Candidate:
    name = extract_name(text) or "Unknown"

    emails = get_email(text)
    phones = get_phone_number(text)

    skills = extract_skills(text)
    education = extract_education(text)

    experience_blocks = extract_experience(text)
    experience_years = compute_total_experience(experience_blocks)

    return Candidate(
        name=name,
        email=emails[0] if emails else None,
        phone=phones[0] if phones else None,
        skills=skills,
        education=education,
        experience=experience_years,
        resume_link=None
    )