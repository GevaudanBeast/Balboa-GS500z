"""Constants for the Balboa GS500Z Spa integration."""
from typing import Final

# ==================================================================================
# INTEGRATION METADATA
# ==================================================================================
DOMAIN: Final = "balboa_gs500z"

# ==================================================================================
# CONFIGURATION KEYS
# ==================================================================================
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_WINDOW_SIZE: Final = "window_size"
CONF_ORDER_GUARD: Final = "order_guard"

# ==================================================================================
# DEFAULT VALUES
# ==================================================================================
DEFAULT_PORT: Final = 8899
DEFAULT_WINDOW_SIZE: Final = 5  # Number of frames to keep in validation window
DEFAULT_ORDER_GUARD: Final = True  # Enable mode transition validation

# Validation limits
MIN_WINDOW_SIZE: Final = 3  # Minimum frames needed for reliable validation
MAX_WINDOW_SIZE: Final = 20  # Maximum to avoid excessive memory and lag
MIN_PORT: Final = 1  # Valid TCP port range
MAX_PORT: Final = 65535  # Valid TCP port range

# ==================================================================================
# RS-485 PROTOCOL CONSTANTS
# ==================================================================================
# Frame structure: [Header(3) + Data(23) + Checksum(1)] = 27 bytes total
FRAME_HEADER: Final = bytes([0x64, 0x3F, 0x2B])  # Fixed header identifying spa frames
FRAME_LENGTH: Final = 27  # Total frame size in bytes

# Temperature encoding: raw value × 0.5 = °C
# Example: 0x4C (76) × 0.5 = 38°C
TEMP_MULTIPLIER: Final = 0.5

# ==================================================================================
# MODE CONSTANTS (byte 23 in RS-485 frame)
# ==================================================================================
MODE_ST: Final = 0x20  # Standard mode (full heating)
MODE_ECO: Final = 0x00  # Economy mode (alternates with ST/SL)
MODE_SL: Final = 0x40  # Sleep mode (minimal heating)
MODE_UNK: Final = 0x60  # Unknown/transitional mode (ignored in validation)

# ==================================================================================
# HOME ASSISTANT MODE MAPPINGS
# ==================================================================================
# Preset mode names in Home Assistant
HVAC_MODE_ST: Final = "standard"
HVAC_MODE_ECO: Final = "eco"
HVAC_MODE_SL: Final = "sleep"

# Bidirectional mappings between RS-485 and Home Assistant
RS485_TO_HA_MODE: Final = {
    MODE_ST: HVAC_MODE_ST,
    MODE_ECO: HVAC_MODE_ECO,
    MODE_SL: HVAC_MODE_SL,
}

HA_TO_RS485_MODE: Final = {
    HVAC_MODE_ST: MODE_ST,
    HVAC_MODE_ECO: MODE_ECO,
    HVAC_MODE_SL: MODE_SL,
}

# Valid mode transitions enforced by VL403 keypad (ST → ECO → SL → ST)
# Used for validation even in read-only mode to detect anomalies
VALID_MODE_TRANSITIONS: Final = {
    HVAC_MODE_ST: [HVAC_MODE_ECO],
    HVAC_MODE_ECO: [HVAC_MODE_SL, HVAC_MODE_ST],
    HVAC_MODE_SL: [HVAC_MODE_ST],
}

# ==================================================================================
# ENTITY CONFIGURATION
# ==================================================================================
CLIMATE_ENTITY_ID: Final = "spa"
HEATER_SENSOR_ID: Final = "spa_heater"

# ==================================================================================
# NETWORK & TIMING
# ==================================================================================
RECONNECT_DELAY: Final = 5  # Seconds to wait before reconnection attempt
CONNECTION_TIMEOUT: Final = 10  # Seconds to wait for initial connection

# ==================================================================================
# DATA STORAGE KEYS
# ==================================================================================
COORDINATOR: Final = "coordinator"
TCP_CLIENT: Final = "tcp_client"
PLATFORMS: Final = ["climate", "binary_sensor"]

# ==================================================================================
# ERROR KEYS
# ==================================================================================
ERROR_CANNOT_CONNECT: Final = "cannot_connect"
ERROR_UNKNOWN: Final = "unknown"
