"""Config flow for Balboa GS500Z Spa integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_ORDER_GUARD,
    CONF_WINDOW_SIZE,
    DEFAULT_ORDER_GUARD,
    DEFAULT_PORT,
    DEFAULT_WINDOW_SIZE,
    DOMAIN,
)
from .tcp_client import BalboaTCPClient

_LOGGER = logging.getLogger(__name__)


class BalboaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Balboa GS500Z Spa."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            # Test connection
            if await self._test_connection(host, port):
                # Create unique ID based on host:port
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Balboa Spa ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                    },
                )
            else:
                errors["base"] = "cannot_connect"

        # Show form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
                }
            ),
            errors=errors,
        )

    async def _test_connection(self, host: str, port: int) -> bool:
        """Test if we can connect to the EW11A."""
        try:
            _LOGGER.info("Testing connection to %s:%s", host, port)
            client = BalboaTCPClient(host, port)

            # Try to connect
            connected = await client.connect()

            if connected:
                await client.disconnect()
                _LOGGER.info("Connection test successful")
                return True
            else:
                _LOGGER.error("Connection test failed")
                return False

        except Exception as err:
            _LOGGER.error("Connection test error: %s", err)
            return False

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> BalboaOptionsFlow:
        """Get the options flow for this handler."""
        return BalboaOptionsFlow(config_entry)


class BalboaOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Balboa GS500Z Spa."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate window size
            window_size = user_input.get(CONF_WINDOW_SIZE, DEFAULT_WINDOW_SIZE)
            if window_size < 3:
                errors[CONF_WINDOW_SIZE] = "window_size_too_small"
            elif window_size > 20:
                errors[CONF_WINDOW_SIZE] = "window_size_too_large"
            else:
                return self.async_create_entry(title="", data=user_input)

        # Get current options or defaults
        current_window_size = self.config_entry.options.get(
            CONF_WINDOW_SIZE, DEFAULT_WINDOW_SIZE
        )
        current_order_guard = self.config_entry.options.get(
            CONF_ORDER_GUARD, DEFAULT_ORDER_GUARD
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_WINDOW_SIZE, default=current_window_size
                    ): vol.All(vol.Coerce(int), vol.Range(min=3, max=20)),
                    vol.Optional(
                        CONF_ORDER_GUARD, default=current_order_guard
                    ): bool,
                }
            ),
            errors=errors,
        )
