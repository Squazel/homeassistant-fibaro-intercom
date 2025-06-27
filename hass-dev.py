#!/usr/bin/env python3
"""
FIBARO Intercom Development CLI

This is the main development interface for contributors.
All commands delegate to the centralized tools/commands.py script.
"""

import sys
from pathlib import Path

# Add tools directory to path so we can import commands
tools_dir = Path(__file__).parent / "tools"
sys.path.insert(0, str(tools_dir))

try:
    from commands import format_code, lint_code, run_tests, setup_environment, quality_check, full_check
except ImportError:
    print("❌ Could not import development commands.")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("""
🛠️  FIBARO Intercom Development CLI

Usage: python hass-dev <command>

Commands:
  setup        - Set up development environment (run this first!)
  format       - Format code with ruff
  lint         - Run linting checks (advisory mode)
  lint-strict  - Run linting checks (strict mode)
  test         - Run the test suite with pytest
  quality      - Run format + lint (no tests)
  check        - Run all checks (format + lint + test)
  check-strict - Run all checks with strict type checking

Examples:
  python hass-dev setup       # First-time setup
  python hass-dev format      # Just format the code
  python hass-dev quality     # Quick quality check (no tests)
  python hass-dev check       # Full check before committing

💡 Tip: Use 'quality' for quick feedback, 'check' before committing
        """)
        return

    command = sys.argv[1].lower()

    if command == "setup":
        success = setup_environment()
        if success:
            print("""
🎉 Development environment setup complete!

Next steps:
  python hass-dev quality  # Quick format + lint check
  python hass-dev check    # Full check including tests

All tool configurations are centralized in pyproject.toml
Pre-commit hooks will run automatically on commit
            """)
    elif command == "format":
        success = format_code()
    elif command == "lint":
        success = lint_code(strict=False)
    elif command == "lint-strict":
        success = lint_code(strict=True)
    elif command == "test":
        success = run_tests()
    elif command == "quality":
        success = quality_check(strict=False)
    elif command == "check":
        success = full_check(strict=False)
    elif command == "check-strict":
        success = full_check(strict=True)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: setup, format, lint, lint-strict, test, quality, check, check-strict")
        return

    if success:
        print(f"\n🎉 Command '{command}' completed successfully!")
    else:
        print(f"\n💥 Command '{command}' failed. Please fix the issues above.")


if __name__ == "__main__":
    main()
