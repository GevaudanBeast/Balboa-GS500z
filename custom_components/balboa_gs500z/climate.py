"""Climate platform for Balboa GS500Z Spa."""
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
    """Set up the Balboa climate platform."""
    coordinator: BalboaDataCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    async_add_entities([BalboaClimate(coordinator, entry)], True)


class BalboaClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Balboa GS500Z Spa as a climate device."""

    _attr_has_entity_name = True
    _attr_name = "Spa"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT]  # Spa is always in heat mode
    _attr_preset_modes = [HVAC_MODE_ST, HVAC_MODE_ECO, HVAC_MODE_SL]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )
    _attr_target_temperature_step = 1
    _attr_min_temp = 15
    _attr_max_temp = 40

    def __init__(
        self, coordinator: BalboaDataCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the climate device."""
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
        """Return the current temperature."""
        if self.coordinator.data:
            return self.coordinator.data.get("water_temp")
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if self.coordinator.data:
            return self.coordinator.data.get("setpoint")
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        # Spa is always in heat mode
        return HVACMode.HEAT

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode (ST/ECO/SL)."""
        if self.coordinator.data:
            rs485_mode = self.coordinator.data.get("mode")
            if rs485_mode:
                return RS485_TO_HA_MODE.get(rs485_mode, HVAC_MODE_ST)
        return None

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        _LOGGER.info("Setting target temperature to %s°C", temperature)
        await self.coordinator.async_set_temperature(int(temperature))

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        # Spa only supports heat mode, so this is a no-op
        _LOGGER.debug("HVAC mode change requested: %s (no action taken)", hvac_mode)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode (ST/ECO/SL)."""
        _LOGGER.info("Setting preset mode to %s", preset_mode)

        # Convert HA mode to RS-485 mode
        rs485_mode = HA_TO_RS485_MODE.get(preset_mode)
        if rs485_mode is None:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)
            return

        # Map back to protocol mode name
        mode_names = {
            HVAC_MODE_ST: "ST",
            HVAC_MODE_ECO: "ECO",
            HVAC_MODE_SL: "SL",
        }
        target_mode = mode_names.get(preset_mode)

        if target_mode:
            await self.coordinator.async_set_mode(target_mode)

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:hot-tub"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("water_temp") is not None
        )
