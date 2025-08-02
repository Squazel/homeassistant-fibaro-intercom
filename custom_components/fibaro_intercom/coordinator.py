"""Coordinator for FIBARO Intercom integration."""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
import time
from typing import Any

import websockets
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from websockets.exceptions import ConnectionClosed

from .const import (
    ATTR_BUTTON,
    ATTR_BUTTON_STATE,
    ATTR_RELAY,
    ATTR_RELAY_STATE,
    DOMAIN,
    EVENT_DOORBELL_PRESSED,
    METHOD_BUTTON_STATE_CHANGED,
    METHOD_LOGIN,
    METHOD_REFRESH_TOKEN,
    METHOD_RELAY_OPEN,
    METHOD_RELAY_STATE_CHANGED,
    WEBSOCKET_PATH,
)

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
        self.websocket: Any = None
        self.token: str | None = None
        self.token_expires_at: float | None = None
        self.connected = False
        self.relay_states: dict[int, bool] = {0: False, 1: False}
        self._message_id = 0
        self._reconnect_task: asyncio.Task | None = None
        self._listen_task: asyncio.Task | None = None
        self._health_check_task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self._last_authentication_time: float = 0

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

    def _get_device_id(self) -> str:
        """Get the device ID for this coordinator."""
        # This will be set by the entity platform during setup
        return getattr(self, "_device_id", f"fibaro_intercom_{self.host}")

    def set_device_id(self, device_id: str) -> None:
        """Set the device ID for this coordinator."""
        self._device_id = device_id

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context - called in executor to avoid blocking."""
        return ssl.create_default_context()

    async def async_test_connection(self) -> bool:
        """Test connection to the intercom."""
        try:
            uri = f"wss://{self.host}:{self.port}{WEBSOCKET_PATH}"
            # Create SSL context in executor to avoid blocking the event loop
            ssl_context = await self.hass.async_add_executor_job(
                self._create_ssl_context
            )
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
        # Create SSL context in executor to avoid blocking the event loop
        ssl_context = await self.hass.async_add_executor_job(self._create_ssl_context)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.websocket = await websockets.connect(
            uri,
            ssl=ssl_context,
        )
        _LOGGER.info(
            "WebSocket connected successfully to %s with ping/pong monitoring", uri
        )

        # Authenticate (this will start the message listener)
        await self._async_login()

        self.connected = True
        _LOGGER.info("Connected to FIBARO Intercom at %s:%s", self.host, self.port)

        # Update coordinator data with connection status
        self.async_set_updated_data(
            {
                "connected": True,
                "relay_states": self.relay_states,
            }
        )

    async def _async_login(self) -> None:
        """Authenticate with the intercom."""
        # Start listening for messages BEFORE sending login request
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
        self._listen_task = self.hass.async_create_background_task(
            self._async_listen_messages(), name="fibaro_intercom_listen"
        )

        login_request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": METHOD_LOGIN,
            "params": {
                "user": self.username,
                "pass": self.password,
            },
        }

        # Record authentication timestamp before sending request
        auth_before_login = self._last_authentication_time
        await self.websocket.send(json.dumps(login_request))

        # Wait up to 10 seconds for the login response
        for _ in range(20):  # Check every 0.5 seconds for 10 seconds total
            await asyncio.sleep(0.5)
            if self._last_authentication_time > auth_before_login and self.token:
                _LOGGER.debug("Login successful - token received")
                return

        # No login response received within timeout
        raise ConnectionError("Login failed - no response received within 10 seconds")

    def _is_token_expired(self) -> bool:
        """Check if token has expired."""
        if not self.token_expires_at:
            return False
        return time.time() >= self.token_expires_at

    async def _async_listen_messages(self) -> None:
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    # Log all received messages at debug level to track what we're getting
                    if isinstance(message, bytes):
                        _LOGGER.debug("Received binary message: %s bytes", len(message))
                    else:
                        _LOGGER.debug("Received message: %s", message)

                    data = json.loads(message)
                    await self._async_handle_message(data)
                except json.JSONDecodeError:
                    _LOGGER.warning("Received invalid JSON: %s", message)
                except Exception as ex:
                    _LOGGER.error("Error handling message: %s", ex, exc_info=True)
                    _LOGGER.error("Message that caused the error: %s", message)
        except ConnectionClosed as ex:
            if ex.code == 1000:
                _LOGGER.info("WebSocket connection closed normally")
            else:
                _LOGGER.warning(
                    "WebSocket connection closed with code %s: %s", ex.code, ex.reason
                )
            self._handle_disconnection()
        except Exception as ex:
            _LOGGER.warning("WebSocket connection lost due to unexpected error: %s", ex)
            self._handle_disconnection()

    def _handle_disconnection(self) -> None:
        """Handle WebSocket disconnection and trigger reconnection."""
        self.connected = False
        # Update coordinator data with disconnection status
        self.async_set_updated_data(
            {
                "connected": False,
                "relay_states": self.relay_states,
            }
        )
        if not self._stop_event.is_set():
            # Start reconnection if not stopping
            if not self._reconnect_task or self._reconnect_task.done():
                _LOGGER.info("Starting reconnection task...")
                self._reconnect_task = asyncio.create_task(self._async_reconnect_loop())

    async def _async_handle_message(self, data: dict[str, Any]) -> None:
        """Handle incoming WebSocket message."""
        # Check if this is a login or token refresh response and update our token
        if (
            "result" in data
            and isinstance(data["result"], dict)
            and "token" in data["result"]
        ):
            result = data["result"]
            old_token = self.token
            self.token = result["token"]

            if "exp_time" in result:
                exp_time_ms = float(result["exp_time"])
                self.token_expires_at = time.time() + (exp_time_ms / 1000.0)
                _LOGGER.debug(
                    "Token updated (expires in %d seconds)", exp_time_ms / 1000
                )
            else:
                self.token_expires_at = time.time() + 900
                _LOGGER.debug("Token updated (assuming 15min expiry)")

            # Update authentication timestamp for successful login or token refresh
            self._last_authentication_time = time.time()

            if old_token != self.token:
                _LOGGER.debug(
                    "Token refreshed: %s... -> %s...",
                    old_token[:8] if old_token else "None",
                    self.token[:8] if self.token else "None",
                )
            elif not old_token:
                _LOGGER.debug("Successfully authenticated with new token")

            # (Re)start health check monitoring with new token timing
            if self._health_check_task and not self._health_check_task.done():
                self._health_check_task.cancel()
            self._health_check_task = self.hass.async_create_background_task(
                self._async_health_check_loop(), name="fibaro_intercom_health"
            )

            if self.token_expires_at:
                expires_in = int(self.token_expires_at - time.time())
                _LOGGER.info(
                    "Health check monitoring (re)started - token expires in %d seconds at %s",
                    expires_in,
                    time.ctime(self.token_expires_at),
                )
            else:
                _LOGGER.info("Health check monitoring (re)started")

            return  # Don't process login/token refresh responses further

        method = data.get("method")

        if method == METHOD_RELAY_STATE_CHANGED:
            await self._async_handle_relay_state_changed(data.get("params", {}))
        elif method == METHOD_BUTTON_STATE_CHANGED:
            await self._async_handle_button_state_changed(data.get("params", {}))
        elif "error" in data:
            error = data["error"]
            error_message = str(error.get("message", "Unknown error"))
            error_code = str(error.get("code", "Unknown code"))

            # Handle expired token or invalid token
            error_data = (
                error.get("data") if isinstance(error.get("data"), dict) else {}
            )
            if (
                str(error.get("message", "")) == "Expired"
                or str(error_data.get("name", "")) == "InvalidToken"
            ):
                _LOGGER.info("Token expired or invalid, reconnecting...")
                self.connected = False
                await self.async_disconnect()
                await asyncio.sleep(2)  # brief pause before reconnect
                await self.async_connect()
            elif (
                "login" in error_message.lower()
                or "authentication" in error_message.lower()
            ):
                # Login/authentication errors - these will be caught by timeout in _async_login()
                # which will trigger the backoff logic
                _LOGGER.error(
                    "Authentication error from intercom: %s (code: %s)",
                    error_message,
                    error_code,
                )
            else:
                # Other errors (relay operations, etc.)
                _LOGGER.warning(
                    "Received error from intercom: %s (code: %s)",
                    error_message,
                    error_code,
                )

    async def _async_handle_relay_state_changed(self, params: dict[str, Any]) -> None:
        """Handle relay state change."""
        relay = params.get(ATTR_RELAY, 0)
        state = params.get(ATTR_RELAY_STATE, False)

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
        state = params.get(ATTR_BUTTON_STATE, False)

        if state:  # Button pressed
            _LOGGER.debug("Doorbell button %s pressed", button)

            # Fire Home Assistant event for device triggers
            self.hass.bus.async_fire(
                EVENT_DOORBELL_PRESSED,
                {
                    ATTR_BUTTON: button,
                    "device_id": self._get_device_id(),
                },
            )

    async def _async_reconnect_loop(self) -> None:
        """Reconnect with exponential backoff."""
        backoff = 1
        max_backoff = 600

        while not self._stop_event.is_set() and not self.connected:
            try:
                _LOGGER.info("Attempting to reconnect to FIBARO Intercom...")
                await self._async_connect_websocket()
                _LOGGER.info("Reconnected successfully")
                backoff = 1  # Reset backoff on successful connection
                return  # Exit the loop on successful reconnection
            except Exception as ex:
                if backoff < max_backoff:
                    _LOGGER.info(
                        "Reconnection failed: %s. Retrying in %s seconds", ex, backoff
                    )
                else:
                    _LOGGER.warning(
                        "Reconnection failed: %s. Retrying in %s seconds (max backoff reached)",
                        ex,
                        backoff,
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

        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

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
        self.token_expires_at = None

        # Update coordinator data to reflect disconnection
        self.async_set_updated_data(
            {
                "connected": False,
                "relay_states": self.relay_states,
            }
        )

    async def async_open_relay(self, relay: int, timeout: int | None = None) -> None:
        """Open a relay (fire and forget)."""
        # If not connected, try to reconnect immediately
        if not self.connected or not self.token:
            _LOGGER.warning(
                "Not connected, attempting immediate reconnection before relay command"
            )
            try:
                await self._async_connect_websocket()
                _LOGGER.info("Successfully reconnected before relay command")
            except Exception as ex:
                _LOGGER.error("Failed to reconnect before relay command: %s", ex)
                # Still trigger background reconnection
                if not self._reconnect_task or self._reconnect_task.done():
                    self._reconnect_task = asyncio.create_task(
                        self._async_reconnect_loop()
                    )
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
            _LOGGER.debug("Sent relay %s open command", relay)
        except Exception as ex:
            _LOGGER.error("Failed to open relay %s: %s", relay, ex)
            # Mark as disconnected if sending failed
            if self.connected:
                self.connected = False
                self.async_set_updated_data(
                    {
                        "connected": False,
                        "relay_states": self.relay_states,
                    }
                )
                # Trigger reconnection
                if not self._reconnect_task or self._reconnect_task.done():
                    self._reconnect_task = asyncio.create_task(
                        self._async_reconnect_loop()
                    )
            raise
        # No waiting for response, let main listener handle errors/state

    async def _async_update_data(self) -> dict[str, Any]:
        """Update coordinator data."""
        return {
            "connected": self.connected,
            "relay_states": self.relay_states,
        }

    async def _async_health_check_loop(self) -> None:
        """Periodically check token expiration and connection health."""
        while not self._stop_event.is_set() and self.connected:
            try:
                # Calculate next check interval:
                # - Every 60 seconds normally
                # - OR half the time remaining until token expiry (whichever is sooner)
                check_interval = 60  # Default 1 minute

                if self.token_expires_at:
                    time_until_expiry = self.token_expires_at - time.time()
                    if time_until_expiry > 0:
                        # Check at half the remaining time, but at least every 60 seconds
                        check_interval = min(check_interval, time_until_expiry / 2)
                        _LOGGER.debug(
                            "Next health check in %d seconds (token expires in %d seconds)",
                            int(check_interval),
                            int(time_until_expiry),
                        )

                await asyncio.wait_for(self._stop_event.wait(), timeout=check_interval)
                if self._stop_event.is_set():
                    break
            except asyncio.TimeoutError:
                pass  # Continue with health check

            if not self.connected or not self.websocket:
                break

            try:
                # Check if token is already expired - if so, trigger full reconnection to be safe
                if self._is_token_expired():
                    _LOGGER.warning(
                        "Token has expired (not expected). Triggering full reconnection..."
                    )
                    self._handle_disconnection()
                    break
                else:
                    # Token is still valid, refresh it and wait for confirmation
                    refresh_request = {
                        "jsonrpc": "2.0",
                        "id": self._get_next_id(),
                        "method": METHOD_REFRESH_TOKEN,
                        "params": {
                            "token": self.token,
                        },
                    }

                    # Record when we sent the refresh request
                    auth_before_refresh = self._last_authentication_time
                    _LOGGER.debug("Performing health check via token refresh")
                    await self.websocket.send(json.dumps(refresh_request))

                    # Wait up to 10 seconds for the token refresh response
                    for _ in range(20):  # Check every 0.5 seconds for 10 seconds total
                        await asyncio.sleep(0.5)
                        if self._last_authentication_time > auth_before_refresh:
                            _LOGGER.debug("Health check successful - token refreshed")
                            break
                    else:
                        # No token refresh received within timeout
                        _LOGGER.warning(
                            "Health check failed - no token refresh received within 10 seconds"
                        )
                        self._handle_disconnection()
                        break

            except Exception as ex:
                _LOGGER.warning("Health check failed: %s. Triggering reconnection.", ex)
                self._handle_disconnection()
                break
