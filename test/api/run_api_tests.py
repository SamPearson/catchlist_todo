#!/usr/bin/env python
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime


def run_tests(args):
    # Add timestamp to report directory if not explicitly specified
    if args.report_dir == "./reports/allure-results":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        args.report_dir = f"./reports/allure-results-{timestamp}"
    
    # Construct base pytest command
    cmd = [
        "pytest",
        "--env=dev",
        "-v",
        #"-s", # This flag enables print statements, but is very spammy.
        f"--alluredir={args.report_dir}",
    ]

    # Add pytest markers if specified
    if args.markers:
        cmd.extend(["-m", args.markers])

    # Add any additional arguments passed to the script
    if args.pytest_args:
        cmd.extend(args.pytest_args)

    # Create reports directory if it doesn't exist
    Path(args.report_dir).mkdir(parents=True, exist_ok=True)

    # Run pytest
    try:
        result = subprocess.run(cmd)

        # If allure is requested, serve the report
        if not args.no_allure:
            print("\nTests passed! Opening Allure report...")
            subprocess.run(["allure", "serve", args.report_dir], shell=True)
        else:
            sys.exit(result.returncode)

    except FileNotFoundError as e:
        if 'allure' in str(e):
            print("Error: Allure command not found. Please ensure Allure is installed and in your PATH")
        elif 'pytest' in str(e):
            print("Error: pytest not found. Please ensure pytest is installed")
        else:
            raise
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run API tests with pytest and Allure reporting")
    parser.add_argument(
        "--report-dir",
        default="./reports/allure-results",
        help="Directory for Allure reports (default: ./reports/allure-results)"
    )
    parser.add_argument(
        "--no-allure",
        action="store_true",
        help="Don't open Allure report after test execution"
    )
    parser.add_argument(
        "-m", "--markers",
        help="Run tests matching given mark expression (e.g., 'smoke', 'not slow')"
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional arguments to pass to pytest"
    )

    args = parser.parse_args()
    run_tests(args)


if __name__ == "__main__":
    main()