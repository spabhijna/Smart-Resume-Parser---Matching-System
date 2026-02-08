smart-hiring-assistant/
│
├── README.md
├── pyproject.toml          # or requirements.txt
├── .gitignore
│
├── data/
│   ├── resumes/            # raw input resumes (.txt)
│   ├── jobs/               # job descriptions (JSON)
│   ├── outputs/            # generated reports + scores
│   └── samples/            # controlled test inputs
│
├── src/
│   ├── main.py              # entry point (pipeline orchestration)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── candidate.py     # Candidate dataclass
│   │   └── job.py           # JobRequirement dataclass
│   │
│   ├── parsing/
│   │   ├── __init__.py
│   │   ├── resume_parser.py # regex + heuristic parsing
│   │   └── skill_bank.py    # known skills list
│   │
│   ├── matching/
│   │   ├── __init__.py
│   │   └── matcher.py       # scoring logic
│   │
│   ├── reporting/
│   │   ├── __init__.py
│   │   └── report_generator.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── prompts.py       # prompt templates only
│   │   └── ai_helpers.py    # AI calls + post-processing
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── file_manager.py  # save/load JSON
│   │
│   └── utils/
│       ├── __init__.py
│       └── text_utils.py    # reusable string helpers
│
├── tests/
│   ├── test_parsing.py
│   ├── test_matching.py
│   └── test_reporting.py
│
└── docs/
    ├── architecture.md
    ├── scoring_logic.md
    └── prompt_design.md
