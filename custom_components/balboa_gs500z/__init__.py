"""The Balboa GS500Z Spa integration.

This integration provides read-only monitoring of Balboa GS500Z spa systems
via RS-485 communication through an EW11A WiFi-to-RS485 bridge.

Key components:
- TCP client: Manages connection to EW11A and parses RS-485 frames
- Data coordinator: Validates data using sliding window consensus
- Climate entity: Displays temperature and mode information
- Binary sensor: Shows heater status

READ-ONLY MODE: This integration cannot control the spa. The VL403 keypad
uses a proprietary protocol. See IR_CONTROL.md for control options.
"""
from __future__ import annotations

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_HOST,
    CONF_ORDER_GUARD,
    CONF_PORT,
    CONF_WINDOW_SIZE,
    CONNECTION_TIMEOUT,
    COORDINATOR,
    DEFAULT_ORDER_GUARD,
    DEFAULT_WINDOW_SIZE,
    DOMAIN,
    TCP_CLIENT,
)
from .coordinator import BalboaDataCoordinator
from .tcp_client import BalboaTCPClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Balboa GS500Z Spa from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry containing host, port, and options

    Returns:
        True if setup succeeded, False otherwise

    Raises:
        ConfigEntryNotReady: If unable to connect to EW11A within timeout

    Setup sequence:
        1. Extract configuration (host, port, window_size, order_guard)
        2. Create TCP client for EW11A communication
        3. Create data coordinator with sliding window validation
        4. Start TCP client and wait for initial connection
        5. Forward setup to platform entities (climate, binary_sensor)
        6. Register options update listener
    """
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    window_size = entry.options.get(CONF_WINDOW_SIZE, DEFAULT_WINDOW_SIZE)
    order_guard = entry.options.get(CONF_ORDER_GUARD, DEFAULT_ORDER_GUARD)

    _LOGGER.info("Setting up Balboa GS500Z integration for %s:%s", host, port)

    tcp_client = None
    coordinator = None

    try:
        # Create TCP client
        tcp_client = BalboaTCPClient(host, port)

        # Create coordinator (may raise ValueError if window_size invalid)
        coordinator = BalboaDataCoordinator(
            hass, tcp_client, window_size=window_size, order_guard=order_guard
        )

        # Store coordinator and client before starting (needed for cleanup on error)
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            COORDINATOR: coordinator,
            TCP_CLIENT: tcp_client,
        }

        # Start TCP client in background and track the task
        start_task = asyncio.create_task(tcp_client.start())

        # Wait for initial connection with timeout
        try:
            await asyncio.wait_for(
                _wait_for_connection(tcp_client),
                timeout=CONNECTION_TIMEOUT
            )
        except asyncio.TimeoutError:
            # Cleanup before raising
            if not start_task.done():
                start_task.cancel()
            await tcp_client.disconnect()
            raise ConfigEntryNotReady(
                f"Timeout connecting to {host}:{port} after {CONNECTION_TIMEOUT}s"
            ) from None

        # Forward entry setup to platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        # ==================================================================================
        # NOTE: Services are not registered (read-only integration)
        # ==================================================================================
        # Write operations are not supported. The VL403 keypad uses a proprietary protocol
        # (not standard RS-485). For spa control, use:
        # - Physical VL403 keypad (direct control)
        # - IR remote via ESP32/ESPHome (see IR_CONTROL.md)
        # ==================================================================================

        # Register update listener for options changes
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))

        _LOGGER.info("Balboa GS500Z integration setup complete")
        return True

    except ValueError as err:
        # Invalid configuration (e.g., window_size out of range)
        _LOGGER.error("Invalid configuration: %s", err)
        # Cleanup if we created resources
        if tcp_client:
            try:
                await tcp_client.disconnect()
            except Exception:
                pass
        # Remove from hass.data if we added it
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)
        raise ConfigEntryNotReady(f"Invalid configuration: {err}") from err

    except Exception as err:
        # Unexpected error during setup
        _LOGGER.error("Unexpected error during setup: %s", err, exc_info=True)
        # Cleanup
        if tcp_client:
            try:
                await tcp_client.disconnect()
            except Exception:
                pass
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)
        raise ConfigEntryNotReady(f"Setup failed: {err}") from err


async def _wait_for_connection(tcp_client: BalboaTCPClient) -> None:
    """Wait for TCP client to establish connection.

    Args:
        tcp_client: TCP client instance to monitor

    Note:
        Polls every 0.5s until is_connected is True.
        Caller should wrap this in asyncio.wait_for() for timeout.
    """
    while not tcp_client.is_connected:
        await asyncio.sleep(0.5)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and cleanup resources.

    Args:
        hass: Home Assistant instance
        entry: Config entry to unload

    Returns:
        True if unload succeeded, False otherwise

    Note:
        Stops TCP client and removes all stored data for this entry.
        Platforms are unloaded first to prevent orphaned entities.
    """
    _LOGGER.info("Unloading Balboa GS500Z integration")

    # Unload platforms first (remove entities)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Stop TCP client and cleanup (with error handling)
        try:
            data = hass.data[DOMAIN].pop(entry.entry_id, None)
            if data:
                tcp_client: BalboaTCPClient = data.get(TCP_CLIENT)
                if tcp_client:
                    await tcp_client.disconnect()
                    _LOGGER.debug("TCP client disconnected successfully")
        except Exception as err:
            # Log but don't fail unload if cleanup has issues
            _LOGGER.error("Error during TCP client cleanup: %s", err, exc_info=True)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry (called when options are updated).

    Args:
        hass: Home Assistant instance
        entry: Config entry to reload

    Note:
        This is called when user changes options (window_size, order_guard).
        Unloads current setup and creates a new one with updated settings.
    """
    _LOGGER.info("Reloading Balboa GS500Z integration (options changed)")

    # Unload current setup
    await async_unload_entry(hass, entry)

    # Setup with new options
    await async_setup_entry(hass, entry)
