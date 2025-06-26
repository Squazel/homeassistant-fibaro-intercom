"""Binary sensor platform for FIBARO Intercom integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (BinarySensorDeviceClass,
                                                    BinarySensorEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_CONNECTION_STATUS, ENTITY_DOORBELL
from .coordinator import FibaroIntercomCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FIBARO Intercom binary sensors."""
    coordinator: FibaroIntercomCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        FibaroIntercomConnectionSensor(coordinator, config_entry),
        FibaroIntercomDoorbellSensor(coordinator, config_entry),
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
            "name": f"FIBARO Intercom ({coordinator.host})",
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
            "Connection Status",
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


class FibaroIntercomDoorbellSensor(FibaroIntercomBinarySensor):
    """Binary sensor for FIBARO Intercom doorbell."""

    def __init__(
        self,
        coordinator: FibaroIntercomCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the doorbell sensor."""
        super().__init__(
            coordinator,
            config_entry,
            ENTITY_DOORBELL,
            "Doorbell",
            BinarySensorDeviceClass.OCCUPANCY,
        )

    @property
    def is_on(self) -> bool:
        """Return True if doorbell is pressed."""
        return (
            self.coordinator.data.get("doorbell_pressed", False)
            if self.coordinator.data
            else False
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.data.get("connected", False)
            if self.coordinator.data
            else False
        )
