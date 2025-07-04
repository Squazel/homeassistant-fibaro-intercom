"""Camera platform for FIBARO Intercom integration."""

from __future__ import annotations

import logging

from homeassistant.components.mjpeg.camera import MjpegCamera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import HTTP_BASIC_AUTHENTICATION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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

    # Build URLs for the MJPEG camera
    mjpeg_url = f"http://{coordinator.host}:{CAMERA_PORT}{CAMERA_LIVE_MJPEG}"
    still_image_url = f"http://{coordinator.host}:{CAMERA_PORT}{CAMERA_STILL_JPEG}"

    entities = [
        MjpegCamera(
            name="FIBARO Intercom Camera",
            mjpeg_url=mjpeg_url,
            still_image_url=still_image_url,
            authentication=HTTP_BASIC_AUTHENTICATION,
            username=coordinator.username,
            password=coordinator.password,
            verify_ssl=False,
            unique_id=f"{config_entry.entry_id}_{ENTITY_CAMERA}",
            device_info=DeviceInfo(
                identifiers={(DOMAIN, config_entry.entry_id)},
                name="FIBARO Intercom",
                manufacturer="FIBARO",
                model="Intercom",
                sw_version="1.0",
            ),
        )
    ]

    async_add_entities(entities)
