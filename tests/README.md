# Testing and Development Guide

This guide covers testing and development for the FIBARO Intercom integration.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip or poetry for dependency management

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Squazel/homeassistant-fibaro-intercom.git
cd homeassistant-fibaro-intercom
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
```

This single requirements file includes everything needed for:
- Testing (pytest, pytest-asyncio, etc.)
- Code quality (black, isort, flake8, mypy)
- Runtime dependencies (websockets, aiohttp)

The integration's core logic in `client.py` only requires `websockets` and can be tested independently of Home Assistant.

## Architecture

The integration is designed with separation of concerns to enable standalone testing:

### Core Components

1. **`client.py`**: Standalone FIBARO Intercom client
   - Pure Python implementation
   - No Home Assistant dependencies
   - Can be tested independently
   - Handles WebSocket communication and JSON-RPC

2. **`coordinator.py`**: Home Assistant integration layer
   - Bridges between the client and Home Assistant
   - Manages data updates and state
   - Handles Home Assistant-specific events

3. **Platform Files**: Home Assistant entity implementations
   - `binary_sensor.py`: Connection status and doorbell sensors
   - `switch.py`: Relay control switches
   - `camera.py`: Camera stream integration
   - `config_flow.py`: UI configuration flow

## Testing

### Running Tests

Run all tests:
```bash
python -m pytest
```

Run with coverage:
```bash
# From project root
cd custom_components/fibaro_intercom
python -m pytest ../../tests/ --cov=client --cov-report=html:../../tests/htmlcov --cov-report=term-missing

# Or with XML output for CI
python -m pytest ../../tests/ --cov=client --cov-report=xml:../../tests/coverage.xml --cov-report=term-missing
```

Run specific test files:
```bash
python -m pytest tests/test_client.py
python -m pytest tests/test_coordinator.py
```

All tests should pass successfully. The test suite includes comprehensive tests for:
- WebSocket connection and authentication
- Relay control operations
- Event handling and callbacks
- Error conditions and edge cases
- SSL configuration options

### Test Structure

- `tests/test_client.py`: Tests for the standalone client
- `tests/test_coordinator.py`: Tests for the Home Assistant coordinator
- `tests/test_config_flow.py`: Tests for the configuration flow
- `tests/conftest.py`: Shared test fixtures and utilities

### Standalone Client Testing

The core client can be tested without Home Assistant:

```python
from custom_components.fibaro_intercom.client import FibaroIntercomClient

# Create a client instance
client = FibaroIntercomClient(
    host="192.168.0.17",
    port=8081,
    username="admin",
    password="password"
)

# Test connection (requires real intercom or mock server)
await client.connect()
result = await client.open_relay(0, 5000)
await client.disconnect()
```

### Mock Testing

For unit tests, use the provided mocks:

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_relay_open():
    with patch('websockets.connect') as mock_connect:
        mock_websocket = AsyncMock()
        mock_connect.return_value = mock_websocket
        
        client = FibaroIntercomClient("192.168.0.17", 8081, "user", "pass")
        await client.connect()
        
        # Test your functionality
        assert client.is_connected
```

## Code Quality

### Formatting

Format code with Black:
```bash
black custom_components/ tests/
```

### Import Sorting

Sort imports with isort:
```bash
isort custom_components/ tests/
```

### Linting

Run flake8 for linting:
```bash
flake8 custom_components/ tests/
```

### Type Checking

Run mypy for type checking:
```bash
mypy custom_components/fibaro_intercom/
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Manual Testing

### FIBARO API Documentation

For complete API reference, consult the [FIBARO Intercom API Documentation](https://manuals.fibaro.com/knowledge-base-browse/intercom-api/).

### Testing with Real Hardware

1. Set up the integration in a development Home Assistant instance
2. Configure with your intercom's IP and credentials
3. Test relay operations through the UI
4. Monitor logs for any issues

### Testing with Mock Server

Create a simple WebSocket server for testing:

```python
import asyncio
import websockets
import json

async def mock_intercom_server(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        
        if data.get("method") == "com.fibaro.intercom.account.login":
            response = {
                "jsonrpc": "2.0",
                "id": data["id"],
                "result": {"token": "mock_token_12345"}
            }
        elif data.get("method") == "com.fibaro.intercom.relay.open":
            response = {
                "jsonrpc": "2.0",
                "id": data["id"],
                "result": True
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": data["id"],
                "error": {"code": -32601, "message": "Method not found"}
            }
        
        await websocket.send(json.dumps(response))

# Run the mock server
start_server = websockets.serve(mock_intercom_server, "localhost", 8081)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

## Debugging

### Enable Debug Logging

Add to your development `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.fibaro_intercom: debug
    custom_components.fibaro_intercom.client: debug
    custom_components.fibaro_intercom.coordinator: debug
```

### Common Debug Scenarios

1. **Connection Issues**:
   - Check WebSocket connection establishment
   - Verify authentication token receipt
   - Monitor reconnection attempts

2. **Message Handling**:
   - Log all incoming JSON-RPC messages
   - Verify event callback execution
   - Check request/response matching

3. **State Updates**:
   - Monitor coordinator data updates
   - Verify entity state changes
   - Check Home Assistant event firing

## Contributing

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation as needed
6. Submit a pull request

### Code Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Add docstrings for all public methods
- Keep functions focused and testable
- Separate Home Assistant-specific code from core logic

### Testing Requirements

- All new features must have unit tests
- Achieve >90% code coverage
- Include both success and error case tests
- Test edge cases and boundary conditions

## Release Process

1. Update version in `manifest.json`
2. Create a GitHub release with release notes
3. Optionally set up automated releases later

## Documentation Structure

- **`README.md`**: Main user documentation, installation, configuration, usage
- **`tests/README.md`**: This file - development, testing, contributing
- **`DESCRIPTION.md`**: HACS integration description
- **`.github/WORKFLOWS.md`**: GitHub Actions documentation

## Troubleshooting Development Issues

### Import Errors in IDE

If your IDE shows import errors for Home Assistant modules:

1. Either install Home Assistant: `pip install homeassistant`
2. Or configure your IDE to ignore these specific import errors
3. The integration will work correctly when deployed to Home Assistant

### WebSocket Testing

Use tools like `wscat` to manually test WebSocket connections:

```bash
npm install -g wscat
wscat -c wss://192.168.0.17:8081/wsock
```

### Python Path Issues

Ensure the project root is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

Or in your IDE, mark the project root as a source folder.
