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
        """Parse a RS-485 frame from J18.

        Confirmed byte mapping (GS501Z+/VL403, captures 01/10/2025):
          byte 3  : water temperature (raw * 0.5 = deg C)
          byte 5  : setpoint (raw * 0.5 = deg C)
          byte 6  : frame counter (ignored)
          byte 17 : pump/blower state (bit7=blower, low bits=pump speed)
          byte 19 : heater + context (bit0 = heater ON, universal across modes)
          byte 20 : light state (0x02/0x03 = ON variants)
          byte 23 : operating mode (0x20=ST, 0x00=ECO, 0x40=SL, 0x60=transitoire)
        """
        try:
            water_temp_raw = frame[3]
            setpoint_raw = frame[5]
            pump_byte = frame[17]
            heater_byte = frame[19]
            light_byte = frame[20]
            mode_byte = frame[23]

            water_temp = round(water_temp_raw * TEMP_MULTIPLIER)
            setpoint = round(setpoint_raw * TEMP_MULTIPLIER)

            # Byte 17: blower (bit 7) and pump speed (lower bits)
            blower_on = bool(pump_byte & 0x80)
            pump_raw = pump_byte & 0x7F
            if pump_raw in (0x01, 0x08):
                pump1_state = "low"
            elif pump_raw in (0x02, 0x18):
                pump1_state = "high"
            else:
                pump1_state = "off"

            # Byte 19 bit 0: universal heater indicator (confirmed all modes)
            heater_on = bool(heater_byte & 0x01)

            # Bytes 20-21: light state
            light_on = light_byte in (0x02, 0x03)

            # Byte 23: operating mode (strict decode)
            b23 = mode_byte & 0x60
            if b23 == 0x60:
                mode = "UNK"
            elif b23 == 0x40:
                mode = "SL"
            elif b23 == 0x20:
                mode = "ST"
            elif mode_byte == 0x00:
                mode = "ECO"
            else:
                _LOGGER.warning("Unknown mode byte: 0x%02X", mode_byte)
                mode = "UNK"

            result = {
                "water_temp": water_temp,
                "setpoint": setpoint,
                "mode": mode,
                "heater_on": heater_on,
                "pump1_state": pump1_state,
                "blower_on": blower_on,
                "light_on": light_on,
                "_b19": heater_byte,
                "_b23": mode_byte,
                "raw_frame": frame.hex(),
            }

            _LOGGER.debug("Parsed frame: %s", result)
            return result

        except Exception as err:
            _LOGGER.error("Error parsing frame: %s", err)
            return None

    async def send_command(self, command: bytes) -> bool:
        """Send a command to the spa."""
        if not self._writer:
            _LOGGER.error("Cannot send command: not connected")
            return False

        try:
            # Encapsulate command in brackets with hex encoding
            hex_str = command.hex().upper()
            frame = "[{0}]\r\n".format(hex_str).encode("ascii")

            _LOGGER.info("Sending command: %s", hex_str)
            self._writer.write(frame)
            await self._writer.drain()
            return True

        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            return False

    def build_setpoint_command(self, setpoint: int) -> bytes:
        """Build a setpoint change command.

        NOT IMPLEMENTED — J18 is read-only; the exact write protocol for the
        GS500Z/GS501Z bus has not been reverse-engineered.  This stub exists
        as a placeholder for when J1 bus control (via EL817 optocoupler) is
        validated.  Do not call in production.
        """
        _LOGGER.error(
            "build_setpoint_command called but write protocol is not implemented. "
            "J18 is RX-only; J1 bus control is pending hardware validation."
        )
        raise NotImplementedError(
            "Setpoint command not implemented: J18 is read-only. "
            "Awaiting J1 bus protocol validation."
        )

    def build_mode_command(self, current_mode: str, target_mode: str) -> Optional[bytes]:
        """Build a mode change command.

        NOT IMPLEMENTED — same reason as build_setpoint_command.  Mode changes
        are performed physically via the VL403 panel.  J1 bus control (EL817
        porte-OR) is the planned mechanism once validated.
        """
        _LOGGER.error(
            "build_mode_command called but write protocol is not implemented. "
            "J18 is RX-only; J1 bus control is pending hardware validation."
        )
        raise NotImplementedError(
            "Mode command not implemented: J18 is read-only. "
            "Awaiting J1 bus protocol validation."
        )

    def get_last_frame(self) -> Optional[dict]:
        """Get the last parsed frame."""
        return self._last_frame

    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._writer is not None and not self._writer.is_closing()
