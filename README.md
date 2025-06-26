# FIBARO Intercom Integration for Home Assistant

[![Tests](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/tests.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/tests.yml)
[![HACS](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hacs.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hacs.yml)
[![hassfest](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/hassfest.yml)
[![CodeQL](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/codeql.yml/badge.svg)](https://github.com/Squazel/homeassistant-fibaro-intercom/actions/workflows/codeql.yml)

A custom Home Assistant integration for controlling and monitoring FIBARO Intercom devices over their JSON-RPC 2.0 WebSocket API.

## Features

- **Real-time Connection**: Persistent WebSocket connection with automatic reconnection
- **Relay Control**: Open door/gate relays with optional timeout
- **Doorbell Monitoring**: Real-time doorbell press detection
- **Camera Integration**: Access to live video stream and still images
- **Event Handling**: Home Assistant events for doorbell presses
- **Robust Error Handling**: Comprehensive error handling and logging

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/Squazel/homeassistant-fibaro-intercom`
6. Select "Integration" as the category
7. Click "Add" and close the dialog
8. Locate Fibaro Intercom in the list of repositories and Download it

### Manual Installation

1. Copy the `custom_components/fibaro_intercom` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

### Via UI

1. Go to Settings → Devices & Services → Integrations
2. Click "Add Integration"
3. Search for "FIBARO Intercom"
4. Enter your intercom details:
   - **Host**: IP address or hostname
   - **Port**: WebSocket port (default: `8081`)
   - **Username**: Local account username
   - **Password**: Local account password

### Configuration Options

After setup, you can modify these options:
- Port number
- Credentials
- TLS verification settings
- Camera stream URLs

## Entities Created

### Binary Sensors
- **Connection Status**: Shows if the integration is connected to the intercom
- **Doorbell**: Activated when doorbell is pressed (auto-resets after 1 second)

### Switches
- **Relay 0**: Control for the first relay
- **Relay 1**: Control for the second relay

### Camera
- **Live Stream**: Real-time video feed from the intercom camera
- **Still Images**: Snapshot capability

## Services

### `fibaro_intercom.open_relay`

Opens a relay for a specified duration.

**Parameters:**
- `relay` (required): Relay number (0 or 1)
- `timeout` (optional): Duration in milliseconds (250-30000ms)

**Example:**
```yaml
service: fibaro_intercom.open_relay
data:
  relay: 0
  timeout: 5000
```

## Events

### `fibaro_intercom.doorbell_pressed`

Fired when the doorbell button is pressed.

**Event Data:**
- `button`: Button number that was pressed
- `timestamp`: When the event occurred

**Example Automation:**
```yaml
automation:
  - alias: "Doorbell Notification"
    trigger:
      platform: event
      event_type: fibaro_intercom.doorbell_pressed
    action:
      service: notify.mobile_app_your_phone
      data:
        message: "Someone is at the door!"
```

## API Reference

The integration communicates with the FIBARO Intercom using JSON-RPC 2.0 over WebSocket.

For complete API documentation, see the [FIBARO Intercom API Reference](https://manuals.fibaro.com/knowledge-base-browse/intercom-api/).

### WebSocket Endpoint
```
wss://<IP_ADDRESS>:<PORT>/wsock
```

### Authentication
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "com.fibaro.intercom.account.login",
  "params": {
    "user": "<USERNAME>",
    "pass": "<PASSWORD>"
  }
}
```

### Relay Control
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "com.fibaro.intercom.relay.open",
  "params": {
    "token": "<TOKEN>",
    "relay": 0,
    "timeout": 5000
  }
}
```

## Troubleshooting

### Connection Issues

1. **Check Network Connectivity**: Ensure Home Assistant can reach the intercom
2. **Verify Credentials**: Confirm username/password are correct
3. **Check Port**: Default WebSocket port is 8081
4. **TLS Issues**: Try disabling TLS verification if using self-signed certificates

### Debugging

Enable debug logging by adding to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.fibaro_intercom: debug
```

### Common Issues

- **Authentication Failed**: Check username/password and ensure local account is enabled
- **Connection Refused**: Verify the intercom IP address and port
- **Camera Not Working**: Check camera URLs and authentication

## Development

For development setup, testing, and contributing guidelines, see [tests/README.md](tests/README.md).  
For project structure and documentation overview, see [PROJECT.md](PROJECT.md).

**Quick start for developers:**
```bash
git clone https://github.com/Squazel/homeassistant-fibaro-intercom.git
cd homeassistant-fibaro-intercom
python -m venv .venv
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python -m pytest  # Run tests to verify setup - all tests should pass
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Squazel/homeassistant-fibaro-intercom/issues)
- **Documentation**: This README and [tests/README.md](tests/README.md) for development
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)
- **FIBARO API Reference**: [Official API Documentation](https://manuals.fibaro.com/knowledge-base-browse/intercom-api/)

## Version

**v1.0.0** - Initial release with WebSocket connection, relay control, doorbell monitoring, camera integration, and configuration flow.
