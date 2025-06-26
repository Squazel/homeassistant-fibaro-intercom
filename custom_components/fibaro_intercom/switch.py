"""Switch platform for FIBARO Intercom integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_RELAY_PREFIX
from .coordinator import FibaroIntercomCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FIBARO Intercom switches."""
    coordinator: FibaroIntercomCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        FibaroIntercomRelaySwitch(coordinator, config_entry, 0),
        FibaroIntercomRelaySwitch(coordinator, config_entry, 1),
    ]

    async_add_entities(entities)


class FibaroIntercomRelaySwitch(CoordinatorEntity, SwitchEntity):
    """Switch for FIBARO Intercom relay control."""

    def __init__(
        self,
        coordinator: FibaroIntercomCoordinator,
        config_entry: ConfigEntry,
        relay_number: int,
    ) -> None:
        """Initialize the relay switch."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._relay_number = relay_number
        self._attr_unique_id = (
            f"{config_entry.entry_id}_{ENTITY_RELAY_PREFIX}{relay_number}"
        )
        self._attr_name = f"Relay {relay_number}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"FIBARO Intercom ({coordinator.host})",
            "manufacturer": "FIBARO",
            "model": "Intercom",
            "sw_version": "1.0",
        }

    @property
    def is_on(self) -> bool:
        """Return True if relay is on."""
        if not self.coordinator.data:
            return False
        relay_states = self.coordinator.data.get("relay_states", {})
        return relay_states.get(self._relay_number, False)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.data.get("connected", False)
            if self.coordinator.data
            else False
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the relay on."""
        await self.coordinator.async_open_relay(self._relay_number)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the relay off - not supported by FIBARO Intercom."""
        # FIBARO Intercom relays are momentary, they can't be turned off
        # This is here for interface compatibility but does nothing
        pass
