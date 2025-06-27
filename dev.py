#!/usr/bin/env python3
"""
Development utility script for FIBARO Intercom integration
Provides shortcuts for common development tasks
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n🔄 {description}...")
    try:
        # Fix encoding issues on Windows
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def format_code():
    """Format code with black and isort."""
    print("🎨 Formatting code...")
    success = True
    success &= run_command("black custom_components/ tests/", "Black formatting")
    success &= run_command("isort custom_components/ tests/", "Import sorting")
    return success


def lint_code():
    """Run linting checks."""
    print("🔍 Running linting checks...")
    success = True
    success &= run_command(
        "flake8 custom_components/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics",
        "Flake8 syntax check"
    )
    success &= run_command(
        "flake8 custom_components/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
        "Flake8 style check"
    )
    return success


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    return run_command(
        "python -m pytest tests/ -v --cov=custom_components/fibaro_intercom --cov-report=term-missing",
        "Test suite"
    )


def check_all():
    """Run all checks (format, lint, test)."""
    print("🚀 Running all checks...")
    success = True
    success &= format_code()
    success &= lint_code()
    success &= run_tests()

    if success:
        print("\n🎉 All checks passed! Your code is ready to commit.")
    else:
        print("\n💥 Some checks failed. Please fix the issues above.")
    return success


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("""
🛠️  FIBARO Intercom Development Tool

Usage: python dev.py <command>

Commands:
  format    - Format code with black and isort
  lint      - Run linting checks with flake8
  test      - Run the test suite with pytest
  check     - Run all checks (format + lint + test)

Examples:
  python dev.py format    # Just format the code
  python dev.py check     # Run everything before committing
        """)
        return

    command = sys.argv[1].lower()

    if command == "format":
        format_code()
    elif command == "lint":
        lint_code()
    elif command == "test":
        run_tests()
    elif command == "check":
        check_all()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: format, lint, test, check")


if __name__ == "__main__":
    main()
