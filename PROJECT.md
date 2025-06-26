# Project Structure & Documentation

## 📁 Repository Structure

```
homeassistant-fibaro-intercom/
├── custom_components/fibaro_intercom/    # Integration code
│   ├── __init__.py                      # Entry point
│   ├── manifest.json                    # Integration metadata
│   ├── const.py                         # Constants
│   ├── config_flow.py                   # UI configuration
│   ├── coordinator.py                   # HA data coordinator
│   ├── client.py                        # Standalone WebSocket client
│   ├── binary_sensor.py                 # Connection & doorbell sensors
│   ├── switch.py                        # Relay switches
│   ├── camera.py                        # Camera integration
│   └── services.yaml                    # Service definitions
├── tests/                               # Test suite
│   ├── test_client.py                   # Client tests (11 tests, 69% coverage)
│   ├── conftest.py                      # Test fixtures
│   ├── coverage.xml                     # Coverage report (gitignored)
│   └── README.md                        # Development guide
├── .github/workflows/                   # CI/CD automation
│   ├── tests.yml                        # Test pipeline
│   ├── hacs.yml                         # HACS validation
│   ├── hassfest.yml                     # HA validation
│   └── codeql.yml                       # Security scanning
├── README.md                            # Main documentation
├── DESCRIPTION.md                       # HACS description
├── requirements.txt                     # Development dependencies
├── LICENSE                              # MIT license
└── .gitignore                           # Git exclusions
```

## 📚 Documentation Locations

### User Documentation
- **`README.md`**: Complete user guide
  - Installation (HACS + manual)
  - Configuration via UI
  - Usage examples
  - API reference
  - Troubleshooting

- **`DESCRIPTION.md`**: HACS marketplace description
  - Feature highlights
  - Quick setup guide
  - Requirements

### Developer Documentation  
- **`tests/README.md`**: Development guide
  - Setup instructions
  - Architecture overview
  - Testing procedures
  - Code quality tools
  - Contributing guidelines

- **`.github/WORKFLOWS.md`**: CI/CD documentation
  - Workflow descriptions
  - Quality gates
  - Release process

## 🧪 Testing & Coverage

- **Location**: `tests/` directory
- **Framework**: pytest with asyncio support
- **Coverage**: 69% (154 statements, 48 missed)
- **Files**:
  - `coverage.xml` - XML coverage report (for CI)
  - `htmlcov/` - HTML coverage report (for local viewing)
  - `__pycache__/` - Compiled bytecode (gitignored)

## 🔧 Development Workflow

1. **Setup**: `pip install -r requirements.txt`
2. **Code**: Edit files in `custom_components/fibaro_intercom/`
3. **Test**: Run `python -m pytest` from project root
4. **Format**: `black custom_components/ tests/`
5. **Sort**: `isort custom_components/ tests/`
6. **Lint**: `flake8 custom_components/ tests/`
7. **Coverage**: See testing commands in `tests/README.md`

## 🚀 CI/CD Pipeline

- **Tests**: Python 3.11, 3.12, 3.13 matrix
- **Quality**: black, isort, flake8, mypy
- **Validation**: HACS + hassfest
- **Security**: CodeQL scanning
- **Coverage**: Automatic upload to Codecov

All documentation is consolidated into these key files to avoid duplication and maintenance overhead.
