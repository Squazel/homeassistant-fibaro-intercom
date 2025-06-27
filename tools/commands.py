#!/usr/bin/env python3
"""
Centralized development commands for FIBARO Intercom integration

This script defines the canonical commands for all development tasks.
All other tools (dev CLI, pre-commit, CI/CD) should call these functions
to ensure consistency across environments.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_emoji(emoji: str, fallback: str) -> str:
    """Get emoji if supported, fallback otherwise."""
    # Check if we're in pre-commit (no emoji support)
    if os.environ.get('PRE_COMMIT'):
        return fallback

    # Check if we're in CI (usually no emoji support)
    if os.environ.get('CI'):
        return fallback

    # Try to encode the emoji to see if it's supported
    try:
        emoji.encode(sys.stdout.encoding or 'utf-8')
        return emoji
    except (UnicodeEncodeError, LookupError):
        return fallback


def run_command(cmd: str, description: str, cwd: Optional[Path] = None) -> bool:
    """Run a command and print the result."""
    print(f"\n{get_emoji('🔄', '>')} {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=cwd
        )
        if result.stdout.strip():
            print(result.stdout)
        print(f"{get_emoji('✅', '[OK]')} {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{get_emoji('❌', '[FAIL]')} {description} failed:")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def format_code() -> bool:
    """Format code with ruff (using pyproject.toml config)."""
    print(f"{get_emoji('🎨', '*')} Formatting code...")
    success = True
    success &= run_command("ruff format custom_components/ tests/", "Ruff formatting")
    success &= run_command("ruff check --fix custom_components/ tests/", "Ruff import sorting & auto-fixes")
    return success


def lint_code(strict: bool = False) -> bool:
    """Run linting checks (using pyproject.toml config)."""
    print(f"{get_emoji('🔍', '?')} Running linting checks...")
    success = True

    # Always run ruff linting
    success &= run_command("ruff check custom_components/ tests/", "Ruff linting")

    # MyPy type checking - allow failures in non-strict mode for Home Assistant integrations
    if strict:
        success &= run_command("mypy custom_components/fibaro_intercom/", "MyPy type checking (strict)")
    else:
        print(f"\n{get_emoji('🔄', '>')} MyPy type checking (advisory)...")
        try:
            result = subprocess.run(
                "mypy custom_components/fibaro_intercom/",
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.stdout.strip():
                print(result.stdout)
            if result.returncode == 0:
                print(f"{get_emoji('✅', '[OK]')} MyPy type checking completed successfully")
            else:
                print(f"{get_emoji('⚠️', '[WARN]')} MyPy found type issues (expected for Home Assistant integrations)")
        except Exception as e:
            print(f"{get_emoji('⚠️', '[WARN]')} MyPy check failed: {e}")

    return success


def run_tests() -> bool:
    """Run the test suite (using pyproject.toml config)."""
    print(f"{get_emoji('🧪', 'T')} Running tests...")
    # Run from the correct directory to ensure coverage works
    project_root = Path(__file__).parent.parent
    return run_command("python -m pytest", "Test suite", cwd=project_root)


def setup_environment() -> bool:
    """Set up the development environment."""
    print(f"{get_emoji('🚀', '^')} Setting up FIBARO Intercom development environment...")

    success = True

    # Install development dependencies
    success &= run_command('pip install -e ".[dev]"', "Installing development dependencies")

    # Install pre-commit hooks
    success &= run_command("pre-commit install", "Installing pre-commit hooks")

    return success


def quality_check(strict: bool = False) -> bool:
    """Run code quality checks (no tests)."""
    print(f"{get_emoji('🔍', '?')} Running code quality checks...")
    success = True
    success &= format_code()
    success &= lint_code(strict=strict)
    return success


def full_check(strict: bool = False) -> bool:
    """Run all checks (format, lint, test)."""
    print(f"{get_emoji('🚀', '^')} Running all checks...")
    success = True
    success &= format_code()
    success &= lint_code(strict=strict)
    success &= run_tests()
    return success


if __name__ == "__main__":
    # Allow this script to be called directly
    if len(sys.argv) < 2:
        print("""
Usage: python commands.py <action> [options]

Actions:
  format       - Format code with ruff
  lint         - Run linting checks
  lint-strict  - Run linting checks (fail on type errors)
  test         - Run test suite
  setup        - Set up development environment
  quality      - Run format + lint (no tests)
  check        - Run all checks (format + lint + test)
  check-strict - Run all checks with strict type checking
        """)
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "format":
        success = format_code()
    elif action == "lint":
        success = lint_code(strict=False)
    elif action == "lint-strict":
        success = lint_code(strict=True)
    elif action == "test":
        success = run_tests()
    elif action == "setup":
        success = setup_environment()
    elif action == "quality":
        success = quality_check(strict=False)
    elif action == "check":
        success = full_check(strict=False)
    elif action == "check-strict":
        success = full_check(strict=True)
    else:
        print(f"{get_emoji('❌', '[FAIL]')} Unknown action: {action}")
        sys.exit(1)

    sys.exit(0 if success else 1)
