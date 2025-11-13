"""Binary sensor platform for Balboa GS500Z Spa."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COORDINATOR, DOMAIN, HEATER_SENSOR_ID
from .coordinator import BalboaDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Balboa binary sensor platform."""
    coordinator: BalboaDataCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    async_add_entities([BalboaHeaterSensor(coordinator, entry)], True)


class BalboaHeaterSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of the Balboa spa heater status."""

    _attr_has_entity_name = True
    _attr_name = "Heater"
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(
        self, coordinator: BalboaDataCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{HEATER_SENSOR_ID}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Balboa GS500Z Spa",
            "manufacturer": "Balboa",
            "model": "GS500Z",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the heater is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("heater_on", False)
        return False

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        if self.is_on:
            return "mdi:fire"
        return "mdi:fire-off"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
