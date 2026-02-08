# One-on-One Resume Analyzer

A focused tool for analyzing a single candidate's resume against a specific job posting. Provides detailed skill gap analysis, experience matching, and AI-powered insights.

## Features

- 📄 **Resume Parsing**: Extract structured data from text resumes
- 🤖 **AI Profile Summary**: Get professional candidate summaries (if API key configured)
- 📊 **Detailed Match Analysis**: Visual breakdowns with skill gap identification
- 💡 **Smart Recommendations**: Interview decisions based on match scores
- 💾 **Save Reports**: Export detailed JSON analysis for record-keeping

## Quick Start

### Interactive Mode
```bash
python analyze_candidate.py
```
Follow the prompts to:
1. Enter resume file path
2. Select job posting (1-3)
3. Review detailed analysis
4. Optionally save report

### Direct Mode (Skip Resume Prompt)
```bash
python analyze_candidate.py data/resumes/Dr_Sarah_Chen_resume.txt
```
You'll only need to select the job number.

## Example Usage

```bash
$ python analyze_candidate.py data/resumes/Alex_Rivera_resume.txt

======================================================================
 ONE-ON-ONE RESUME ANALYZER
======================================================================

Available jobs:

   1. Machine Learning Engineer
   2. Junior Web Developer
   3. Engineering Manager

Select job number (1-3):
Job: 1

======================================================================
 ONE-ON-ONE RESUME ANALYSIS
======================================================================

📄 Step 1: Parsing Resume...
   File: data/resumes/Alex_Rivera_resume.txt
   ✓ Parsed: Alex Rivera
   ✓ Experience: 9 years
   ✓ Skills: 10 identified

🤖 Step 2: Generating AI Profile Summary...
   Alex Rivera is a highly accomplished Senior Software Engineer with nine 
   years of progressive experience, demonstrating a clear trajectory toward 
   a Lead or Architect role. His core technical strengths center on modern 
   backend development using Python (FastAPI) and robust database integration.

💼 Step 3: Matching Against Job: Machine Learning Engineer
   Company: NeuralNet Labs
   Location: San Francisco (Hybrid)

📊 Match Results:
   ──────────────────────────────────────────────────────────────────
   Overall Score: 0.56 (Potential Fit)
   ──────────────────────────────────────────────────────────────────

   Component Breakdown:
   required             [████████████████░░░░░░░░░░░░░░] 0.55
   preferred            [██████░░░░░░░░░░░░░░░░░░░░░░░░] 0.25
   experience           [██████████████████████████████] 0.86
   education            [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.00

   📅 Experience Analysis:
   ✓ Within range: 9 years (range 3-7)

   🎯 Hard Required Skills (1/1):
   ✓ Matched: python

   🔧 Soft Required Skills (1/4):
   ✓ Matched: sql
   ⚠️  Missing: pytorch, tensorflow, scikit-learn

   ⭐ Preferred Skills (1/4):
   ✓ Matched: docker
   • Not Found: kubernetes, huggingface, cuda

🤖 AI Match Explanation:
   ──────────────────────────────────────────────────────────────────
   This candidate has strong backend engineering fundamentals with 9 years 
   of experience and Python proficiency. However, they lack the critical ML 
   frameworks (PyTorch, TensorFlow) required for this role. Strong systems 
   and cloud experience could translate well, but would need significant 
   ramp-up time in ML-specific tools. Consider for backend-heavy ML 
   infrastructure roles rather than pure ML engineering.

======================================================================
💡 RECOMMENDATION:

   ⚠️  POTENTIAL FIT - Consider with Reservations
   → Review missing requirements carefully
   → Key gaps: pytorch, tensorflow, scikit-learn
   → May need additional training/support
======================================================================

Save detailed analysis to file? (y/n):
```

## Match Score Interpretation

| Score Range | Match Level | Recommendation |
|-------------|-------------|----------------|
| **0.85+** | 🌟 Strong Candidate | Schedule interview immediately |
| **0.70 - 0.84** | ✅ Good Fit | Recommended for interview |
| **0.50 - 0.69** | ⚠️ Potential Fit | Consider with reservations |
| **< 0.50** | ❌ Weak Match | Not recommended |

## Output Components

### 1. Resume Parsing
- Extracts candidate name, experience years, skills
- Identifies education background
- Uses spaCy NLP and regex patterns

### 2. AI Profile Summary
- Professional career trajectory analysis
- Key strengths and specializations
- Leadership potential assessment
- **Requires**: Valid `GEMINI_API_KEY` in `.env`

