#!/usr/bin/env python3
"""
Main CLI dispatcher for Resume Parser.

Usage:
    python -m src.cli batch              # Run batch pipeline
    python -m src.cli analyze <resume>   # Analyze single resume
"""

import sys


def print_help():
    """Display help message with available commands."""
    print("""
Resume Parser - Command Line Interface

Usage:
    python -m src.cli batch                 Process all resumes (batch pipeline)
    python -m src.cli analyze <resume>      Analyze a single resume

Commands:
    batch       Run batch pipeline - process all resumes against all jobs
                Generates reports, collects feedback, provides AI suggestions
    
    analyze     One-on-one analysis - deep dive into single candidate
                Args: <resume> - path to resume text file
                Example: python -m src.cli analyze data/resumes/candidate.txt
    
    help        Show this help message

For more information, see:
    - README.md for project overview
    - docs/ANALYZER_README.md for analyze command details
    """)


def main():
    """Main entry point for CLI dispatcher."""
    if len(sys.argv) < 2:
        print("Error: No command specified.\n")
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command in ["help", "-h", "--help"]:
        print_help()
        sys.exit(0)

    elif command == "batch":
        # Import and run batch pipeline
        from src.cli.batch_pipeline import main as batch_main

        sys.exit(batch_main() or 0)

    elif command == "analyze":
        # Import and run one-on-one analyzer
        from src.cli.analyze_one import main as analyze_main

        sys.exit(analyze_main() or 0)

    else:
        print(f"Error: Unknown command '{command}'.\n")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
