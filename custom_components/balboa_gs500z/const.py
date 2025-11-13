"""Constants for the Balboa GS500Z Spa integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "balboa_gs500z"

# Configuration keys
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_WINDOW_SIZE: Final = "window_size"
CONF_REFRESH_RATE: Final = "refresh_rate"
CONF_ORDER_GUARD: Final = "order_guard"

# Default values
DEFAULT_PORT: Final = 8899
DEFAULT_WINDOW_SIZE: Final = 5
DEFAULT_REFRESH_RATE: Final = 2
DEFAULT_ORDER_GUARD: Final = True

# RS-485 Protocol constants
FRAME_HEADER: Final = bytes([0x64, 0x3F, 0x2B])
FRAME_LENGTH: Final = 27

# Temperature conversion
TEMP_MULTIPLIER: Final = 0.5

# Mode mappings (byte 23)
MODE_ST: Final = 0x20
MODE_ECO: Final = 0x00
MODE_SL: Final = 0x40
MODE_UNK: Final = 0x60  # Transitoire

# HVAC modes for Home Assistant
HVAC_MODE_ST: Final = "standard"
HVAC_MODE_ECO: Final = "eco"
HVAC_MODE_SL: Final = "sleep"

# Mode mapping RS-485 → HA
RS485_TO_HA_MODE: Final = {
    MODE_ST: HVAC_MODE_ST,
    MODE_ECO: HVAC_MODE_ECO,
    MODE_SL: HVAC_MODE_SL,
}

# Mode mapping HA → RS-485
HA_TO_RS485_MODE: Final = {
    HVAC_MODE_ST: MODE_ST,
    HVAC_MODE_ECO: MODE_ECO,
    HVAC_MODE_SL: MODE_SL,
}

# Valid mode transitions (ST → ECO → SL → ST)
VALID_MODE_TRANSITIONS: Final = {
    HVAC_MODE_ST: [HVAC_MODE_ECO],
    HVAC_MODE_ECO: [HVAC_MODE_SL, HVAC_MODE_ST],  # Allow SL→ECO if transitoire
    HVAC_MODE_SL: [HVAC_MODE_ST],
}

# NOTE: Services are not defined because write operations are not supported.
# The VL403 uses a proprietary protocol (not standard RS-485).
# For control, use physical keypad or IR remote via ESP32 (see IR_CONTROL.md).

# Entity IDs
CLIMATE_ENTITY_ID: Final = "spa"
HEATER_SENSOR_ID: Final = "spa_heater"

# Update intervals
RECONNECT_DELAY: Final = 5  # seconds
CONNECTION_TIMEOUT: Final = 10  # seconds

# Coordinator keys
COORDINATOR: Final = "coordinator"
TCP_CLIENT: Final = "tcp_client"
PLATFORMS: Final = ["climate", "binary_sensor"]
