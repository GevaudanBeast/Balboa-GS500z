"""Data coordinator for Balboa GS500Z Spa."""
from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ORDER_GUARD,
    CONF_WINDOW_SIZE,
    DEFAULT_ORDER_GUARD,
    DEFAULT_WINDOW_SIZE,
    DOMAIN,
    VALID_MODE_TRANSITIONS,
)
from .tcp_client import BalboaTCPClient

_LOGGER = logging.getLogger(__name__)


class BalboaDataCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Balboa GS500Z data with sliding window validation."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: BalboaTCPClient,
        window_size: int = DEFAULT_WINDOW_SIZE,
        order_guard: bool = DEFAULT_ORDER_GUARD,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),  # Fallback only
        )
        self.client = client
        self.window_size = window_size
        self.order_guard = order_guard

        # Sliding window for validation
        self._frame_window: deque = deque(maxlen=window_size)

        # Validated stable data
        self._stable_data: dict[str, Any] = {
            "water_temp": None,
            "setpoint": None,
            "mode": None,
            "heater_on": False,
        }

        # Set the callback for TCP client
        self.client.callback = self._handle_frame

    async def _handle_frame(self, frame: dict) -> None:
        """Handle a new frame from the TCP client."""
        _LOGGER.debug("Received frame: %s", frame)

        # Add to sliding window
        self._frame_window.append(frame)

        # Validate and update stable data
        if len(self._frame_window) >= 3:  # Need at least 3 frames
            validated = self._validate_window()
            if validated:
                old_data = self._stable_data.copy()
                self._stable_data = validated

                # Check if data actually changed
                if old_data != self._stable_data:
                    _LOGGER.info("Stable data updated: %s", self._stable_data)
                    # Trigger update to entities
                    self.async_set_updated_data(self._stable_data)
                else:
                    _LOGGER.debug("Data unchanged, no update needed")

    def _validate_window(self) -> dict[str, Any] | None:
        """Validate data using sliding window with 3 consecutive confirmations."""
        if len(self._frame_window) < 3:
            return None

        # Get last 3 frames
        recent_frames = list(self._frame_window)[-3:]

        # Check if all 3 frames agree on the values
        water_temps = [f["water_temp"] for f in recent_frames]
        setpoints = [f["setpoint"] for f in recent_frames]
        modes = [f["mode"] for f in recent_frames]
        heaters = [f["heater_on"] for f in recent_frames]

        # Check consistency
        if len(set(water_temps)) != 1:
            _LOGGER.debug("Water temp not consistent: %s", water_temps)
            return None

        if len(set(setpoints)) != 1:
            _LOGGER.debug("Setpoint not consistent: %s", setpoints)
            return None

        # Mode validation with transitoire tolerance
        mode = self._validate_mode(modes)
        if mode is None:
            return None

        # Heater status - majority vote
        heater_on = sum(heaters) >= 2

        validated_data = {
            "water_temp": water_temps[0],
            "setpoint": setpoints[0],
            "mode": mode,
            "heater_on": heater_on,
        }

        # Order guard validation
        if self.order_guard and self._stable_data.get("mode"):
            if not self._validate_mode_transition(self._stable_data["mode"], mode):
                _LOGGER.warning(
                    "Invalid mode transition: %s → %s (blocked by order guard)",
                    self._stable_data["mode"],
                    mode,
                )
                return None

        return validated_data

    def _validate_mode(self, modes: list[str]) -> str | None:
        """Validate mode with transitoire tolerance."""
        # Remove UNK (transitoire) modes
        valid_modes = [m for m in modes if m != "UNK"]

        if not valid_modes:
            _LOGGER.debug("All modes are UNK (transitoire)")
            return None

        # Check if remaining modes are consistent
        if len(set(valid_modes)) == 1:
            return valid_modes[0]

        # Allow SL→ECO transition if there's a UNK in between
        if set(modes) == {"SL", "UNK", "ECO"} or set(modes) == {"ECO", "UNK"}:
            return "ECO"

        _LOGGER.debug("Modes not consistent: %s", modes)
        return None

    def _validate_mode_transition(self, old_mode: str, new_mode: str) -> bool:
        """Validate mode transition according to VL403 order."""
        if old_mode == new_mode:
            return True

        # Check if transition is valid (ST → ECO → SL → ST)
        valid_transitions = VALID_MODE_TRANSITIONS.get(old_mode, [])
        return new_mode in valid_transitions

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint.

        This is a fallback method. Data is primarily pushed via TCP client callback.
        """
        if not self.client.is_connected:
            raise UpdateFailed("TCP client not connected")

        # Return current stable data
        return self._stable_data

    async def async_set_temperature(self, temperature: int) -> bool:
        """Set the target temperature."""
        try:
            command = self.client.build_setpoint_command(temperature)
            success = await self.client.send_command(command)

            if success:
                _LOGGER.info("Setpoint command sent: %d°C", temperature)
            else:
                _LOGGER.error("Failed to send setpoint command")

            return success

        except Exception as err:
            _LOGGER.error("Error setting temperature: %s", err)
            return False

    async def async_set_mode(self, mode: str) -> bool:
        """Set the spa mode."""
        try:
            current_mode = self._stable_data.get("mode")
            if not current_mode:
                _LOGGER.error("Current mode unknown, cannot set mode")
                return False

            # Validate transition if order guard is enabled
            if self.order_guard:
                if not self._validate_mode_transition(current_mode, mode):
                    _LOGGER.error(
                        "Invalid mode transition: %s → %s (blocked by order guard)",
                        current_mode,
                        mode,
                    )
                    return False

            command = self.client.build_mode_command(current_mode, mode)
            if command is None:
                return True  # Already in target mode

            success = await self.client.send_command(command)

            if success:
                _LOGGER.info("Mode command sent: %s → %s", current_mode, mode)
            else:
                _LOGGER.error("Failed to send mode command")

            return success

        except Exception as err:
            _LOGGER.error("Error setting mode: %s", err)
            return False

    @property
    def stable_data(self) -> dict[str, Any]:
        """Get the current stable data."""
        return self._stable_data

    def update_options(self, window_size: int, order_guard: bool) -> None:
        """Update coordinator options."""
        self.window_size = window_size
        self.order_guard = order_guard
        self._frame_window = deque(self._frame_window, maxlen=window_size)
        _LOGGER.info(
            "Options updated: window_size=%d, order_guard=%s", window_size, order_guard
        )
