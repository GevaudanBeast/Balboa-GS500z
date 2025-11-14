"""Climate platform for Balboa GS500Z Spa.

This module provides the climate entity for Home Assistant, representing the spa
as a thermostat with temperature and mode (preset) information.

READ-ONLY MODE: This integration cannot control the spa via RS-485.
The VL403 keypad uses a proprietary protocol. See IR_CONTROL.md for control options.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CLIMATE_ENTITY_ID,
    COORDINATOR,
    DOMAIN,
    HA_TO_RS485_MODE,
    HVAC_MODE_ECO,
    HVAC_MODE_SL,
    HVAC_MODE_ST,
    RS485_TO_HA_MODE,
)
from .coordinator import BalboaDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Balboa climate platform from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry for this integration
        async_add_entities: Callback to add new entities

    Note:
        Creates a single climate entity representing the spa.
    """
    coordinator: BalboaDataCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    async_add_entities([BalboaClimate(coordinator, entry)], True)


class BalboaClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Balboa GS500Z Spa as a climate device.

    READ-ONLY MODE: This integration cannot write to the RS-485 bus.
    The VL403 keypad uses a proprietary protocol, not standard RS-485 commands.
    Control must be done via the physical keypad or future IR remote (ESP32).
    """

    _attr_has_entity_name = True
    _attr_name = "Spa"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT]  # Spa is always in heat mode
    _attr_preset_modes = [HVAC_MODE_ST, HVAC_MODE_ECO, HVAC_MODE_SL]
    # READ-ONLY: No write features supported (VL403 uses proprietary protocol)
    _attr_supported_features = 0
    _attr_target_temperature_step = 1
    _attr_min_temp = 15
    _attr_max_temp = 40

    def __init__(
        self, coordinator: BalboaDataCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the climate device.

        Args:
            coordinator: Data coordinator managing spa state
            entry: Config entry for unique ID and device info

        Note:
            This entity is read-only (no temperature or mode control).
            Supported features is set to 0 to indicate no write operations.
        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{CLIMATE_ENTITY_ID}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Balboa GS500Z Spa",
            "manufacturer": "Balboa",
            "model": "GS500Z",
        }

    @property
    def current_temperature(self) -> float | None:
        """Return the current water temperature in °C.

        Returns:
            Current water temperature from RS-485 data, or None if unavailable

        Note:
            Temperature is validated by coordinator (10-50°C range typically).
        """
        if self.coordinator.data:
            return self.coordinator.data.get("water_temp")
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature setpoint in °C.

        Returns:
            Target temperature from RS-485 data, or None if unavailable

        Note:
            This is read-only. Cannot be changed via RS-485 (VL403 proprietary protocol).
        """
        if self.coordinator.data:
            return self.coordinator.data.get("setpoint")
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode.

        Returns:
            Always HVACMode.HEAT (spa is always heating to maintain temperature)

        Note:
            The spa doesn't have an off mode - it's always maintaining temperature.
        """
        # Spa is always in heat mode
        return HVACMode.HEAT

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode (ST/ECO/SL).

        Returns:
            Current operating mode string, or None if unavailable
            - "standard": ST mode (0x20) - full heating
            - "eco": ECO mode (0x00) - economy mode
            - "sleep": SL mode (0x40) - sleep mode

        Note:
            ECO mode automatically alternates between ST/ECO/SL for efficiency.
            This is read-only. Use physical keypad or IR control to change.
        """
        if self.coordinator.data:
            rs485_mode = self.coordinator.data.get("mode")
            if rs485_mode and rs485_mode != "UNK":
                # Map RS-485 mode (ST/ECO/SL) to Home Assistant preset mode
                return RS485_TO_HA_MODE.get(rs485_mode, HVAC_MODE_ST)
        return None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode (not supported - read-only).

        Args:
            hvac_mode: Requested HVAC mode

        Note:
            This is a no-op. The spa is always in heat mode and cannot be turned off.
            This method exists to satisfy the ClimateEntity interface.
        """
        # Spa only supports heat mode, so this is a no-op
        _LOGGER.debug("HVAC mode change requested: %s (no action taken)", hvac_mode)

    # ==================================================================================
    # WRITE METHODS - NOT IMPLEMENTED (READ-ONLY MODE)
    # ==================================================================================
    # async_set_temperature and async_set_preset_mode are intentionally not implemented.
    # The VL403 keypad uses a proprietary protocol that cannot be written to via RS-485.
    #
    # To control the spa, use:
    # - Physical VL403 keypad (direct control)
    # - IR remote control via ESP32/ESPHome (see IR_CONTROL.md)
    # ==================================================================================

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend.

        Returns:
            Material Design Icon name for hot tub
        """
        return "mdi:hot-tub"

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if coordinator has valid data with water temperature, False otherwise

        Note:
            Entity is considered unavailable if:
            - Last coordinator update failed
            - Water temperature data is missing (indicates no valid frames received)
        """
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.get("water_temp") is not None
        )
