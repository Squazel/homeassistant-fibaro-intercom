"""Config flow for FIBARO Intercom integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
import websockets
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_PORT, DOMAIN
from .coordinator import FibaroIntercomCoordinator

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


class FibaroIntercomConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FIBARO Intercom."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            # Set unique ID to prevent multiple entries for same device
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            # Test connection
            try:
                coordinator = FibaroIntercomCoordinator(
                    self.hass, host, port, username, password
                )
                await coordinator.async_test_connection()

                return self.async_create_entry(
                    title=f"FIBARO Intercom ({host})",
                    data=user_input,
                )
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception as ex:
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigFlow,
    ) -> OptionsFlow:
        """Create the options flow."""
        return FibaroIntercomOptionsFlowHandler(config_entry)


class FibaroIntercomOptionsFlowHandler(OptionsFlow):
    """Handle options flow for FIBARO Intercom."""

    def __init__(self, config_entry: ConfigFlow) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PORT,
                        default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT),
                    ): cv.port,
                    vol.Optional(
                        CONF_USERNAME,
                        default=self.config_entry.data.get(CONF_USERNAME, ""),
                    ): cv.string,
                    vol.Optional(
                        CONF_PASSWORD,
                        default=self.config_entry.data.get(CONF_PASSWORD, ""),
                    ): cv.string,
                }
            ),
        )
