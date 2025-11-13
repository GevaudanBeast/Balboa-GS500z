"""The Balboa GS500Z Spa integration."""
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
    """Set up Balboa GS500Z Spa from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    window_size = entry.options.get(CONF_WINDOW_SIZE, DEFAULT_WINDOW_SIZE)
    order_guard = entry.options.get(CONF_ORDER_GUARD, DEFAULT_ORDER_GUARD)

    _LOGGER.info("Setting up Balboa GS500Z integration for %s:%s", host, port)

    # Create TCP client
    tcp_client = BalboaTCPClient(host, port)

    # Create coordinator
    coordinator = BalboaDataCoordinator(
        hass, tcp_client, window_size=window_size, order_guard=order_guard
    )

    # Store coordinator and client
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
        TCP_CLIENT: tcp_client,
    }

    # Start TCP client
    try:
        # Start client in background
        asyncio.create_task(tcp_client.start())

        # Wait for first connection
        for _ in range(10):  # Wait up to 10 seconds
            if tcp_client.is_connected:
                break
            await asyncio.sleep(1)
        else:
            raise ConfigEntryNotReady(f"Failed to connect to {host}:{port}")

    except Exception as err:
        _LOGGER.error("Failed to start TCP client: %s", err)
        raise ConfigEntryNotReady(f"Failed to connect to {host}:{port}") from err

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # NOTE: Services are not registered because write operations are not supported.
    # The VL403 keypad uses a proprietary protocol (not standard RS-485).
    # For spa control, use physical keypad or IR remote via ESP32 (see IR_CONTROL.md).

    # Register update listener for options
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Balboa GS500Z integration setup complete")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Balboa GS500Z integration")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Stop TCP client
        data = hass.data[DOMAIN].pop(entry.entry_id)
        tcp_client: BalboaTCPClient = data[TCP_CLIENT]
        await tcp_client.disconnect()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
