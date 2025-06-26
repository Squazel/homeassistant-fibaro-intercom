"""Shared test fixtures and utilities."""

import json
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    websocket = AsyncMock()
    websocket.send = AsyncMock()
    websocket.close = AsyncMock()
    websocket.__aenter__ = AsyncMock(return_value=websocket)
    websocket.__aexit__ = AsyncMock(return_value=None)
    return websocket


@pytest.fixture
def login_response():
    """Sample login response."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token"},
    }


@pytest.fixture
def relay_response():
    """Sample relay open response."""
    return {"jsonrpc": "2.0", "id": 2, "result": True}


@pytest.fixture
def error_response():
    """Sample error response."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32602, "message": "Invalid params"},
    }


@pytest.fixture
def doorbell_event():
    """Sample doorbell event."""
    return {
        "jsonrpc": "2.0",
        "method": "com.fibaro.intercom.device.buttonStateChanged",
        "params": {"button": 2, "state": True},
    }


@pytest.fixture
def relay_state_event():
    """Sample relay state changed event."""
    return {
        "jsonrpc": "2.0",
        "method": "com.fibaro.intercom.relay.stateChanged",
        "params": {"relay": 0, "state": True, "method": "WS_API", "user": ""},
    }


class MockWebSocketMessages:
    """Helper class to simulate WebSocket message sequences."""

    def __init__(self, messages):
        self.messages = iter(messages)
        self.sent_messages = []

    async def send(self, message):
        """Mock send method that records sent messages."""
        self.sent_messages.append(json.loads(message))
        try:
            return next(self.messages)
        except StopIteration:
            return None

    def __aiter__(self):
        """Async iterator for receiving messages."""
        return self

    async def __anext__(self):
        """Get next message."""
        try:
            message = next(self.messages)
            return json.dumps(message) if isinstance(message, dict) else message
        except StopIteration:
            raise StopAsyncIteration
