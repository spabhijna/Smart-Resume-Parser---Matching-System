import pytest
from src.parsing.parser import parse_resume


# Example resume text fixture
@pytest.fixture
def example_resume():
    resume_path = 'data/resumes/test_resume_1.txt'

    with open(resume_path,'r') as file:
        content = file.read()
        return content


def test_parse_resume_basic(example_resume):
    """Test that parse_resume returns a valid Candidate object."""
    candidate = parse_resume(example_resume)
    assert candidate is not None


def test_parse_resume_name(example_resume):
    """Test that the candidate's name is parsed correctly."""
    candidate = parse_resume(example_resume)
    assert candidate.name == "John Smith"


def test_parse_resume_email(example_resume):
    """Test that the candidate's email is parsed correctly."""
    candidate = parse_resume(example_resume)
    assert candidate.email == "john.smith@email.com"


def test_parse_resume_phone(example_resume):
    """Test that the candidate's phone is parsed correctly."""
    candidate = parse_resume(example_resume)
    assert candidate.phone == "5551234567"


def test_parse_resume_skills(example_resume):
    """Test that the candidate's skills are parsed correctly."""
    candidate = parse_resume(example_resume)
    assert candidate.skills is not None
    assert len(candidate.skills) > 0
    assert "python" in candidate.skills
    assert "machine learning" in candidate.skills


def test_parse_resume_experience(example_resume):
    """Test that the candidate's experience is parsed correctly."""
    candidate = parse_resume(example_resume)
    assert candidate.experience is not None
    # The resume mentions 5+ years of experience
    assert candidate.experience >= 5


def test_parse_resume_education(example_resume):
    """Test that the candidate's education is parsed correctly."""
    candidate = parse_resume(example_resume)
    assert candidate.education is not None
    assert candidate.education[0]['degree'] == 'MSC'
    assert candidate.education[1]['degree'] == 'BSC' 
    assert candidate.education[0]['raw'] == 'Master of Science in Computer Science'
    assert candidate.education[1]['raw'] == 'Bachelor of Science in Computer Science'
    assert candidate.education[1]['year'] == '2016'
    assert candidate.education[0]['year'] == '2018'
    