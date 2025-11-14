# Balboa GS500Z Home Assistant Integration

[![Validate](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Validate/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Hassfest](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Hassfest/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Release](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Release/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **[🇫🇷 Version française](README.md)** | **🇬🇧 English version**

Home Assistant integration to **monitor** a Balboa GS500Z spa via an EW11A WiFi RS-485 module.

> 🚀 **First installation?** Follow the [**Quick Start Guide (5 minutes)**](QUICKSTART.en.md)

> ⚠️ **Read-only mode**: This integration allows you to **read** the spa state (temperature, mode, heating) but **cannot control it** via RS-485. The VL403 uses a proprietary protocol. For control, see the [IR solution with ESP32](#-spa-control-ir-solution).

---

## 📖 Documentation

- **[QUICKSTART.en.md](QUICKSTART.en.md)** - 🚀 Get started in 5 minutes
- **[IR_CONTROL.en.md](IR_CONTROL.en.md)** - 🎯 Control the spa with ESP32
- **[PROTOCOL.en.md](PROTOCOL.en.md)** - 🔧 RS-485 technical details
- **[EXAMPLES.en.md](EXAMPLES.en.md)** - 💡 Automation examples
- **[INSTALL.en.md](INSTALL.en.md)** - 📦 Detailed installation guide

---

## 🎯 Features

### RS-485 Monitoring (read-only)

- **Climate Entity**: Spa state display
  - 🌡️ Real-time water temperature
  - 🎯 Current setpoint temperature
  - 🔄 Operating mode: Standard (ST), Economy (ECO), Sleep (SL)

- **Binary Sensor**: Heater status (active/inactive)

- **Advanced features**:
  - Sliding window for data validation (prevents erroneous readings)
  - Automatic TCP reconnection on disconnect
  - Configurable settings after installation
  - Complete analysis of 16,841 real frames validated ✅

### Spa Control (solution to implement)

To control the spa from Home Assistant:
- 🎯 **Recommended solution**: IR Module + ESP32 with ESPHome (see [IR_CONTROL.en.md](IR_CONTROL.en.md))
- ⌨️ **Alternative**: Use the physical VL403 keypad

## 📋 Prerequisites

- Home Assistant 2023.1 or higher
- EW11A WiFi RS-485 module configured in TCP mode
- Balboa GS500Z spa with control board and VL403 keypad

## 🔧 Quick Installation

### Via HACS (recommended)

1. **HACS** → **Integrations** → **⋮** → **Custom repositories**
2. Add: `https://github.com/GevaudanBeast/Balboa-GS500z`
3. Search for "Balboa GS500Z" → **Download**
4. **Restart** Home Assistant

### Configuration

1. **Settings** → **Devices & Services** → **+ Add Integration**
2. Search for "Balboa GS500Z"
3. Enter your EW11A IP address and port (8899)

✅ **You're ready!** Your `climate.spa` and `binary_sensor.spa_heater` entities are created.

📖 **Detailed guide**: [QUICKSTART.en.md](QUICKSTART.en.md) (wiring, EW11A configuration, etc.)

## 🎮 Usage

### Created Entities

- `climate.spa` - Temperature, mode, setpoint
- `binary_sensor.spa_heater` - Heater status

### Example: Notification when spa is ready

```yaml
automation:
  - alias: "Spa ready"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('climate.spa', 'current_temperature') >=
             state_attr('climate.spa', 'temperature') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🔥 Spa ready!"
          message: "The spa has reached {{ state_attr('climate.spa', 'temperature') }}°C"
```

### Simple Lovelace card

```yaml
type: thermostat
entity: climate.spa
name: My Spa
```

📖 **More examples**: [EXAMPLES.en.md](EXAMPLES.en.md) (automations, advanced Lovelace cards, etc.)

## 🔌 EW11A Configuration (summary)

Required settings:
- **Mode**: TCP Server
- **Baud Rate**: 9600
- **Port**: 8899

📖 **Complete guide**: [QUICKSTART.en.md](QUICKSTART.en.md) (wiring, WiFi configuration, etc.)

## 🎯 Spa Control: IR Solution

### Why doesn't RS-485 write work?

After extensive testing, it has been confirmed that:
- ❌ The VL403 keypad uses a **proprietary protocol** (not standard RS-485)
- ❌ Connecting the EW11A to the keypad connectors causes malfunctions (e.g., forced pump)
- ✅ The RS-485 bus is **read-only** (monitoring/broadcast only)

### Solution: IR Module + ESP32

To control the spa from Home Assistant, use:

| Component | Role |
|-----------|------|
| **Balboa IR Module** | Official infrared receiver (connects to GS500Z) |
| **ESP32 + ESPHome** | IR transmitter controllable from Home Assistant |

**Complete architecture**:

```
Home Assistant
     │
     ├──► Balboa GS500Z (this integration)
     │    └─► Read via RS-485 (EW11A)
     │
     └──► ESP32 ESPHome
          └─► Control via IR → Balboa IR Module
```

### Complete guide: IR_CONTROL.en.md

📁 See **[IR_CONTROL.en.md](IR_CONTROL.en.md)** for the complete guide:
- Required hardware (ESP32, IR LED, IR receiver)
- IR protocol reverse engineering
- Complete ESPHome configuration
- Home Assistant scripts for transparent control
- Automation examples with control

**Advantages of this solution**:
- ✅ Real-time reading (RS-485 via this integration)
- ✅ Functional writing (IR via ESP32)
- ✅ No spa modifications
- ✅ Native ESPHome integration
- ✅ Safe (no electronic risk)

## 📡 RS-485 Protocol

### Frame Structure

Frames are in the format: `[643F2B...]` (27 bytes = 54 hex characters)

- **Header**: `64 3F 2B`
- **Byte 3**: Water temperature (× 0.5°C)
- **Byte 5**: Setpoint temperature (× 0.5°C)
- **Byte 19 bit 0**: Heater status (1 = active)
- **Byte 23**: Mode
  - `0x20`: ST (Standard)
  - `0x00`: ECO (Economy)
  - `0x40`: SL (Sleep)
  - `0x60`: Transient (ignored)

### Sliding Window

The integration uses a sliding window to validate data:
- Keeps the last N frames (default: 5)
- Requires 3 consecutive confirmations to validate a value
- Tolerance for transient modes (0x60)

### Order Guard

If enabled, the integration respects the VL403 mode transition order:
- ST → ECO
- ECO → SL (or ECO → ST)
- SL → ST

Invalid transitions are blocked to avoid errors.

## 🆘 Troubleshooting

### ❌ "Unable to connect"

1. Check the EW11A IP address (may change on reboot)
2. Test: `telnet <EW11A_IP> 8899`
3. Verify that the EW11A is powered on

### ❌ "The mode keeps changing"

**This is normal!** In ECO mode, the spa automatically alternates between Standard/Eco/Sleep to save energy.

### ❌ "Values are not updating"

1. Go to integration **Options**
2. Increase "Data reliability" to **7** or **10**

### 💡 Enable detailed logs

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.balboa_gs500z: debug
```

📖 **More help**: [GitHub Issues](https://github.com/GevaudanBeast/Balboa-GS500z/issues)

## 🏗️ Technical Architecture

```
custom_components/balboa_gs500z/
├── __init__.py           # Entry point, integration setup
├── manifest.json         # Integration metadata
├── const.py             # Constants
├── config_flow.py       # Initial configuration
├── tcp_client.py        # TCP client for EW11A
├── coordinator.py       # Data coordinator with sliding window
├── climate.py           # Climate entity (spa)
├── binary_sensor.py     # Binary sensor entity (heater)
├── strings.json         # Translation strings
└── translations/
    ├── en.json         # English translation
    └── fr.json         # French translation
```

## 🔐 Security

This integration is designed for local network use. No data is sent outside.

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests

## 📧 Support

For any questions or issues:
- Open an issue on GitHub
- Check Home Assistant logs

## ⚠️ Warnings

- This integration is provided "as is" without warranty
- Test first in a development environment
- **Read-only mode**: This integration cannot control the spa (see [IR_CONTROL.en.md](IR_CONTROL.en.md) for control)
- **Never** connect the EW11A to the VL403 keypad connectors (risk of malfunction)
- Connect the EW11A only to the designated RS-485 connectors
- Backup your Home Assistant configuration before installation

## 🙏 Acknowledgments

- Balboa for the GS500Z protocol
- The Home Assistant community
- All contributors

## 📚 Resources

- [Home Assistant Documentation](https://www.home-assistant.io/)
- [HACS](https://hacs.xyz/)
- [RS-485 Protocol](https://en.wikipedia.org/wiki/RS-485)

---

Made with ❤️ for the Home Assistant community
