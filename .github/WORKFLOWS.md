# GitHub Workflows

This repository includes several GitHub Actions workflows for continuous integration and deployment.

## Workflows Overview

### 1. Code Quality (`quality.yml`)
- **Triggers**: Push to main/master, pull requests
- **Python**: 3.13 (single version for efficiency)
- **Steps**:
  - Ruff linting and formatting
  - MyPy type checking (advisory)
  - Code quality validation

### 2. Tests (`tests.yml`)
- **Triggers**: Push to main/master, pull requests
- **Matrix**: Python 3.11, 3.12, 3.13 (for compatibility testing)
- **Steps**:
  - Unit tests with pytest
  - Coverage reporting to Codecov
  - Integration structure validation (Python 3.13)

### 3. HACS Validation (`hacs.yml`)
- **Triggers**: Push, pull requests, daily schedule
- **Purpose**: Validates integration for HACS compatibility
- **Uses**: Official HACS action

### 4. Home Assistant Validation (`hassfest.yml`)
- **Triggers**: Push, pull requests, daily schedule
- **Purpose**: Validates integration with Home Assistant's hassfest tool
- **Uses**: Official Home Assistant action

### 5. CodeQL Security Analysis (`codeql.yml`)
- **Triggers**: Push to main/master, pull requests, weekly schedule
- **Purpose**: Static security analysis
- **Language**: Python

## Workflow Status Badges

The README.md includes status badges for all workflows:

```markdown
[![Code Quality](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/quality.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/quality.yml)
[![Tests](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/tests.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/tests.yml)
[![HACS](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hacs.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hacs.yml)
[![hassfest](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hassfest.yml)
[![CodeQL](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/codeql.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/codeql.yml)
```

## Quality Gates

The workflows enforce several quality gates:

1. **Code Style**: Ruff formatting and import sorting
2. **Code Quality**: Ruff linting with comprehensive checks
3. **Type Safety**: MyPy type checking (advisory for Home Assistant compatibility)
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
# Modern unified workflow using centralized commands
python hass-dev.py check    # Complete check (format + lint + test)
python hass-dev.py quality  # Code quality only (format + lint)
python hass-dev.py test     # Tests only
python hass-dev.py lint     # Lint only (Ruff + MyPy)
python hass-dev.py format   # Format only (Ruff)
```

All commands use the same tools and configuration as CI via `tools/commands.py`.

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
