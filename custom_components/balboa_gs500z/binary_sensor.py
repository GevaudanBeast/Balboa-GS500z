"""Binary sensor platform for Balboa GS500Z Spa.

This module provides a binary sensor entity indicating whether the spa heater
is currently active (ON) or inactive (OFF).
"""
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
    """Set up the Balboa binary sensor platform from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry for this integration
        async_add_entities: Callback to add new entities

    Note:
        Creates a single binary sensor entity for heater status.
    """
    coordinator: BalboaDataCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    async_add_entities([BalboaHeaterSensor(coordinator, entry)], True)


class BalboaHeaterSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of the Balboa spa heater status.

    This binary sensor indicates whether the spa's heating element is currently
    active. The heater status is extracted from byte 19, bit 0 of the RS-485 frame.

    State:
        - ON: Heater is actively heating water
        - OFF: Heater is idle (target temperature reached or cycling)
    """

    _attr_has_entity_name = True
    _attr_name = "Heater"
    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(
        self, coordinator: BalboaDataCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the binary sensor.

        Args:
            coordinator: Data coordinator managing spa state
            entry: Config entry for unique ID and device info
        """
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
        """Return true if the heater is on.

        Returns:
            True if heater is active, False if idle or data unavailable

        Note:
            Uses majority vote from coordinator's sliding window validation
            (2 out of 3 frames must show heater ON).
        """
        if self.coordinator.data:
            return self.coordinator.data.get("heater_on", False)
        return False

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend.

        Returns:
            "mdi:fire" if heater is on, "mdi:fire-off" if heater is off

        Note:
            Icon changes dynamically based on heater state for visual feedback.
        """
        if self.is_on:
            return "mdi:fire"
        return "mdi:fire-off"

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if coordinator has successfully updated data, False otherwise

        Note:
            Unlike climate entity, doesn't require specific data fields.
            Entity is available as long as coordinator is receiving frames.
        """
        return self.coordinator.last_update_success and self.coordinator.data is not None
