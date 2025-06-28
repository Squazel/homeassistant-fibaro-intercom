"""The FIBARO Intercom integration."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.http import StaticPathConfig
import homeassistant.helpers.config_validation as cv

from .const import ATTR_RELAY, ATTR_TIMEOUT, DEFAULT_PORT, DOMAIN
from .coordinator import FibaroIntercomCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
]

# Service schema
SERVICE_OPEN_RELAY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_RELAY): vol.All(vol.Coerce(int), vol.Range(min=0, max=1)),
        vol.Optional(ATTR_TIMEOUT): vol.All(
            vol.Coerce(int), vol.Range(min=250, max=30000)
        ),
    }
)

# Config schema - integration only configurable via config entries
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the FIBARO Intercom component."""
    # Register frontend resources for custom card
    await _async_register_frontend_card(hass)
    return True


async def _async_register_frontend_card(hass: HomeAssistant) -> None:
    """Register the frontend card resources."""
    try:
        # Get the path to our frontend directory
        frontend_path = Path(__file__).parent / "frontend"
        card_file = frontend_path / "fibaro-intercom-card.js"

        if not card_file.exists():
            _LOGGER.error("FIBARO Intercom card file not found: %s", card_file)
            return

        # Register the static path for the frontend directory
        await hass.http.async_register_static_paths(
            [StaticPathConfig(f"/{DOMAIN}", str(frontend_path), cache_headers=False)]
        )

        # Use the frontend.add_extra_js_url method to automatically load the card
        # This is the standard way integrations register custom cards
        card_url = f"/{DOMAIN}/fibaro-intercom-card.js"

        # Add to frontend extra JS URLs
        hass.components.frontend.add_extra_js_url(hass, card_url)

        _LOGGER.info("FIBARO Intercom card registered automatically at: %s", card_url)

    except Exception as err:
        _LOGGER.error("Failed to register FIBARO Intercom card: %s", err)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FIBARO Intercom from a config entry."""
    _LOGGER.debug("Setting up FIBARO Intercom integration")

    # Get configuration data
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    port = DEFAULT_PORT  # Always use default port

    # Create coordinator
    coordinator = FibaroIntercomCoordinator(hass, host, port, username, password)

    # Test connection and start coordinator
    try:
        await coordinator.async_test_connection()
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed to connect to FIBARO Intercom: %s", err)
        return False

    # Store coordinator in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register services (only once)
    if not hass.services.has_service(DOMAIN, "open_relay"):

        async def async_open_relay_service(call: ServiceCall) -> None:
            """Handle open_relay service call."""
            relay = call.data[ATTR_RELAY]
            timeout = call.data.get(ATTR_TIMEOUT)

            # Find the coordinator for the first configured device
            # In practice, you might want to support targeting specific devices
            for coordinator_data in hass.data[DOMAIN].values():
                if isinstance(coordinator_data, FibaroIntercomCoordinator):
                    await coordinator_data.async_open_relay(relay, timeout)
                    break

        hass.services.async_register(
            DOMAIN,
            "open_relay",
            async_open_relay_service,
            schema=SERVICE_OPEN_RELAY_SCHEMA,
        )

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Start the coordinator connection
    await coordinator.async_connect()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading FIBARO Intercom integration")

    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Stop coordinator and remove from hass data
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_disconnect()

        # Remove services if this was the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "open_relay")

    return unload_ok
