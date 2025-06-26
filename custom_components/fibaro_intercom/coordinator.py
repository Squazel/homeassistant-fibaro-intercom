"""Coordinator for FIBARO Intercom integration."""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
from typing import Any, Callable

import websockets
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from websockets.exceptions import ConnectionClosed, InvalidURI

from .const import (ATTR_BUTTON, ATTR_RELAY, ATTR_STATE, ATTR_TIMEOUT, DOMAIN,
                    EVENT_DOORBELL_PRESSED, METHOD_BUTTON_STATE_CHANGED,
                    METHOD_LOGIN, METHOD_RELAY_OPEN,
                    METHOD_RELAY_STATE_CHANGED, WEBSOCKET_PATH)

_LOGGER = logging.getLogger(__name__)


class FibaroIntercomCoordinator(DataUpdateCoordinator):
    """Coordinator for managing FIBARO Intercom WebSocket connection."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_update_data,
        )
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.websocket: websockets.WebSocketServerProtocol | None = None
        self.token: str | None = None
        self.connected = False
        self.relay_states: dict[int, bool] = {0: False, 1: False}
        self.doorbell_pressed = False
        self._message_id = 0
        self._reconnect_task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

        # Subscribe to Home Assistant stop event
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self._async_stop)

    async def _async_stop(self, event: Event) -> None:
        """Handle Home Assistant stop."""
        self._stop_event.set()
        await self.async_disconnect()

    def _get_next_id(self) -> int:
        """Get next message ID."""
        self._message_id += 1
        return self._message_id

    async def async_test_connection(self) -> bool:
        """Test connection to the intercom."""
        try:
            uri = f"wss://{self.host}:{self.port}{WEBSOCKET_PATH}"
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                # Send login request
                login_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": METHOD_LOGIN,
                    "params": {
                        "user": self.username,
                        "pass": self.password,
                    },
                }
                await websocket.send(json.dumps(login_request))

                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(response)

                if "error" in data:
                    _LOGGER.error("Login failed: %s", data["error"])
                    raise ConnectionError("Authentication failed")

                if "result" not in data or "token" not in data["result"]:
                    raise ConnectionError("Invalid login response")

                return True

        except Exception as ex:
            _LOGGER.error("Connection test failed: %s", ex)
            raise ConnectionError(f"Connection failed: {ex}") from ex

    async def async_connect(self) -> None:
        """Connect to the intercom."""
        if self.connected:
            return

        try:
            await self._async_connect_websocket()
        except Exception as ex:
            _LOGGER.error("Failed to connect: %s", ex)
            # Start reconnection task
            if not self._reconnect_task or self._reconnect_task.done():
                self._reconnect_task = asyncio.create_task(self._async_reconnect_loop())
            raise

    async def _async_connect_websocket(self) -> None:
        """Connect WebSocket and authenticate."""
        uri = f"wss://{self.host}:{self.port}{WEBSOCKET_PATH}"
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.websocket = await websockets.connect(uri, ssl=ssl_context)

        # Authenticate
        await self._async_login()

        # Start listening for messages
        self.hass.async_create_background_task(
            self._async_listen_messages(), name="fibaro_intercom_listen"
        )

        self.connected = True
        _LOGGER.info("Connected to FIBARO Intercom at %s:%s", self.host, self.port)

    async def _async_login(self) -> None:
        """Authenticate with the intercom."""
        login_request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": METHOD_LOGIN,
            "params": {
                "user": self.username,
                "pass": self.password,
            },
        }

        await self.websocket.send(json.dumps(login_request))

        # Wait for login response
        response = await asyncio.wait_for(self.websocket.recv(), timeout=10)
        data = json.loads(response)

        if "error" in data:
            raise ConnectionError(f"Login failed: {data['error']}")

        if "result" not in data or "token" not in data["result"]:
            raise ConnectionError("Invalid login response")

        self.token = data["result"]["token"]
        _LOGGER.debug("Successfully authenticated with token")

    async def _async_listen_messages(self) -> None:
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._async_handle_message(data)
                except json.JSONDecodeError:
                    _LOGGER.warning("Received invalid JSON: %s", message)
                except Exception as ex:
                    _LOGGER.error("Error handling message: %s", ex)
        except ConnectionClosed:
            _LOGGER.warning("WebSocket connection closed")
            self.connected = False
            if not self._stop_event.is_set():
                # Start reconnection if not stopping
                if not self._reconnect_task or self._reconnect_task.done():
                    self._reconnect_task = asyncio.create_task(
                        self._async_reconnect_loop()
                    )

    async def _async_handle_message(self, data: dict[str, Any]) -> None:
        """Handle incoming WebSocket message."""
        method = data.get("method")

        if method == METHOD_RELAY_STATE_CHANGED:
            await self._async_handle_relay_state_changed(data.get("params", {}))
        elif method == METHOD_BUTTON_STATE_CHANGED:
            await self._async_handle_button_state_changed(data.get("params", {}))
        elif "error" in data:
            _LOGGER.warning("Received error: %s", data["error"])

    async def _async_handle_relay_state_changed(self, params: dict[str, Any]) -> None:
        """Handle relay state change."""
        relay = params.get(ATTR_RELAY, 0)
        state = params.get(ATTR_STATE, False)

        _LOGGER.debug("Relay %s state changed to %s", relay, state)
        self.relay_states[relay] = state

        # Update coordinator data
        self.async_set_updated_data(
            {
                "relay_states": self.relay_states,
                "connected": self.connected,
            }
        )

    async def _async_handle_button_state_changed(self, params: dict[str, Any]) -> None:
        """Handle button state change (doorbell)."""
        button = params.get(ATTR_BUTTON, 0)
        state = params.get(ATTR_STATE, False)

        if state:  # Button pressed
            _LOGGER.debug("Doorbell button %s pressed", button)

            # Fire Home Assistant event
            self.hass.bus.async_fire(
                EVENT_DOORBELL_PRESSED,
                {
                    ATTR_BUTTON: button,
                    "device_id": f"fibaro_intercom_{self.host}",
                },
            )

            # Update doorbell sensor state
            self.doorbell_pressed = True
            self.async_set_updated_data(
                {
                    "doorbell_pressed": True,
                    "relay_states": self.relay_states,
                    "connected": self.connected,
                }
            )

            # Reset doorbell state after 1 second
            def reset_doorbell():
                self.doorbell_pressed = False
                self.async_set_updated_data(
                    {
                        "doorbell_pressed": False,
                        "relay_states": self.relay_states,
                        "connected": self.connected,
                    }
                )

            self.hass.loop.call_later(1.0, reset_doorbell)

    async def _async_reconnect_loop(self) -> None:
        """Reconnect with exponential backoff."""
        backoff = 1
        max_backoff = 300

        while not self._stop_event.is_set() and not self.connected:
            try:
                _LOGGER.info("Attempting to reconnect to FIBARO Intercom...")
                await self._async_connect_websocket()
                backoff = 1  # Reset backoff on successful connection
            except Exception as ex:
                _LOGGER.warning(
                    "Reconnection failed: %s. Retrying in %s seconds", ex, backoff
                )
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=backoff)
                    break  # Stop event was set
                except asyncio.TimeoutError:
                    pass  # Continue with next retry

                backoff = min(backoff * 2, max_backoff)

    async def async_disconnect(self) -> None:
        """Disconnect from the intercom."""
        self._stop_event.set()

        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        self.connected = False
        self.token = None

    async def async_open_relay(self, relay: int, timeout: int | None = None) -> bool:
        """Open a relay."""
        if not self.connected or not self.token:
            raise ConnectionError("Not connected to intercom")

        params = {
            "token": self.token,
            "relay": relay,
        }

        if timeout is not None:
            params["timeout"] = timeout

        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": METHOD_RELAY_OPEN,
            "params": params,
        }

        try:
            await self.websocket.send(json.dumps(request))

            # Wait for response (optional, depending on requirements)
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5)
            data = json.loads(response)

            if "error" in data:
                _LOGGER.warning("Relay open failed: %s", data["error"])
                return False

            return data.get("result", False)

        except Exception as ex:
            _LOGGER.error("Failed to open relay %s: %s", relay, ex)
            return False

    async def _async_update_data(self) -> dict[str, Any]:
        """Update coordinator data."""
        return {
            "connected": self.connected,
            "relay_states": self.relay_states,
            "doorbell_pressed": self.doorbell_pressed,
        }
