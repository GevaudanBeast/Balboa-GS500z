"""Config flow for Balboa GS500Z Spa integration.

This module handles the configuration flow for adding and configuring the integration
in Home Assistant. It validates user inputs and tests connectivity to the EW11A module.
"""
from __future__ import annotations

import asyncio
import logging
import re
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
    CONNECTION_TIMEOUT,
    DEFAULT_ORDER_GUARD,
    DEFAULT_PORT,
    DEFAULT_WINDOW_SIZE,
    DOMAIN,
    ERROR_CANNOT_CONNECT,
    MAX_WINDOW_SIZE,
    MIN_WINDOW_SIZE,
)
from .tcp_client import BalboaTCPClient

_LOGGER = logging.getLogger(__name__)

# IP address validation pattern (basic IPv4 format check)
_IP_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)


class BalboaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Balboa GS500Z Spa."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial configuration step.

        This validates user input and tests connectivity to the EW11A module.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Extract and validate input
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]

            # Basic IPv4 format validation (also accepts hostnames)
            if not _IP_PATTERN.match(host) and not self._is_valid_hostname(host):
                _LOGGER.warning("Invalid host format: %s", host)
                errors["base"] = ERROR_CANNOT_CONNECT
            else:
                # Test connection with timeout
                if await self._test_connection(host, port):
                    # Create unique ID based on host:port to prevent duplicates
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
                    errors["base"] = ERROR_CANNOT_CONNECT

        # Show configuration form
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

    def _is_valid_hostname(self, hostname: str) -> bool:
        """Validate hostname format.

        Args:
            hostname: The hostname to validate

        Returns:
            True if hostname format is valid, False otherwise
        """
        # RFC 1123 hostname validation (simplified)
        if len(hostname) > 255:
            return False

        # Remove trailing dot if present
        if hostname.endswith("."):
            hostname = hostname[:-1]

        # Check each label
        labels = hostname.split(".")
        for label in labels:
            if not label or len(label) > 63:
                return False
            if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$", label):
                return False

        return True

    async def _test_connection(self, host: str, port: int) -> bool:
        """Test connectivity to the EW11A module.

        Args:
            host: IP address or hostname of the EW11A
            port: TCP port number

        Returns:
            True if connection succeeds, False otherwise
        """
        client = None
        try:
            _LOGGER.info("Testing connection to %s:%s", host, port)
            client = BalboaTCPClient(host, port)

            # Try to connect with timeout
            connected = await asyncio.wait_for(
                client.connect(),
                timeout=CONNECTION_TIMEOUT
            )

            if connected:
                _LOGGER.info("Connection test successful")
                return True
            else:
                _LOGGER.error("Connection test failed: could not connect")
                return False

        except asyncio.TimeoutError:
            _LOGGER.error("Connection test timed out after %ds", CONNECTION_TIMEOUT)
            return False
        except OSError as err:
            # Network errors (connection refused, host unreachable, etc.)
            _LOGGER.error("Connection test failed: %s", err)
            return False
        except Exception as err:
            # Catch-all for unexpected errors
            _LOGGER.exception("Unexpected error during connection test: %s", err)
            return False
        finally:
            # Always cleanup connection
            if client:
                try:
                    await client.disconnect()
                except Exception as err:
                    _LOGGER.debug("Error during cleanup: %s", err)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> BalboaOptionsFlow:
        """Get the options flow for this handler."""
        return BalboaOptionsFlow(config_entry)


class BalboaOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Balboa GS500Z Spa.

    This allows users to modify advanced settings after initial configuration.
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow.

        Args:
            config_entry: The configuration entry being modified
        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow.

        Validates advanced settings like window size and mode validation guard.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate window size (double-check even though schema validates)
            window_size = user_input.get(CONF_WINDOW_SIZE, DEFAULT_WINDOW_SIZE)

            if window_size < MIN_WINDOW_SIZE:
                errors[CONF_WINDOW_SIZE] = "window_size_too_small"
            elif window_size > MAX_WINDOW_SIZE:
                errors[CONF_WINDOW_SIZE] = "window_size_too_large"
            else:
                # All validations passed
                return self.async_create_entry(title="", data=user_input)

        # Get current options or fall back to defaults
        current_window_size = self.config_entry.options.get(
            CONF_WINDOW_SIZE, DEFAULT_WINDOW_SIZE
        )
        current_order_guard = self.config_entry.options.get(
            CONF_ORDER_GUARD, DEFAULT_ORDER_GUARD
        )

        # Show options form
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_WINDOW_SIZE, default=current_window_size
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_WINDOW_SIZE, max=MAX_WINDOW_SIZE)
                    ),
                    vol.Optional(
                        CONF_ORDER_GUARD, default=current_order_guard
                    ): bool,
                }
            ),
            errors=errors,
        )
