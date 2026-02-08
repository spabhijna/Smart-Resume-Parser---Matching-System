# Smart Resume Parser & Matching System

> An AI-enhanced resume parser that extracts structured data, matches candidates to jobs, and provides human-readable insights for recruiters.

## 🎯 Features

- **Resume Parsing**: Extract names, emails, skills, experience, and education from text resumes
- **Smart Matching**: Score candidates against job requirements using configurable rules
- **AI Insights**: Get human-readable explanations of scores and candidate profiles
- **Feedback Loop**: Collect recruiter feedback and receive AI-powered improvement suggestions
- **Reporting**: Generate detailed JSON reports with match scores and recommendations
- **Extensible**: Modular architecture makes it easy to add new features

## � Two Modes of Operation

### 1️⃣ Batch Pipeline (Process Multiple Resumes)
Best for: Initial screening of many candidates
```bash
uv run python -m src.main
```

### 2️⃣ One-on-One Analyzer (Deep Dive Single Candidate)
Best for: Detailed analysis of shortlisted candidates
```bash
python analyze_candidate.py data/resumes/candidate.txt
```
📖 See [ANALYZER_README.md](ANALYZER_README.md) for detailed usage

## �🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Resume-Parser

# Install dependencies
pip install -e .
```

### 2. Configure AI Integration (Optional)

Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey) and add it to `.env`:

```bash
# Copy the template
cp .env.template .env

# Edit .env and add your API key
GEMINI_API_KEY=your-actual-api-key-here
```

**Note**: The system works without AI, but you'll miss out on:
- Professional candidate summaries
- Match explanations
- Feedback analysis and improvement suggestions

### 3. Run the Pipeline

```bash
python -m src.main
```

Or using uv:

```bash
uv run python -m src.main
```

## 📁 Project Structure

smart-hiring-assistant/
│
├── README.md
├── pyproject.toml          # Dependencies and project config
├── .env                    # Environment variables (API keys)
├── .env.template           # Template for environment setup
├── .gitignore
│
├── data/
│   ├── resumes/            # Raw input resumes (.txt)
│   └── jobs/               # Job descriptions (JobRequirement objects)
│
├── src/
│   ├── main.py              # Pipeline orchestration
│   ├── config.py            # AI configuration management
│   │
│   ├── models/              # Data models
│   │   ├── candidate.py     # Candidate dataclass
│   │   ├── job.py           # Job dataclass
│   │   └── match_config.py  # Matching configuration
│   │
│   ├── parsing/             # Resume parsing
│   │   └── parser.py        # ResumeParser class (regex + spaCy)
│   │
│   ├── matching/            # Candidate matching
│   │   └── matcher.py       # RuleBasedCandidateMatcher
│   │
│   ├── reporting/           # Report generation
│   │   └── report_generator.py
│   │
│   ├── ai/                  # AI integration (NEW!)
│   │   ├── ai_service.py    # HiringAIAssistant class
│   │   └── prompts.py       # Prompt templates
│   │
│   ├── storage/             # JSON output files
│   └── utils/               # Helper utilities
│
└── tests/
    ├── test_parser.py
    ├── test_matching.py
    └── test_ai_service.py   # AI service tests (with mocking)

## 🤖 AI Integration

### What AI Adds

The AI integration enhances the rule-based system with **human-readable explanations**. It doesn't make hiring decisions — it explains the decisions your rules make.

#### 1. **Candidate Summaries** (After Parsing)

**When**: After parsing each resume  
**Purpose**: Generate a professional summary highlighting strengths and specializations

**Example Output**:
```
💡 AI Summary: Senior systems architect with 18 years of experience in cloud 
infrastructure and distributed systems. Deep expertise in AWS, Kubernetes, and 
Python. Strong leadership background with proven ability to mentor teams. May 
require ramp-up time for hands-on ML frameworks.
```

#### 2. **Match Explanations** (After Matching)

**When**: After scoring each candidate against a job  
**Purpose**: Explain why the score makes sense and what's missing

**Example Output**:
```
💡 AI Explanation: This candidate meets all hard requirements and exceeds the 
experience expectation with 18 years vs. 8+ required. Deep systems expertise 
aligns well with the engineering manager role. Some ML frameworks are missing 
but these are soft requirements. Candidate demonstrates strong leadership 
through project management skills. Overall, this is a strong match suitable 
for interview consideration.
```

#### 3. **Feedback Analysis** (After Collection)

**When**: After collecting recruiter feedback on top candidates  
**Purpose**: Identify patterns and suggest rule improvements

**Example Output**:
```
🎯 AI RECOMMENDATIONS FOR MATCHING SYSTEM:

