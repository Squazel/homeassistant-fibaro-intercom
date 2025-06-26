# GitHub Workflows

This repository includes several GitHub Actions workflows for continuous integration and deployment.

## Workflows Overview

### 1. Tests (`tests.yml`)
- **Triggers**: Push to main/master, pull requests
- **Matrix**: Python 3.11, 3.12, 3.13
- **Steps**:
  - Code quality checks (flake8, black, isort)
  - Type checking with mypy
  - Unit tests with pytest
  - Coverage reporting to Codecov
  - Integration structure validation

### 2. HACS Validation (`hacs.yml`)
- **Triggers**: Push, pull requests, daily schedule
- **Purpose**: Validates integration for HACS compatibility
- **Uses**: Official HACS action

### 3. Home Assistant Validation (`hassfest.yml`)
- **Triggers**: Push, pull requests, daily schedule
- **Purpose**: Validates integration with Home Assistant's hassfest tool
- **Uses**: Official Home Assistant action

### 4. CodeQL Security Analysis (`codeql.yml`)
- **Triggers**: Push to main/master, pull requests, weekly schedule
- **Purpose**: Static security analysis
- **Language**: Python

## Workflow Status Badges

The README.md includes status badges for all workflows:

```markdown
[![Tests](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/tests.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/tests.yml)
[![HACS](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hacs.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hacs.yml)
[![hassfest](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hassfest.yml)
[![CodeQL](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/codeql.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/codeql.yml)
```

## Quality Gates

The workflows enforce several quality gates:

1. **Code Style**: Black formatting and isort import sorting
2. **Code Quality**: flake8 linting with specific error checks
3. **Type Safety**: mypy type checking (warnings only)
4. **Test Coverage**: pytest with coverage reporting
5. **Integration Validation**: HACS and hassfest compatibility
6. **Security**: CodeQL static analysis

## Coverage Reporting

- **Tool**: pytest-cov
- **Target**: Client module (core business logic)
- **Report**: Uploaded to Codecov for tracking
- **Current**: ~69% coverage

## Local Development

Before pushing, run these commands locally to match CI:

```bash
# Format code
black custom_components/ tests/
isort custom_components/ tests/

# Lint
flake8 custom_components/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Type check
mypy custom_components/fibaro_intercom/

# Test
cd custom_components/fibaro_intercom
python -m pytest ../../tests/ -v --cov=client --cov-report=term-missing
```

## Release Process

1. Update version in `manifest.json`
2. Create a GitHub release with detailed release notes
3. Optionally add automated release workflows later if needed

## HACS Integration

The repository is structured for HACS compatibility:

- `DESCRIPTION.md`: HACS integration description
- `manifest.json`: Home Assistant integration manifest
- Proper directory structure under `custom_components/`
- GitHub releases (manual for now)
- HACS validation workflow

## Documentation Structure

- **`README.md`**: User-facing documentation
- **`DESCRIPTION.md`**: HACS integration description  
- **`tests/README.md`**: Development and testing guide
- **`.github/WORKFLOWS.md`**: This file - CI/CD documentation

## Security

- CodeQL scans for security vulnerabilities
- Dependency updates can be managed via Dependabot (if configured)
- All workflows use pinned action versions for security
