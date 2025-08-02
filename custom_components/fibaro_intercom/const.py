"""Constants for the FIBARO Intercom integration."""

from __future__ import annotations

DOMAIN = "fibaro_intercom"

# Configuration
DEFAULT_PORT = 8081
DEFAULT_TIMEOUT = 30

# WebSocket endpoints
WEBSOCKET_PATH = "/wsock"

# JSON-RPC methods
METHOD_LOGIN = "com.fibaro.intercom.account.login"
METHOD_REFRESH_TOKEN = "com.fibaro.intercom.account.refreshToken"
METHOD_RELAY_OPEN = "com.fibaro.intercom.relay.open"
METHOD_RELAY_STATE_CHANGED = "com.fibaro.intercom.relay.stateChanged"
METHOD_BUTTON_STATE_CHANGED = "com.fibaro.intercom.device.buttonStateChanged"

# Events
EVENT_DOORBELL_PRESSED = "fibaro_intercom.doorbell_pressed"

# Camera endpoints
CAMERA_LIVE_MJPEG = "/live/mjpeg"
CAMERA_STILL_JPEG = "/live/jpeg"
CAMERA_PORT = 8080

# Entity names
ENTITY_CONNECTION_STATUS = "connection_status"
ENTITY_RELAY_PREFIX = "relay_"
ENTITY_CAMERA = "camera"

# Attributes
ATTR_RELAY = "relay"
ATTR_TIMEOUT = "timeout"
ATTR_BUTTON = "button"
ATTR_RELAY_STATE = "is_open"
ATTR_BUTTON_STATE = "state"
ATTR_METHOD = "method"
ATTR_USER = "user"
