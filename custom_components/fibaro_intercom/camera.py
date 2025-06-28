"""Camera platform for FIBARO Intercom integration."""

from __future__ import annotations

import asyncio
import logging

from aiohttp import BasicAuth
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CAMERA_LIVE_MJPEG,
    CAMERA_PORT,
    CAMERA_STILL_JPEG,
    DOMAIN,
    ENTITY_CAMERA,
)
from .coordinator import FibaroIntercomCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FIBARO Intercom camera."""
    coordinator: FibaroIntercomCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        FibaroIntercomCamera(coordinator, config_entry),
    ]

    async_add_entities(entities)


class FibaroIntercomCamera(CoordinatorEntity, Camera):
    """Camera entity for FIBARO Intercom."""

    def __init__(
        self,
        coordinator: FibaroIntercomCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the camera."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_{ENTITY_CAMERA}"
        self._attr_name = "FIBARO Intercom Camera"

        # Required attributes for Home Assistant camera
        # Initialize with a dummy token to prevent IndexError
        # FIBARO Intercom uses HTTP Basic Auth, not token-based access
        self.access_tokens: list[str] = ["basic_auth"]
        self._webrtc_provider = None
        # Required in newer Home Assistant versions - FIBARO Intercom uses MJPEG, not WebRTC
        self._supports_native_async_webrtc = False

        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "FIBARO Intercom",
            "manufacturer": "FIBARO",
            "model": "Intercom",
            "sw_version": "1.0",
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.data.get("connected", False)
            if self.coordinator.data
            else False
        )

    @property
    def entity_picture(self) -> str | None:
        """Return entity picture URL or None."""
        # FIBARO Intercom uses HTTP Basic Auth, not access tokens
        # Return None to avoid access_tokens[-1] IndexError
        return None

    @property
    def state_attributes(self) -> dict[str, str] | None:
        """Return state attributes."""
        # Override to handle access tokens for FIBARO Intercom
        # Return None to avoid including dummy access token in state
        return None

    @property
    def supported_features(self) -> int:
        """Return supported features."""
        from homeassistant.components.camera import CameraEntityFeature

        return CameraEntityFeature.STREAM

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        if not self.available:
            return None

        try:
            session = async_get_clientsession(self.hass, verify_ssl=False)
            auth = BasicAuth(self.coordinator.username, self.coordinator.password)
            url = f"http://{self.coordinator.host}:{CAMERA_PORT}{CAMERA_STILL_JPEG}"

            async with session.get(url, auth=auth, timeout=10) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    _LOGGER.warning(
                        "Failed to fetch camera image: HTTP %s", response.status
                    )
                    return None

        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout fetching camera image")
            return None
        except Exception as ex:
            _LOGGER.error("Error fetching camera image: %s", ex)
            return None

    async def stream_source(self) -> str | None:
        """Return the source of the stream."""
        if not self.available:
            return None

        # Return MJPEG stream URL with authentication
        return (
            f"http://{self.coordinator.username}:{self.coordinator.password}@"
            f"{self.coordinator.host}:{CAMERA_PORT}{CAMERA_LIVE_MJPEG}"
        )
