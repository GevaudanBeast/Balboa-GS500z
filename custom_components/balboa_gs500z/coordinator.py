"""Data coordinator for Balboa GS500Z Spa.

This module implements a DataUpdateCoordinator with sliding window validation for
reliable data extraction from the RS-485 stream. It uses a consensus-based approach
to filter out transient errors and ensure stable readings.

Key features:
- Sliding window validation (3-20 frames, default 5)
- 3 consecutive confirmations required for value changes
- Mode transition validation (optional order guard)
- Automatic tolerance for transient 0x60 (UNK) mode values
- Thread-safe frame handling with validation
"""
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
    MAX_WINDOW_SIZE,
    MIN_WINDOW_SIZE,
    VALID_MODE_TRANSITIONS,
)
from .tcp_client import BalboaTCPClient

_LOGGER = logging.getLogger(__name__)

# Expected keys in a valid frame from tcp_client
_REQUIRED_FRAME_KEYS = {"water_temp", "setpoint", "mode", "heater_on"}


class BalboaDataCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Balboa GS500Z data with sliding window validation."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: BalboaTCPClient,
        window_size: int = DEFAULT_WINDOW_SIZE,
        order_guard: bool = DEFAULT_ORDER_GUARD,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            client: TCP client for RS-485 communication
            window_size: Number of frames to keep in validation window (3-20)
            order_guard: Whether to validate mode transitions (ST→ECO→SL→ST)

        Raises:
            ValueError: If window_size is out of valid range
        """
        # Validate window size before initialization
        if not MIN_WINDOW_SIZE <= window_size <= MAX_WINDOW_SIZE:
            raise ValueError(
                f"window_size must be between {MIN_WINDOW_SIZE} and {MAX_WINDOW_SIZE}, "
                f"got {window_size}"
            )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),  # Fallback only, data comes via callback
        )
        self.client = client
        self.window_size = window_size
        self.order_guard = order_guard

        # Sliding window for validation (thread-safe due to GIL and deque's thread-safe append)
        self._frame_window: deque[dict[str, Any]] = deque(maxlen=window_size)

        # Validated stable data (what entities see)
        self._stable_data: dict[str, Any] = {
            "water_temp": None,
            "setpoint": None,
            "mode": None,
            "heater_on": False,
        }

        # Lock for protecting _stable_data updates (prevent race conditions)
        self._data_lock = asyncio.Lock()

        # Set the callback for TCP client
        self.client.callback = self._handle_frame

    async def _handle_frame(self, frame: dict[str, Any]) -> None:
        """Handle a new frame from the TCP client.

        This callback is called by tcp_client for each valid frame received.
        It adds the frame to the sliding window and triggers validation.

        Args:
            frame: Parsed frame data with keys: water_temp, setpoint, mode, heater_on

        Note:
            This method is called asynchronously by tcp_client. Multiple calls may
            execute concurrently, but deque.append() is thread-safe and validation
            uses a lock for _stable_data updates.
        """
        try:
            # Validate frame structure before processing
            if not self._is_valid_frame(frame):
                _LOGGER.warning("Received invalid frame structure, skipping: %s", frame)
                return

            _LOGGER.debug("Received frame: %s", frame)

            # Add to sliding window (deque.append is thread-safe)
            self._frame_window.append(frame)

            # Validate and update stable data (need at least 3 frames for consensus)
            if len(self._frame_window) >= 3:
                validated = self._validate_window()
                if validated:
                    # Use lock to prevent race conditions on _stable_data updates
                    async with self._data_lock:
                        old_data = self._stable_data.copy()
                        self._stable_data = validated

                        # Check if data actually changed before notifying entities
                        if old_data != self._stable_data:
                            _LOGGER.info("Stable data updated: %s", self._stable_data)
                            # Trigger update to entities (async_set_updated_data is thread-safe)
                            self.async_set_updated_data(self._stable_data)
                        else:
                            _LOGGER.debug("Data unchanged, no update needed")

        except Exception as err:
            # Catch-all to prevent callback crashes from breaking TCP client
            _LOGGER.error("Unexpected error handling frame: %s", err, exc_info=True)

    def _is_valid_frame(self, frame: dict[str, Any]) -> bool:
        """Validate that a frame has all required keys and reasonable values.

        Args:
            frame: Frame dictionary to validate

        Returns:
            True if frame structure is valid, False otherwise
        """
        # Check required keys are present
        if not _REQUIRED_FRAME_KEYS.issubset(frame.keys()):
            missing = _REQUIRED_FRAME_KEYS - frame.keys()
            _LOGGER.debug("Frame missing required keys: %s", missing)
            return False

        # Validate data types and ranges
        try:
            water_temp = frame["water_temp"]
            setpoint = frame["setpoint"]
            mode = frame["mode"]
            heater_on = frame["heater_on"]

            # Temperature sanity checks (same as tcp_client, but be defensive)
            if not isinstance(water_temp, (int, float)) or not (0 <= water_temp <= 60):
                _LOGGER.debug("Invalid water_temp: %s", water_temp)
                return False

            if not isinstance(setpoint, (int, float)) or not (0 <= setpoint <= 60):
                _LOGGER.debug("Invalid setpoint: %s", setpoint)
                return False

            # Mode must be a known string
            if not isinstance(mode, str) or mode not in {"ST", "ECO", "SL", "UNK"}:
                _LOGGER.debug("Invalid mode: %s", mode)
                return False

            # Heater must be boolean
            if not isinstance(heater_on, bool):
                _LOGGER.debug("Invalid heater_on: %s", heater_on)
                return False

            return True

        except (KeyError, TypeError, ValueError) as err:
            _LOGGER.debug("Frame validation error: %s", err)
            return False

    def _validate_window(self) -> dict[str, Any] | None:
        """Validate data using sliding window with 3 consecutive confirmations.

        This method implements a consensus algorithm: the last 3 frames must agree
        on temperature values, and modes must be consistent (with tolerance for
        transient UNK values). This filters out transient errors and RF noise.

        Returns:
            Validated data dictionary if consensus is reached, None otherwise

        Algorithm:
            - Temperatures: Must be identical across 3 frames
            - Setpoint: Must be identical across 3 frames
            - Mode: Allows UNK (0x60) transients, validates transitions
            - Heater: Majority vote (2 out of 3)
        """
        if len(self._frame_window) < 3:
            return None

        try:
            # Get last 3 frames for consensus check
            recent_frames = list(self._frame_window)[-3:]

            # Extract values from frames (safe - already validated by _is_valid_frame)
            water_temps = [f["water_temp"] for f in recent_frames]
            setpoints = [f["setpoint"] for f in recent_frames]
            modes = [f["mode"] for f in recent_frames]
            heaters = [f["heater_on"] for f in recent_frames]

            # Temperature consistency check (must be identical)
            if len(set(water_temps)) != 1:
                _LOGGER.debug("Water temp not consistent: %s", water_temps)
                return None

            # Setpoint consistency check (must be identical)
            if len(set(setpoints)) != 1:
                _LOGGER.debug("Setpoint not consistent: %s", setpoints)
                return None

            # Mode validation with transient tolerance (allows UNK mode)
            mode = self._validate_mode(modes)
            if mode is None:
                return None

            # Heater status - majority vote (handles brief flickering)
            heater_on = sum(heaters) >= 2

            validated_data = {
                "water_temp": water_temps[0],
                "setpoint": setpoints[0],
                "mode": mode,
                "heater_on": heater_on,
            }

            # Order guard validation (enforces ST→ECO→SL→ST transitions if enabled)
            if self.order_guard and self._stable_data.get("mode"):
                if not self._validate_mode_transition(self._stable_data["mode"], mode):
                    _LOGGER.warning(
                        "Invalid mode transition: %s → %s (blocked by order guard)",
                        self._stable_data["mode"],
                        mode,
                    )
                    return None

            return validated_data

        except (KeyError, TypeError, ValueError) as err:
            # Should never happen if _is_valid_frame works correctly, but be defensive
            _LOGGER.error("Unexpected error during validation: %s", err, exc_info=True)
            return None

    def _validate_mode(self, modes: list[str]) -> str | None:
        """Validate mode with transient (UNK) tolerance.

        The spa occasionally sends 0x60 (UNK) mode bytes during transitions.
        This method filters those out and validates the remaining modes.

        Args:
            modes: List of 3 mode strings from recent frames

        Returns:
            Validated mode string if consistent, None if inconsistent

        Special cases handled:
            - All UNK: Return None (wait for stable mode)
            - Mixed UNK with consistent real modes: Return the real mode
            - SL→UNK→ECO sequence: Valid transition, return ECO
            - ECO→UNK→ECO: Brief transient, return ECO
        """
        # Remove UNK (transient 0x60) modes to find the stable mode
        valid_modes = [m for m in modes if m != "UNK"]

        if not valid_modes:
            _LOGGER.debug("All modes are UNK (transient), waiting for stable mode")
            return None

        # Check if remaining modes are consistent (all the same)
        if len(set(valid_modes)) == 1:
            return valid_modes[0]

        # Special case: Allow SL→ECO transition with UNK in between
        # This is a valid mode change pattern observed in real captures
        if set(modes) == {"SL", "UNK", "ECO"} or set(modes) == {"ECO", "UNK"}:
            return "ECO"

        # Modes are inconsistent and not a known transient pattern
        _LOGGER.debug("Modes not consistent: %s", modes)
        return None

    def _validate_mode_transition(self, old_mode: str, new_mode: str) -> bool:
        """Validate mode transition according to VL403 keypad order.

        The VL403 keypad enforces a specific order: ST → ECO → SL → ST.
        This validation prevents accepting invalid transitions that might
        indicate corrupted data or unexpected behavior.

        Args:
            old_mode: Previous validated mode
            new_mode: New mode to validate

        Returns:
            True if transition is valid or modes are the same, False otherwise

        Valid transitions:
            - ST → ECO
            - ECO → SL or ECO → ST
            - SL → ST
        """
        if old_mode == new_mode:
            return True

        # Check against valid transition map from const.py
        valid_transitions = VALID_MODE_TRANSITIONS.get(old_mode, [])
        is_valid = new_mode in valid_transitions

        if not is_valid:
            _LOGGER.debug(
                "Mode transition %s → %s not in valid transitions: %s",
                old_mode,
                new_mode,
                valid_transitions,
            )

        return is_valid

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint.

        This is a fallback method required by DataUpdateCoordinator. In normal
        operation, data is pushed via TCP client callback (_handle_frame), not
        pulled via this method.

        Returns:
            Current stable data dictionary

        Raises:
            UpdateFailed: If TCP client is not connected
        """
        if not self.client.is_connected:
            raise UpdateFailed("TCP client not connected")

        # Return current stable data (updated via callback, not polled)
        async with self._data_lock:
            return self._stable_data.copy()

    # ==================================================================================
    # WRITE COMMANDS - NOT SUPPORTED
    # ==================================================================================
    # These methods are not functional. RS-485 write operations do not work with
    # the VL403 keypad (uses proprietary protocol). See IR_CONTROL.md for alternatives.
    # ==================================================================================

    async def async_set_temperature(self, temperature: int) -> bool:
        """Set the target temperature.

        ⚠️ NOT SUPPORTED: RS-485 write operations are not functional.
        Use physical VL403 keypad or IR control (ESP32). See IR_CONTROL.md.
        """
        _LOGGER.error(
            "async_set_temperature not supported. VL403 uses proprietary protocol. "
            "Use physical keypad or IR control (ESP32). See IR_CONTROL.md"
        )
        return False

    async def async_set_mode(self, mode: str) -> bool:
        """Set the spa mode.

        ⚠️ NOT SUPPORTED: RS-485 write operations are not functional.
        Use physical VL403 keypad or IR control (ESP32). See IR_CONTROL.md.
        """
        _LOGGER.error(
            "async_set_mode not supported. VL403 uses proprietary protocol. "
            "Use physical keypad or IR control (ESP32). See IR_CONTROL.md"
        )
        return False

    @property
    def stable_data(self) -> dict[str, Any]:
        """Get the current stable data.

        Returns:
            Dictionary with current validated values (water_temp, setpoint, mode, heater_on)

        Note:
            This property is read-only. Values are updated via _handle_frame callback.
        """
        return self._stable_data

    def update_options(self, window_size: int, order_guard: bool) -> None:
        """Update coordinator options (called when user changes settings).

        Args:
            window_size: New window size (must be between MIN_WINDOW_SIZE and MAX_WINDOW_SIZE)
            order_guard: New order guard setting

        Raises:
            ValueError: If window_size is out of valid range

        Note:
            Changing window_size preserves existing frames but adjusts the deque capacity.
            If new size is smaller, oldest frames are automatically dropped.
        """
        # Validate window size
        if not MIN_WINDOW_SIZE <= window_size <= MAX_WINDOW_SIZE:
            raise ValueError(
                f"window_size must be between {MIN_WINDOW_SIZE} and {MAX_WINDOW_SIZE}, "
                f"got {window_size}"
            )

        # Update settings
        self.window_size = window_size
        self.order_guard = order_guard

        # Recreate deque with new maxlen (preserves existing frames, drops oldest if needed)
        self._frame_window = deque(self._frame_window, maxlen=window_size)

        _LOGGER.info(
            "Options updated: window_size=%d, order_guard=%s", window_size, order_guard
        )
