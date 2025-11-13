"""TCP client for Balboa GS500Z RS-485 communication via EW11A."""
import asyncio
import logging
from typing import Callable, Optional
from collections.abc import Awaitable

from .const import (
    FRAME_HEADER,
    FRAME_LENGTH,
    MODE_ECO,
    MODE_SL,
    MODE_ST,
    MODE_UNK,
    RECONNECT_DELAY,
    CONNECTION_TIMEOUT,
    TEMP_MULTIPLIER,
)

_LOGGER = logging.getLogger(__name__)


class BalboaTCPClient:
    """TCP client for EW11A RS-485 bridge."""

    def __init__(
        self,
        host: str,
        port: int,
        callback: Optional[Callable[[dict], Awaitable[None]]] = None,
    ) -> None:
        """Initialize the TCP client."""
        self.host = host
        self.port = port
        self.callback = callback
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._running = False
        self._read_task: Optional[asyncio.Task] = None
        self._buffer = bytearray()
        self._last_frame: Optional[dict] = None

    async def connect(self) -> bool:
        """Connect to the EW11A."""
        try:
            _LOGGER.info("Connecting to %s:%s", self.host, self.port)
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=CONNECTION_TIMEOUT,
            )
            _LOGGER.info("Connected to %s:%s", self.host, self.port)
            return True
        except asyncio.TimeoutError:
            _LOGGER.error("Connection timeout to %s:%s", self.host, self.port)
            return False
        except OSError as err:
            _LOGGER.error("Connection error to %s:%s: %s", self.host, self.port, err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the EW11A."""
        self._running = False
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            self._read_task = None

        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as err:
                _LOGGER.debug("Error closing writer: %s", err)
            self._writer = None
            self._reader = None
        _LOGGER.info("Disconnected from %s:%s", self.host, self.port)

    async def start(self) -> None:
        """Start the TCP client with auto-reconnect."""
        self._running = True
        while self._running:
            if await self.connect():
                self._read_task = asyncio.create_task(self._read_loop())
                try:
                    await self._read_task
                except asyncio.CancelledError:
                    break
                except Exception as err:
                    _LOGGER.error("Read loop error: %s", err)

            if self._running:
                _LOGGER.info("Reconnecting in %s seconds...", RECONNECT_DELAY)
                await asyncio.sleep(RECONNECT_DELAY)

    async def _read_loop(self) -> None:
        """Read loop for incoming data."""
        try:
            while self._running and self._reader:
                data = await self._reader.read(1024)
                if not data:
                    _LOGGER.warning("Connection closed by remote host")
                    break

                self._buffer.extend(data)
                self._process_buffer()

        except asyncio.CancelledError:
            raise
        except Exception as err:
            _LOGGER.error("Error in read loop: %s", err)
            raise

    def _process_buffer(self) -> None:
        """Process the buffer to extract frames."""
        while len(self._buffer) >= FRAME_LENGTH:
            # Look for frame start
            start_idx = self._find_frame_start()
            if start_idx is None:
                # No valid frame header found, clear buffer
                self._buffer.clear()
                break

            # Remove data before frame start
            if start_idx > 0:
                self._buffer = self._buffer[start_idx:]

            # Check if we have a complete frame
            if len(self._buffer) < FRAME_LENGTH * 2:  # 27 bytes = 54 hex chars
                # Wait for more data
                break

            # Extract potential frame (looking for [....])
            frame_str = self._buffer.decode("ascii", errors="ignore")
            start_bracket = frame_str.find("[")
            end_bracket = frame_str.find("]", start_bracket)

            if start_bracket == -1 or end_bracket == -1:
                # No complete frame yet
                self._buffer = self._buffer[1:]
                continue

            # Extract hex string
            hex_str = frame_str[start_bracket + 1 : end_bracket]
            if len(hex_str) != FRAME_LENGTH * 2:  # Should be 54 chars
                self._buffer = self._buffer[1:]
                continue

            # Parse the frame
            try:
                frame_bytes = bytes.fromhex(hex_str)
                if self._validate_frame(frame_bytes):
                    parsed = self._parse_frame(frame_bytes)
                    if parsed:
                        self._last_frame = parsed
                        if self.callback:
                            asyncio.create_task(self.callback(parsed))
            except ValueError as err:
                _LOGGER.debug("Invalid hex frame: %s", err)

            # Remove processed frame from buffer
            self._buffer = self._buffer[end_bracket + 1 :]

    def _find_frame_start(self) -> Optional[int]:
        """Find the start of a frame in the buffer."""
        buffer_str = self._buffer.decode("ascii", errors="ignore")
        idx = buffer_str.find("[")
        return idx if idx != -1 else None

    def _validate_frame(self, frame: bytes) -> bool:
        """Validate a frame."""
        if len(frame) != FRAME_LENGTH:
            return False
        if frame[0:3] != FRAME_HEADER:
            _LOGGER.debug("Invalid frame header: %s", frame[0:3].hex())
            return False
        return True

    def _parse_frame(self, frame: bytes) -> Optional[dict]:
        """Parse a RS-485 frame."""
        try:
            # Extract data
            water_temp_raw = frame[3]
            setpoint_raw = frame[5]
            mode_byte = frame[23]
            heater_byte = frame[19]

            # Convert temperatures (multiply by 0.5, round to int)
            water_temp = round(water_temp_raw * TEMP_MULTIPLIER)
            setpoint = round(setpoint_raw * TEMP_MULTIPLIER)

            # Determine mode
            mode = None
            if mode_byte == MODE_ST:
                mode = "ST"
            elif mode_byte == MODE_ECO:
                mode = "ECO"
            elif mode_byte == MODE_SL:
                mode = "SL"
            elif mode_byte == MODE_UNK:
                mode = "UNK"
            else:
                _LOGGER.warning("Unknown mode byte: 0x%02X", mode_byte)
                mode = "UNK"

            # Heater status (bit 0 of byte 19)
            heater_on = bool(heater_byte & 0x01)

            result = {
                "water_temp": water_temp,
                "setpoint": setpoint,
                "mode": mode,
                "heater_on": heater_on,
                "raw_mode_byte": mode_byte,
                "raw_frame": frame.hex(),
            }

            _LOGGER.debug("Parsed frame: %s", result)
            return result

        except Exception as err:
            _LOGGER.error("Error parsing frame: %s", err)
            return None

    # ==================================================================================
    # WRITE COMMANDS - NOT SUPPORTED
    # ==================================================================================
    # The following methods were designed for RS-485 write operations, but tests have
    # confirmed that the VL403 keypad uses a PROPRIETARY protocol (not standard RS-485).
    #
    # Attempting to write to the RS-485 bus causes malfunctions (e.g., forced pump activation).
    # The RS-485 bus is READ-ONLY for monitoring purposes.
    #
    # For spa control, use:
    # - Physical VL403 keypad
    # - IR remote control via ESP32/ESPHome (see IR_CONTROL.md)
    # ==================================================================================

    async def send_command(self, command: bytes) -> bool:
        """Send a command to the spa.

        ⚠️ NOT SUPPORTED: RS-485 write operations are not functional.
        The VL403 uses a proprietary protocol. See IR_CONTROL.md for alternatives.
        """
        _LOGGER.error(
            "RS-485 write not supported. VL403 uses proprietary protocol. "
            "Use physical keypad or IR control (ESP32). See IR_CONTROL.md"
        )
        return False

    def build_setpoint_command(self, setpoint: int) -> bytes:
        """Build a setpoint change command.

        ⚠️ NOT SUPPORTED: Kept for reference only.
        RS-485 write operations do not work with GS500Z/VL403.
        """
        _LOGGER.warning(
            "build_setpoint_command called but RS-485 write is not supported. "
            "Use IR control instead (see IR_CONTROL.md)"
        )

        # Legacy code kept for reference
        setpoint_raw = int(setpoint / TEMP_MULTIPLIER)
        command = bytearray(FRAME_HEADER)
        command.extend([0x00] * (FRAME_LENGTH - 3))
        command[5] = setpoint_raw

        return bytes(command)

    def build_mode_command(self, current_mode: str, target_mode: str) -> Optional[bytes]:
        """Build a mode change command.

        ⚠️ NOT SUPPORTED: Kept for reference only.
        RS-485 write operations do not work with GS500Z/VL403.
        """
        _LOGGER.warning(
            "build_mode_command called but RS-485 write is not supported. "
            "Use IR control instead (see IR_CONTROL.md)"
        )

        # Legacy code kept for reference
        mode_sequence = ["ST", "ECO", "SL"]

        if current_mode not in mode_sequence or target_mode not in mode_sequence:
            return None

        current_idx = mode_sequence.index(current_mode)
        target_idx = mode_sequence.index(target_mode)
        presses = (target_idx - current_idx) % len(mode_sequence)

        if presses == 0:
            return None

        command = bytearray(FRAME_HEADER)
        command.extend([0x00] * (FRAME_LENGTH - 3))
        command[23] = 0x01

        return bytes(command)

    def get_last_frame(self) -> Optional[dict]:
        """Get the last parsed frame."""
        return self._last_frame

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._writer is not None and not self._writer.is_closing()
