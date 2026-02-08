from src.models.job import Job

ml_job = Job(
    title="Machine Learning Engineer",
    company="NeuralNet Labs",
    location="San Francisco (Hybrid)",
    description="Developing NLP and Computer Vision models for healthcare.",
    required_skills=["Python", "PyTorch", "TensorFlow", "SQL", "Scikit-Learn"],
    preferred_skills=["Docker", "Kubernetes", "HuggingFace", "CUDA"],
    min_experience=3,
    max_experience=7,
    min_salary=140000,
    max_salary=190000,
    education_keywords=["Master's", "PhD", "Computer Science", "Mathematics"],
)

junior_job = Job(
    title="Junior Web Developer",
    company="GreenSeed Startups",
    location="Remote",
    description="Maintaining frontend components and simple Python backends.",
    required_skills=["Python", "HTML", "CSS", "JavaScript"],
    preferred_skills=["Git", "Django", "Tailwind"],
    min_experience=0,
    max_experience=2,
    min_salary=60000,
    max_salary=85000,
    education_keywords=["Bachelor's", "Bootcamp"],
)

manager_job = Job(
    title="Engineering Manager",
    company="Global Fintech",
    location="New York",
    description="Leading a team of 10 backend engineers in the payments space.",
    required_skills=["Python", "System Design", "Project Management"],
    preferred_skills=["Agile", "Mentorship", "Fintech Experience", "AWS"],
    min_experience=8,
    max_experience=None,  # No upper limit for leadership
    min_salary=180000,
    max_salary=250000,
    education_keywords=["Business", "Computer Science", "Management"],
)
