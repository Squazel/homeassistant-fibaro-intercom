"""Tests for the standalone FIBARO Intercom client."""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

import pytest

# Import the client without Home Assistant dependencies
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "custom_components", "fibaro_intercom"
    ),
)

from client import FibaroIntercomClient, FibaroIntercomConnectionError


class TestFibaroIntercomClient:
    """Test cases for FibaroIntercomClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = FibaroIntercomClient(
            host="192.168.0.17", port=8081, username="testuser", password="testpass"
        )

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.host == "192.168.0.17"
        assert self.client.port == 8081
        assert self.client.username == "testuser"
        assert self.client.password == "testpass"
        assert not self.client.is_connected

    @pytest.mark.asyncio
    async def test_successful_connection_and_auth(self):
        """Test successful connection and authentication."""
        mock_websocket = AsyncMock()

        # Mock the authentication response
        auth_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"token": "test_token_123"},
        }

        with patch(
            "client.websockets.connect",
            new_callable=AsyncMock,
            return_value=mock_websocket,
        ):
            with patch.object(self.client, "_send_request", return_value=auth_response):
                await self.client.connect()

                assert self.client.is_connected
                assert self.client._token == "test_token_123"

    @pytest.mark.asyncio
    async def test_authentication_failure(self):
        """Test authentication failure."""
        mock_websocket = AsyncMock()

        # Mock authentication error response
        auth_error = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32602, "message": "Invalid credentials"},
        }

        with patch(
            "client.websockets.connect",
            new_callable=AsyncMock,
            return_value=mock_websocket,
        ):
            with patch.object(self.client, "_send_request", return_value=auth_error):
                with pytest.raises(
                    FibaroIntercomConnectionError, match="Authentication failed"
                ):
                    await self.client.connect()

    @pytest.mark.asyncio
    async def test_relay_open_success(self):
        """Test successful relay opening."""
        # Set up authenticated client
        self.client._connected = True
        self.client._token = "test_token"

        relay_response = {"jsonrpc": "2.0", "id": 2, "result": True}

        with patch.object(self.client, "_send_request", return_value=relay_response):
            result = await self.client.open_relay(0, 5000)
            assert result is True

    @pytest.mark.asyncio
    async def test_relay_open_without_connection(self):
        """Test relay opening without connection."""
        with pytest.raises(FibaroIntercomConnectionError):
            await self.client.open_relay(0)

    @pytest.mark.asyncio
    async def test_relay_open_with_error(self):
        """Test relay opening with error response."""
        self.client._connected = True
        self.client._token = "test_token"

        error_response = {
            "jsonrpc": "2.0",
            "id": 2,
            "error": {"code": -32602, "message": "Invalid relay"},
        }

        with patch.object(self.client, "_send_request", return_value=error_response):
            result = await self.client.open_relay(0)
            assert result is False

    @pytest.mark.asyncio
    async def test_event_callback_registration(self):
        """Test event callback registration and removal."""
        callback_called = False

        def test_callback(params):
            nonlocal callback_called
            callback_called = True

        # Register callback
        self.client.add_event_callback("test.method", test_callback)

        # Simulate receiving an event
        test_event = {
            "jsonrpc": "2.0",
            "method": "test.method",
            "params": {"test": "data"},
        }

        await self.client._handle_message(test_event)
        assert callback_called

        # Remove callback
        self.client.remove_event_callback("test.method")
        callback_called = False

        await self.client._handle_message(test_event)
        assert not callback_called

    @pytest.mark.asyncio
    async def test_doorbell_event_handling(self):
        """Test handling of doorbell events."""
        received_params = None

        def doorbell_callback(params):
            nonlocal received_params
            received_params = params

        self.client.add_event_callback(
            "com.fibaro.intercom.device.buttonStateChanged", doorbell_callback
        )

        doorbell_event = {
            "jsonrpc": "2.0",
            "method": "com.fibaro.intercom.device.buttonStateChanged",
            "params": {"button": 2, "state": True},
        }

        await self.client._handle_message(doorbell_event)

        assert received_params is not None
        assert received_params["button"] == 2
        assert received_params["state"] is True

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test client disconnection."""
        mock_websocket = AsyncMock()
        self.client._websocket = mock_websocket
        self.client._connected = True

        await self.client.disconnect()

        assert not self.client._connected
        assert self.client._websocket is None
        assert self.client._token is None
        mock_websocket.close.assert_called_once()

    def test_ssl_configuration(self):
        """Test SSL configuration options."""
        # Test with SSL verification disabled
        client_no_ssl = FibaroIntercomClient(
            host="192.168.0.17",
            port=8081,
            username="user",
            password="pass",
            ssl_verify=False,
        )

        assert not client_no_ssl.ssl_verify

    @pytest.mark.asyncio
    async def test_request_timeout(self):
        """Test request timeout handling."""
        self.client._websocket = AsyncMock()
        self.client._connected = True

        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
            with pytest.raises(FibaroIntercomConnectionError, match="Request timeout"):
                await self.client._send_request("test.method", {})


# Example of how to run these tests standalone
if __name__ == "__main__":
    # Run a simple test without pytest
    async def run_basic_test():
        client = FibaroIntercomClient("192.168.0.17", 8081, "user", "pass")
        print(f"Client created: {client.host}:{client.port}")
        print(f"Connected: {client.is_connected}")

        # Test callback registration
        def test_callback(params):
            print(f"Event received: {params}")

        client.add_event_callback("test.event", test_callback)
        print("Event callback registered")

        # Test event handling
        test_event = {
            "jsonrpc": "2.0",
            "method": "test.event",
            "params": {"message": "Hello, World!"},
        }

        await client._handle_message(test_event)
        print("Test completed successfully!")

    # Uncomment to run basic test
    # asyncio.run(run_basic_test())
