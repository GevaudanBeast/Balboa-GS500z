"""Data coordinator for Balboa GS500Z Spa."""
from __future__ import annotations

import asyncio
import logging
import time
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

# SL memory parameters (v5.8.4)
# After stabilisation, b23 can drop to 0x00 in SL — same as ECO.
# We track recent SL detections and maintain the mode for this window.
_SL_MEMORY_WINDOW_S = 120.0   # seconds
_SL_MEMORY_MIN_OBS = 2        # minimum confirmed SL frames within the window


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
            "pump1_state": "off",
            "blower_on": False,
            "light_on": False,
        }

        # SL memory: list of monotonic timestamps when SL (b23=0x40) was confirmed
        self._sl_timestamps: list[float] = []

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

        # Check if all 3 frames agree on temperature values
        water_temps = [f["water_temp"] for f in recent_frames]
        setpoints = [f["setpoint"] for f in recent_frames]
        modes = [f["mode"] for f in recent_frames]
        heaters = [f["heater_on"] for f in recent_frames]

        if len(set(water_temps)) != 1:
            _LOGGER.debug("Water temp not consistent: %s", water_temps)
            return None

        if len(set(setpoints)) != 1:
            _LOGGER.debug("Setpoint not consistent: %s", setpoints)
            return None

        # Mode validation with SL memory and transitoire tolerance
        mode = self._validate_mode(modes)
        if mode is None:
            return None

        # Heater status — majority vote across the 3 frames
        heater_on = sum(heaters) >= 2

        # Pump and accessories — majority vote for non-critical fields
        pump_states = [f.get("pump1_state", "off") for f in recent_frames]
        pump1_state = max(set(pump_states), key=pump_states.count)

        blowers = [f.get("blower_on", False) for f in recent_frames]
        blower_on = sum(blowers) >= 2

        lights = [f.get("light_on", False) for f in recent_frames]
        light_on = sum(lights) >= 2

        validated_data = {
            "water_temp": water_temps[0],
            "setpoint": setpoints[0],
            "mode": mode,
            "heater_on": heater_on,
            "pump1_state": pump1_state,
            "blower_on": blower_on,
            "light_on": light_on,
        }

        # Order guard validation
        if self.order_guard and self._stable_data.get("mode"):
            if not self._validate_mode_transition(self._stable_data["mode"], mode):
                _LOGGER.warning(
                    "Invalid mode transition: %s -> %s (blocked by order guard)",
                    self._stable_data["mode"],
                    mode,
                )
                return None

        return validated_data

    def _validate_mode(self, modes: list[str]) -> str | None:
        """Validate mode with SL memory and transitoire tolerance (v5.8.4).

        After SL stabilises, b23 can fall back to 0x00 (indistinguishable from
        ECO).  We track timestamps of confirmed SL detections and keep the mode
        as SL for _SL_MEMORY_WINDOW_S seconds (min _SL_MEMORY_MIN_OBS frames).
        """
        # Strip transitoire frames
        valid_modes = [m for m in modes if m != "UNK"]

        if not valid_modes:
            _LOGGER.debug("All modes are UNK (transitoire)")
            return None

        if len(set(valid_modes)) == 1:
            mode = valid_modes[0]
            if mode == "SL":
                self._record_sl()
            return mode

        # If the window looks like ECO but SL memory is active -> keep SL
        apparent_eco = set(valid_modes) <= {"ECO"}
        if apparent_eco and self._sl_memory_active():
            _LOGGER.debug(
                "SL memory active (%d recent obs): maintaining SL despite b23=0x00",
                len(self._recent_sl_timestamps()),
            )
            return "SL"

        # Allow SL->ECO transition when a UNK frame sits between SL and ECO
        if set(modes) <= {"SL", "UNK", "ECO"}:
            return "ECO"

        _LOGGER.debug("Modes not consistent: %s", modes)
        return None

    def _record_sl(self) -> None:
        """Record a confirmed SL detection timestamp."""
        now = time.monotonic()
        self._sl_timestamps.append(now)
        # Prune old entries to avoid unbounded growth
        cutoff = now - _SL_MEMORY_WINDOW_S
        self._sl_timestamps = [t for t in self._sl_timestamps if t >= cutoff]

    def _recent_sl_timestamps(self) -> list[float]:
        """Return SL timestamps within the memory window."""
        cutoff = time.monotonic() - _SL_MEMORY_WINDOW_S
        return [t for t in self._sl_timestamps if t >= cutoff]

    def _sl_memory_active(self) -> bool:
        """Return True if enough recent SL observations exist to trust SL state."""
        return len(self._recent_sl_timestamps()) >= _SL_MEMORY_MIN_OBS

    def _validate_mode_transition(self, old_mode: str, new_mode: str) -> bool:
        """Validate mode transition according to VL403 order (ST->ECO->SL->ST)."""
        if old_mode == new_mode:
            return True
        valid_transitions = VALID_MODE_TRANSITIONS.get(old_mode, [])
        return new_mode in valid_transitions

    async def _async_update_data(self) -> dict[str, Any]:
        """Fallback poll — data is primarily pushed via TCP client callback."""
        if not self.client.is_connected:
            raise UpdateFailed("TCP client not connected")
        return self._stable_data

    async def async_set_temperature(self, temperature: int) -> bool:
        """Set the target temperature.

        Not yet functional — write commands are not implemented (J18 is RX-only).
        This method is a stub pending J1 bus validation.
        """
        _LOGGER.error(
            "async_set_temperature called but write commands are not implemented. "
            "J18 is read-only; awaiting J1 bus protocol validation."
        )
        return False

    async def async_set_mode(self, mode: str) -> bool:
        """Set the spa mode.

        Not yet functional — same reason as async_set_temperature.
        """
        _LOGGER.error(
            "async_set_mode called but write commands are not implemented. "
            "J18 is read-only; awaiting J1 bus protocol validation."
        )
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
