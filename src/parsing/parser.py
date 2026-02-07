from src.models.candidate import Candidate
import re

def get_eamil(text: str) -> str | None:
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    r = re.compile(email_pattern)
    return r.findall(text)


def parse_resume(text: str) -> Candidate:
    pass