### 3. Match Results
Visual breakdown with progress bars:
- **Required Skills Score**: Hard + soft requirements (60% weight)
- **Preferred Skills Score**: Nice-to-have skills (15% weight)
- **Experience Score**: Years of experience match (15% weight)
- **Education Score**: Degree requirements (10% weight)

### 4. Skill Gap Analysis
Detailed breakdown of:
- ✓ **Matched Hard Required**: Critical skills candidate has
- ✗ **Missing Hard Required**: Critical gaps (major concern)
- ✓ **Matched Soft Required**: Important skills candidate has
- ⚠️ **Missing Soft Required**: Important gaps (minor concern)
- ✓ **Matched Preferred**: Bonus skills candidate has
- • **Missing Preferred**: Nice-to-have not found

### 5. AI Match Explanation
Human-readable explanation of:
- Why the score makes sense
- Key strengths for the role
- Critical gaps or concerns
- Overall suitability assessment

### 6. Hiring Recommendation
Clear action items based on match quality:
- Interview scheduling recommendation
- Training/support needs
- Alternative role considerations

## Saved Reports

When you choose to save, a JSON file is created in `src/storage/` with:

```json
{
  "candidate_name": "Alex Rivera",
  "job_title": "Machine Learning Engineer",
  "score": 0.56,
  "match_level": "Potential Fit",
  "breakdown": {
    "required": 0.55,
    "preferred": 0.25,
    "experience": 0.86,
    "education": 0.0
  },
  "skill_analysis": {
    "matched_hard": ["python"],
    "missing_hard": [],
    "matched_soft": ["sql"],
    "missing_soft": ["pytorch", "tensorflow", "scikit-learn"],
    "matched_preferred": ["docker"],
    "missing_preferred": ["kubernetes", "huggingface", "cuda"]
  },
  "candidate_summary": "AI-generated professional summary...",
  "timestamp": "2026-02-08T14:30:00"
}
```

## Available Jobs

Currently configured jobs (see `data/jobs/Jobs.py`):

1. **Machine Learning Engineer** @ NeuralNet Labs
   - Focus: NLP and Computer Vision
   - Experience: 3-7 years
   - Key Skills: Python, PyTorch, TensorFlow

2. **Junior Web Developer** @ GreenSeed Startups  
   - Focus: Frontend + simple backends
   - Experience: 0-2 years
   - Key Skills: Python, HTML, CSS, JavaScript

3. **Engineering Manager** @ Global Fintech
   - Focus: Team leadership (10 engineers)
   - Experience: 8+ years
   - Key Skills: System Design, Project Management

## Adding Custom Jobs

To analyze against your own job posting, edit `data/jobs/Jobs.py`:

```python
from src.models.job import Job

custom_job = Job(
    title="Your Job Title",
    company="Company Name",
    location="Location",
    description="Job description...",
    hard_required_skills=["Python", "SQL"],  # Must-haves
    soft_required_skills=["Docker", "AWS"],  # Important but flexible
    preferred_skills=["Kubernetes"],         # Nice-to-haves
    min_experience=3,
    max_experience=7,
    role_type="IC_SENIOR"  # or "IC", "LEADERSHIP"
)
```

Then add it to the `jobs` dictionary in `analyze_candidate.py`.

## Troubleshooting

### "No module named 'spacy'"
```bash
uv pip install spacy
python -m spacy download en_core_web_sm
```

### "AI features disabled"
- Check if `GEMINI_API_KEY` is set in `.env`
- Get free API key: https://makersuite.google.com/app/apikey
- Analyzer works without AI, just won't show summaries/explanations

### "429 Quota exceeded"
- Free tier: 20 requests/day
- Wait 24 hours or upgrade API plan
- Core matching still works, just no AI insights

## Tips for Best Results

1. **Resume Format**: Use clear section headers (Experience, Education, Skills)
2. **Skills**: Mention technologies explicitly in resume text
3. **Experience**: Include years or date ranges for work history
4. **Multiple Analyses**: Compare same candidate against different jobs
5. **Save Reports**: Keep JSON files for tracking/comparison over time

## Integration with Main Pipeline

This tool complements the main pipeline (`src/main.py`):
- **Main Pipeline**: Batch process multiple resumes against multiple jobs
- **This Tool**: Deep dive into one candidate-job pair

Both use the same:
- Parsing logic
- Matching algorithm
- AI service
- Scoring system

## Performance

- Parsing: < 1 second
- Matching: Instant (rule-based)
- AI Summary: 1-3 seconds (if enabled)
- AI Explanation: 2-4 seconds (if enabled)

**Total**: ~5-10 seconds with AI, < 2 seconds without

---

**Pro Tip**: Run without AI for quick screening, then enable AI for top candidates you want detailed insights on!
