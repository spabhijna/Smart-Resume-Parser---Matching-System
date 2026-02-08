#!/usr/bin/env python3
"""
Batch pipeline CLI - Process multiple resumes against multiple jobs.

Usage:
    python -m src.cli.batch_pipeline
"""

import sys
from pathlib import Path

from src.main import ResumeParserPipeline


def main():
    """
    Run the batch pipeline to process all resumes against all jobs.

    This command:
    1. Loads all resumes from data/resumes/
    2. Parses each resume to extract structured data
    3. Matches each candidate against all job postings
    4. Generates detailed reports with AI insights
    5. Collects recruiter feedback
    6. Provides AI-powered suggestions for improving the matching system
    """
    print("=" * 70)
    print("Resume Parser - Batch Pipeline")
    print("=" * 70)
    print()

    try:
        pipeline = ResumeParserPipeline()
        pipeline.run()

        print("\n" + "=" * 70)
        print("✓ Batch pipeline completed successfully")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