1. Consider grouping ML frameworks (PyTorch, TensorFlow, Keras) under a single 
   soft requirement for senior candidates, as they're largely interchangeable.

2. Reduce penalty for missing specific frameworks when distributed systems 
   experience is present, especially for leadership roles.

3. Reclassify "System Design" from hard required to soft required for IC roles, 
   as it's often learned on the job.
```

### AI Integration Points in Pipeline

```python
# 1. After Parsing → Generate candidate summary
candidate = parser.parse(resume_text)
candidate.ai_summary = ai_assistant.summarize_candidate(candidate)

# 2. After Matching → Explain the score
match_result = matcher.match(candidate, job)
ai_explanation = ai_assistant.explain_match(
    candidate, job, match_result['score'], match_result['breakdown']
)

# 3. After Display → Collect feedback
feedback = collect_feedback_for_job(report)

# 4. End of Pipeline → Analyze feedback
suggestions = ai_assistant.suggest_refinements(feedback_batch)
```

### How to Use Feedback Loop

1. Run the pipeline: `python -m src.main`
2. After displaying top candidates, you'll be prompted:
   ```
   Would you like to provide feedback on candidates? (y/n): y
   ```
3. For each top candidate:
   ```
   1. Dr. Sarah Chen - Score: 0.82
      Decision (interview/pass/skip): interview
      Notes (optional): Strong systems thinker, ML concepts solid
   ```
4. AI analyzes patterns and suggests improvements
5. Suggestions are saved to `src/storage/ai_suggestions.txt`

### Philosophy: AI Explains, Humans Decide

- ✅ AI provides insights and explanations
- ✅ AI identifies patterns in feedback
- ✅ AI suggests improvements
- ❌ AI does NOT change your matching rules
- ❌ AI does NOT make hiring decisions
- ❌ AI does NOT auto-learn without human approval

**You remain in control.** Review AI suggestions and manually update configuration if they make sense.

## 🔧 Configuration

### Matching Configuration

Edit matching behavior in [src/models/match_config.py](src/models/match_config.py):

```python
@dataclass
class MatchConfig:
    # Component weights (must sum to 1.0)
    required_weight: float = 0.60   # Hard + soft required skills
    preferred_weight: float = 0.15  # Nice-to-have skills
    experience_weight: float = 0.15 # Years of experience
    education_weight: float = 0.10  # Degree matching
    
    # Skill penalties
    required_decay: float = 0.7     # Penalty per missing required skill
    min_required_floor: float = 0.2 # Minimum score floor
```

### AI Configuration

Edit AI behavior in `.env`:

```bash
GEMINI_API_KEY=your-api-key-here
AI_MODEL=gemini-flash-latest          # Latest stable flash model (recommended)
# AI_MODEL=gemini-2.5-flash          # Specific version
# AI_MODEL=gemini-pro-latest         # More capable, slower
AI_MAX_TOKENS=2000                 # Max response length
AI_TEMPERATURE=0.7                 # Creativity (0.0-1.0)
```

## 🧪 Testing

Run all tests:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/test_ai_service.py -v
```

**AI Tests**: All AI tests use mocking to avoid real API calls. No API key needed for testing.

## 📊 Adding New Resumes & Jobs

### Add a Resume

1. Create a `.txt` file in `data/resumes/`
2. Format with clear sections: Experience, Education, Skills
3. Run the pipeline — it will auto-detect and parse

### Add a Job

1. Edit `data/jobs/Jobs.py`
2. Create a new `Job` object:

```python
new_job = Job(
    title="Senior Backend Engineer",
    company="TechCorp",
    location="Remote",
    description="Build scalable APIs...",
    hard_required_skills=["Python", "SQL"],
    soft_required_skills=["Docker", "AWS"],
    preferred_skills=["Kubernetes", "Redis"],
    min_experience=5,
    role_type="IC_SENIOR"
)
```

3. Run the pipeline — it will match all candidates against the new job

## 🎓 Learning Outcomes

This project demonstrates:

✅ **File Handling**: Reading resumes, saving JSON reports  
✅ **String Operations**: Regex parsing, text extraction  
✅ **Data Types**: Dataclasses, lists, dictionaries  
✅ **Operators**: Scoring calculations, set operations  
✅ **Conditionals**: Rule-based matching logic  
✅ **Loops**: Processing multiple candidates/jobs  
✅ **AI Integration**: Prompt engineering, graceful degradation  
✅ **Testing**: Unit tests with mocking  
✅ **Project Structure**: Modular, maintainable architecture

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **spaCy** for NLP capabilities
- **Google Gemini** for AI-powered insights
- **Python** for being awesome

---

**Built with ❤️ as a learning project combining Python fundamentals with modern AI integration.**
