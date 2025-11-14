"""TCP client for Balboa GS500Z RS-485 communication via EW11A.

This module handles the TCP connection to the EW11A WiFi-to-RS485 bridge,
reads incoming RS-485 frames, parses them, and notifies the coordinator of updates.

The EW11A encapsulates RS-485 frames in ASCII format: [HEXDATA]\r\n
Example: [643F2B4A004C...]\r\n (27 bytes = 54 hex characters)
"""
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

# Buffer management constants
_MAX_BUFFER_SIZE = 4096  # Maximum buffer size to prevent memory issues (bytes)
_READ_CHUNK_SIZE = 1024  # How much data to read at once (bytes)

# Frame format constants (byte positions in RS-485 frame)
_BYTE_WATER_TEMP = 3  # Water temperature (raw value × 0.5 = °C)
_BYTE_SETPOINT = 5  # Target temperature (raw value × 0.5 = °C)
_BYTE_HEATER_STATUS = 19  # Heater status (bit 0: 1=ON, 0=OFF)
_BYTE_MODE = 23  # Operating mode (0x20=ST, 0x00=ECO, 0x40=SL, 0x60=UNK)


class BalboaTCPClient:
    """TCP client for EW11A RS-485 bridge.

    This class manages the persistent TCP connection to the EW11A module,
    automatically reconnects on disconnection, and parses incoming RS-485 frames.

    Attributes:
        host: IP address or hostname of the EW11A module
        port: TCP port number (usually 8899)
        callback: Optional async callback function called with parsed frame data
    """

    def __init__(
        self,
        host: str,
        port: int,
        callback: Optional[Callable[[dict], Awaitable[None]]] = None,
    ) -> None:
        """Initialize the TCP client.

        Args:
            host: IP address or hostname of EW11A
            port: TCP port number
            callback: Optional async function to call with parsed frames
        """
        self.host = host
        self.port = port
        self.callback = callback

        # Connection state
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._running = False
        self._read_task: Optional[asyncio.Task] = None

        # Frame processing
        self._buffer = bytearray()
        self._last_frame: Optional[dict] = None

        # Callback task tracking (for proper cleanup)
        self._callback_tasks: set[asyncio.Task] = set()

    async def connect(self) -> bool:
        """Establish TCP connection to the EW11A module.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            _LOGGER.info("Connecting to %s:%s", self.host, self.port)

            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=CONNECTION_TIMEOUT,
            )

            _LOGGER.info("Successfully connected to %s:%s", self.host, self.port)
            return True

        except asyncio.TimeoutError:
            _LOGGER.error(
                "Connection timeout to %s:%s after %ds",
                self.host,
                self.port,
                CONNECTION_TIMEOUT
            )
            return False

        except OSError as err:
            # Network errors: connection refused, host unreachable, etc.
            _LOGGER.error(
                "Connection error to %s:%s: %s",
                self.host,
                self.port,
                err
            )
            return False

        except Exception as err:
            # Unexpected errors
            _LOGGER.exception(
                "Unexpected error connecting to %s:%s: %s",
                self.host,
                self.port,
                err
            )
            return False

    async def disconnect(self) -> None:
        """Disconnect from the EW11A and cleanup resources.

        This method ensures all resources are properly released:
        - Cancels the read task
        - Closes the TCP connection
        - Cancels any pending callback tasks
        - Clears the buffer
        """
        self._running = False

        # Cancel read task if running
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            self._read_task = None

        # Cancel all pending callback tasks
        for task in self._callback_tasks:
            if not task.done():
                task.cancel()

        # Wait for callbacks to complete (with timeout)
        if self._callback_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._callback_tasks, return_exceptions=True),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                _LOGGER.warning("Some callback tasks did not complete in time")

        self._callback_tasks.clear()

        # Close TCP connection
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as err:
                _LOGGER.debug("Error closing connection: %s", err)
            finally:
                self._writer = None
                self._reader = None

        # Clear buffer
        self._buffer.clear()

        _LOGGER.info("Disconnected from %s:%s", self.host, self.port)

    async def start(self) -> None:
        """Start the TCP client with automatic reconnection.

        This method runs continuously, reconnecting if the connection drops.
        It should be run as a background task and will only stop when
        disconnect() is called.
        """
        self._running = True

        while self._running:
            # Attempt connection
            if await self.connect():
                # Start read loop
                self._read_task = asyncio.create_task(self._read_loop())

                try:
                    await self._read_task
                except asyncio.CancelledError:
                    # Normal shutdown
                    break
                except Exception as err:
                    _LOGGER.error("Read loop error: %s", err)

            # Wait before reconnecting (unless shutting down)
            if self._running:
                _LOGGER.info("Reconnecting in %ds...", RECONNECT_DELAY)
                await asyncio.sleep(RECONNECT_DELAY)

    async def _read_loop(self) -> None:
        """Continuously read data from the TCP connection.

        This method reads data in chunks, appends to buffer, and processes
        complete frames. It implements buffer size protection to prevent
        memory issues.

        Raises:
            asyncio.CancelledError: When the task is cancelled (normal shutdown)
            Exception: On unexpected errors (triggers reconnection)
        """
        try:
            while self._running and self._reader:
                # Read data chunk
                data = await self._reader.read(_READ_CHUNK_SIZE)

                if not data:
                    # Connection closed by remote
                    _LOGGER.warning("Connection closed by %s:%s", self.host, self.port)
                    break

                # Prevent buffer overflow
                if len(self._buffer) + len(data) > _MAX_BUFFER_SIZE:
                    _LOGGER.warning(
                        "Buffer overflow protection: clearing buffer (%d bytes)",
                        len(self._buffer)
                    )
                    self._buffer.clear()

                # Append data and process
                self._buffer.extend(data)
                self._process_buffer()

        except asyncio.CancelledError:
            # Normal cancellation during shutdown
            raise

        except Exception as err:
            # Unexpected error - log and reraise to trigger reconnection
            _LOGGER.error("Error in read loop: %s", err)
            raise

    def _process_buffer(self) -> None:
        """Extract and process complete frames from the buffer.

        EW11A sends frames as: [HEXDATA]\r\n
        Example: [643F2B4A004C...ABC123]\r\n
        Where HEXDATA is 54 characters (27 bytes in hex)

        This method searches for complete frames, validates them, parses them,
        and notifies the callback. It handles corrupted data gracefully.
        """
        while True:
            # Need minimum buffer size for a frame
            # '[' (1) + hex (54) + ']' (1) = 56 bytes minimum
            if len(self._buffer) < 56:
                break

            # Find frame boundaries
            try:
                buffer_str = self._buffer.decode("ascii", errors="ignore")
            except Exception as err:
                _LOGGER.debug("Buffer decode error: %s", err)
                self._buffer = self._buffer[1:]  # Skip one byte
                continue

            # Look for start bracket
            start_idx = buffer_str.find("[")
            if start_idx == -1:
                # No frame start found, keep last 55 bytes in case of split
                if len(self._buffer) > 55:
                    self._buffer = self._buffer[-55:]
                break

            # Look for end bracket after start
            end_idx = buffer_str.find("]", start_idx + 1)
            if end_idx == -1:
                # No end bracket yet, keep from start_idx and wait for more data
                if start_idx > 0:
                    self._buffer = self._buffer[start_idx:]
                break

            # Extract hex string between brackets
            hex_str = buffer_str[start_idx + 1 : end_idx]

            # Validate hex string length (54 characters = 27 bytes)
            if len(hex_str) != FRAME_LENGTH * 2:
                _LOGGER.debug(
                    "Invalid frame length: expected %d, got %d",
                    FRAME_LENGTH * 2,
                    len(hex_str)
                )
                # Skip this malformed frame and continue
                self._buffer = self._buffer[end_idx + 1 :]
                continue

            # Try to parse hex string into bytes
            try:
                frame_bytes = bytes.fromhex(hex_str)
            except ValueError as err:
                _LOGGER.debug("Invalid hex data: %s", err)
                # Skip this malformed frame
                self._buffer = self._buffer[end_idx + 1 :]
                continue

            # Validate and parse frame
            if self._validate_frame(frame_bytes):
                parsed = self._parse_frame(frame_bytes)
                if parsed:
                    self._last_frame = parsed

                    # Call callback if registered (with task tracking)
                    if self.callback:
                        task = asyncio.create_task(self._safe_callback(parsed))
                        self._callback_tasks.add(task)
                        # Remove from set when done
                        task.add_done_callback(self._callback_tasks.discard)

            # Remove processed frame from buffer
            self._buffer = self._buffer[end_idx + 1 :]

    async def _safe_callback(self, data: dict) -> None:
        """Safely call the callback with error handling.

        Args:
            data: Parsed frame data to pass to callback
        """
        try:
            await self.callback(data)
        except Exception as err:
            _LOGGER.error("Error in callback: %s", err)

    def _validate_frame(self, frame: bytes) -> bool:
        """Validate frame structure and header.

        Args:
            frame: 27-byte RS-485 frame to validate

        Returns:
            True if frame is valid, False otherwise
        """
        # Check frame length (must be exactly 27 bytes)
        if len(frame) != FRAME_LENGTH:
            _LOGGER.debug(
                "Invalid frame length: expected %d, got %d",
                FRAME_LENGTH,
                len(frame)
            )
            return False

        # Check frame header (must be 0x64 0x3F 0x2B)
        if frame[0:3] != FRAME_HEADER:
            _LOGGER.debug(
                "Invalid frame header: expected %s, got %s",
                FRAME_HEADER.hex(),
                frame[0:3].hex()
            )
            return False

        return True

    def _parse_frame(self, frame: bytes) -> Optional[dict]:
        """Parse a validated RS-485 frame into structured data.

        Frame structure (27 bytes total):
        - Bytes 0-2: Header (0x64 0x3F 0x2B)
        - Byte 3: Water temperature (raw value × 0.5 = °C)
        - Byte 5: Target temperature / setpoint (raw value × 0.5 = °C)
        - Byte 19: Heater status (bit 0: 1=ON, 0=OFF)
        - Byte 23: Operating mode (0x20=ST, 0x00=ECO, 0x40=SL, 0x60=UNK)
        - Other bytes: Reserved/unknown

        Args:
            frame: 27-byte validated RS-485 frame

        Returns:
            Dictionary with parsed data, or None if parsing fails
        """
        try:
            # Safety check: verify frame length before accessing indices
            if len(frame) != FRAME_LENGTH:
                _LOGGER.error("Frame length check failed in parser")
                return None

            # Extract raw byte values with bounds checking
            water_temp_raw = frame[_BYTE_WATER_TEMP]  # Byte 3
            setpoint_raw = frame[_BYTE_SETPOINT]  # Byte 5
            heater_byte = frame[_BYTE_HEATER_STATUS]  # Byte 19
            mode_byte = frame[_BYTE_MODE]  # Byte 23

            # Convert temperatures: raw value × 0.5 = °C, rounded to integer
            # Example: 0x4C (76) × 0.5 = 38°C
            water_temp = round(water_temp_raw * TEMP_MULTIPLIER)
            setpoint = round(setpoint_raw * TEMP_MULTIPLIER)

            # Sanity check temperatures (spa range: 15-40°C typically)
            if not (10 <= water_temp <= 50):
                _LOGGER.warning("Water temperature out of expected range: %d°C", water_temp)
            if not (10 <= setpoint <= 50):
                _LOGGER.warning("Setpoint out of expected range: %d°C", setpoint)

            # Determine operating mode from byte 23
            mode_map = {
                MODE_ST: "ST",  # 0x20 = Standard (full heating)
                MODE_ECO: "ECO",  # 0x00 = Economy (alternates ST/ECO/SL)
                MODE_SL: "SL",  # 0x40 = Sleep (minimal heating)
                MODE_UNK: "UNK",  # 0x60 = Unknown/transitional
            }
            mode = mode_map.get(mode_byte)

            if mode is None:
                # Unknown mode byte
                _LOGGER.warning("Unknown mode byte: 0x%02X", mode_byte)
                mode = "UNK"

            # Extract heater status from bit 0 of byte 19
            # Bit 0 = 1 means heater is ON, 0 means OFF
            heater_on = bool(heater_byte & 0x01)

            # Build result dictionary
            result = {
                "water_temp": water_temp,  # Current water temperature (°C)
                "setpoint": setpoint,  # Target temperature (°C)
                "mode": mode,  # Operating mode (ST/ECO/SL/UNK)
                "heater_on": heater_on,  # Heater status (bool)
                "raw_mode_byte": mode_byte,  # Raw mode byte for debugging
                "raw_frame": frame.hex(),  # Full frame in hex for debugging
            }

            _LOGGER.debug("Parsed frame: %s", result)
            return result

        except IndexError as err:
            # Should never happen due to validation, but safe to catch
            _LOGGER.error("Index error parsing frame: %s", err)
            return None

        except Exception as err:
            # Catch any other unexpected errors
            _LOGGER.error("Unexpected error parsing frame: %s", err)
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
