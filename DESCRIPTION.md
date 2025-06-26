# FIBARO Intercom Integration

Control and monitor your FIBARO Intercom directly from Home Assistant with real-time WebSocket communication.

## ✨ Features

- **🔗 Real-time Connection**: Persistent WebSocket with automatic reconnection
- **🚪 Door Control**: Open relays with customizable timeout (250-30000ms)
- **🔔 Doorbell Events**: Instant notifications when doorbell is pressed
- **📹 Camera Integration**: Live video stream and snapshot capabilities
- **⚙️ Easy Setup**: Configuration through Home Assistant UI
- **🛡️ Robust**: Comprehensive error handling and logging

## 📱 What You Get

After installation, you'll have:

- **Binary Sensors**: Connection status and doorbell detection
- **Switches**: Individual relay controls for doors/gates
- **Camera**: Live stream from intercom camera
- **Service**: `fibaro_intercom.open_relay` for automation
- **Events**: `fibaro_intercom.doorbell_pressed` for triggers

## 🚀 Quick Setup

1. Add integration via **Settings** → **Devices & Services**
2. Search for "FIBARO Intercom"
3. Enter your intercom IP, port (8081), username, and password
4. Enjoy secure, local control of your intercom!

## 🔧 Requirements

- FIBARO Intercom with local account enabled
- Network access from Home Assistant to intercom
- WebSocket port (default 8081) accessible

## 📖 Documentation

Complete setup, API reference, and troubleshooting guide available in the [repository README](https://github.com/Squazel/homeassistant-fibaro-intercom).

## 🛠️ Tested & Reliable

- ✅ Comprehensive test suite (11 tests, 69% coverage)
- ✅ Automated CI/CD with GitHub Actions
- ✅ Type-safe Python code with strict typing
- ✅ Follows Home Assistant best practices
