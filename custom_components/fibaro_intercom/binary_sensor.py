"""Binary sensor platform for FIBARO Intercom integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_CONNECTION_STATUS, ENTITY_RELAY_PREFIX
from .coordinator import FibaroIntercomCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FIBARO Intercom binary sensors."""
    coordinator: FibaroIntercomCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create device registry entry for device triggers
    from homeassistant.helpers import device_registry as dr

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.entry_id)},
        name="FIBARO Intercom",
        manufacturer="FIBARO",
        model="Intercom",
        sw_version="1.0",
    )
    coordinator.set_device_id(device.id)

    entities = [
        FibaroIntercomConnectionSensor(coordinator, config_entry),
        FibaroIntercomRelaySensor(coordinator, config_entry, 0),
        FibaroIntercomRelaySensor(coordinator, config_entry, 1),
    ]

    async_add_entities(entities)


class FibaroIntercomBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class for FIBARO Intercom binary sensors."""

    def __init__(
        self,
        coordinator: FibaroIntercomCoordinator,
        config_entry: ConfigEntry,
        entity_id: str,
        name: str,
        device_class: BinarySensorDeviceClass | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_id}"
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "FIBARO Intercom",
            "manufacturer": "FIBARO",
            "model": "Intercom",
            "sw_version": "1.0",
        }


class FibaroIntercomConnectionSensor(FibaroIntercomBinarySensor):
    """Binary sensor for FIBARO Intercom connection status."""

    def __init__(
        self,
        coordinator: FibaroIntercomCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the connection sensor."""
        super().__init__(
            coordinator,
            config_entry,
            ENTITY_CONNECTION_STATUS,
            "FIBARO Intercom Connection Status",
            BinarySensorDeviceClass.CONNECTIVITY,
        )

    @property
    def is_on(self) -> bool:
        """Return True if connected."""
        return (
            self.coordinator.data.get("connected", False)
            if self.coordinator.data
            else False
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True  # This sensor shows connection status, so it's always available


class FibaroIntercomRelaySensor(FibaroIntercomBinarySensor):
    """Binary sensor for FIBARO Intercom relay state."""

    def __init__(
        self,
        coordinator: FibaroIntercomCoordinator,
        config_entry: ConfigEntry,
        relay_number: int,
    ) -> None:
        super().__init__(
            coordinator,
            config_entry,
            f"{ENTITY_RELAY_PREFIX}{relay_number}",
            f"FIBARO Intercom Relay {relay_number}",
            BinarySensorDeviceClass.POWER,
        )
        self._relay_number = relay_number

    @property
    def is_on(self) -> bool:
        """Return True if relay is on (as reported by the intercom)."""
        if not self.coordinator.data:
            return False
        relay_states = self.coordinator.data.get("relay_states", {})
        return relay_states.get(self._relay_number, False)

    @property
    def icon(self) -> str:
        """Return the icon for this relay."""
        if self._relay_number == 0:
            return "mdi:door"
        elif self._relay_number == 1:
            return "mdi:gate"
        else:
            return "mdi:electric-switch"

    @property
    def available(self) -> bool:
        """Return True if entity is available (connected to intercom)."""
        return (
            self.coordinator.data.get("connected", False)
            if self.coordinator.data
            else False
        )
