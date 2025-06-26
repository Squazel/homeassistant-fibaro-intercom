"""Core FIBARO Intercom client logic that can be tested independently."""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
from typing import Any, Callable, Dict, Optional

import websockets
import websockets.exceptions

_LOGGER = logging.getLogger(__name__)


class FibaroIntercomError(Exception):
    """Base exception for FIBARO Intercom errors."""


class FibaroIntercomConnectionError(FibaroIntercomError):
    """Connection-related errors."""


class FibaroIntercomAuthError(FibaroIntercomError):
    """Authentication-related errors."""


class FibaroIntercomClient:
    """Standalone FIBARO Intercom client for JSON-RPC WebSocket communication."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        ssl_verify: bool = True,
        reconnect_interval: int = 5,
        max_reconnect_attempts: int = 10,
    ) -> None:
        """Initialize the client."""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssl_verify = ssl_verify
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts

        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._token: Optional[str] = None
        self._request_id = 0
        self._pending_requests: Dict[int, asyncio.Future[Dict[str, Any]]] = {}
        self._event_callbacks: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self._connected = False
        self._reconnect_task: Optional[asyncio.Task[None]] = None
        self._listen_task: Optional[asyncio.Task[None]] = None

    @property
    def is_connected(self) -> bool:
        """Return True if connected and authenticated."""
        return self._connected and self._token is not None

    def add_event_callback(
        self, method: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Add a callback for a specific JSON-RPC method."""
        self._event_callbacks[method] = callback

    def remove_event_callback(self, method: str) -> None:
        """Remove a callback for a specific JSON-RPC method."""
        self._event_callbacks.pop(method, None)

    async def connect(self) -> None:
        """Connect to the FIBARO Intercom."""
        if self._reconnect_task:
            self._reconnect_task.cancel()

        try:
            await self._connect_websocket()
            await self._authenticate()
            self._connected = True

            # Start listening for messages
            if self._listen_task:
                self._listen_task.cancel()
            self._listen_task = asyncio.create_task(self._listen_for_messages())

        except Exception as ex:
            _LOGGER.error("Failed to connect: %s", ex)
            raise FibaroIntercomConnectionError(f"Connection failed: {ex}") from ex

    async def disconnect(self) -> None:
        """Disconnect from the FIBARO Intercom."""
        self._connected = False

        if self._reconnect_task:
            self._reconnect_task.cancel()
            self._reconnect_task = None

        if self._listen_task:
            self._listen_task.cancel()
            self._listen_task = None

        if self._websocket:
            await self._websocket.close()
            self._websocket = None

        self._token = None

    async def open_relay(self, relay: int, timeout: Optional[int] = None) -> bool:
        """Open a relay."""
        if not self.is_connected:
            raise FibaroIntercomConnectionError("Not connected")

        params: Dict[str, Any] = {
            "token": self._token,
            "relay": relay,
        }

        if timeout is not None:
            params["timeout"] = timeout

        response = await self._send_request("com.fibaro.intercom.relay.open", params)

        if "error" in response:
            error = response["error"]
            _LOGGER.warning(
                "Relay open failed: %s", error.get("message", "Unknown error")
            )
            return False

        return response.get("result", False) is True

    async def _connect_websocket(self) -> None:
        """Establish WebSocket connection."""
        uri = f"wss://{self.host}:{self.port}/wsock"

        ssl_context = None
        if not self.ssl_verify:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        self._websocket = await websockets.connect(
            uri,
            ssl=ssl_context,
            ping_interval=30,
            ping_timeout=10,
        )

    async def _authenticate(self) -> None:
        """Authenticate with the intercom."""
        response = await self._send_request(
            "com.fibaro.intercom.account.login",
            {"user": self.username, "pass": self.password},
        )

        if "error" in response:
            error = response["error"]
            raise FibaroIntercomAuthError(
                f"Authentication failed: {error.get('message', 'Unknown error')}"
            )

        result = response.get("result", {})
        self._token = result.get("token")

        if not self._token:
            raise FibaroIntercomAuthError(
                "No token received in authentication response"
            )

    async def _send_request(
        self, method: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a JSON-RPC request and wait for response."""
        if not self._websocket:
            raise FibaroIntercomConnectionError("WebSocket not connected")

        self._request_id += 1
        request_id = self._request_id

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }

        # Create future for response
        future: asyncio.Future[Dict[str, Any]] = asyncio.Future()
        self._pending_requests[request_id] = future

        try:
            await self._websocket.send(json.dumps(message))
            # Wait for response with timeout
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise FibaroIntercomConnectionError("Request timeout")
        except Exception as ex:
            self._pending_requests.pop(request_id, None)
            raise FibaroIntercomConnectionError(f"Request failed: {ex}") from ex

    async def _listen_for_messages(self) -> None:
        """Listen for incoming WebSocket messages."""
        if not self._websocket:
            return

        try:
            async for message in self._websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    _LOGGER.warning("Received invalid JSON: %s", message)
                except Exception as ex:
                    _LOGGER.error("Error handling message: %s", ex)

        except websockets.exceptions.ConnectionClosed:
            _LOGGER.info("WebSocket connection closed")
            self._connected = False
            if self.max_reconnect_attempts > 0:
                self._reconnect_task = asyncio.create_task(self._reconnect())
        except Exception as ex:
            _LOGGER.error("Error in message listener: %s", ex)
            self._connected = False

    async def _handle_message(self, data: Dict[str, Any]) -> None:
        """Handle incoming JSON-RPC message."""
        # Handle responses to our requests
        if "id" in data and data["id"] in self._pending_requests:
            future = self._pending_requests.pop(data["id"])
            future.set_result(data)
            return

        # Handle notifications/events
        if "method" in data:
            method = data["method"]
            if method in self._event_callbacks:
                try:
                    self._event_callbacks[method](data.get("params", {}))
                except Exception as ex:
                    _LOGGER.error("Error in event callback for %s: %s", method, ex)
            else:
                _LOGGER.debug("Unhandled event: %s", method)

    async def _reconnect(self) -> None:
        """Attempt to reconnect with exponential backoff."""
        attempts = 0
        while attempts < self.max_reconnect_attempts and not self._connected:
            attempts += 1
            delay = min(
                self.reconnect_interval * (2 ** (attempts - 1)), 300
            )  # Max 5 minutes

            _LOGGER.info(
                "Attempting reconnect %d/%d in %d seconds",
                attempts,
                self.max_reconnect_attempts,
                delay,
            )
            await asyncio.sleep(delay)

            try:
                await self.connect()
                _LOGGER.info("Reconnected successfully")
                return
            except Exception as ex:
                _LOGGER.warning("Reconnect attempt %d failed: %s", attempts, ex)

        _LOGGER.error(
            "Failed to reconnect after %d attempts", self.max_reconnect_attempts
        )
