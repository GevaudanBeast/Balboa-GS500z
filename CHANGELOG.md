# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflows for automated CI/CD
- Release automation script
- Development installation script
- Validation and testing scripts

## [0.1.0] - 2025-01-13

### Added
- Initial development release of Balboa GS500Z Home Assistant integration
- **⚠️ This is a preview version - not yet tested on real hardware**
- Climate entity for spa control
  - Current water temperature display
  - Target temperature control (15-40°C)
  - Preset modes: Standard (ST), Eco (ECO), Sleep (SL)
- Binary sensor for heater status
- TCP client with auto-reconnect for EW11A RS-485 WiFi bridge
- RS-485 frame parsing (27-byte protocol)
- Sliding window data validation
  - Configurable window size (3-20 frames)
  - 3-frame consecutive validation
  - Transitoire mode tolerance (0x60)
- Mode order guard (ST → ECO → SL → ST)
- Config flow for easy setup
- Options flow for runtime configuration
- Services:
  - `balboa_gs500z.set_temperature`
  - `balboa_gs500z.set_mode`
- Multi-language support (English, French)
- Comprehensive documentation:
  - README.md
  - PROTOCOL.md
  - EXAMPLES.md
- HACS compatibility

### Known Issues
- Write commands (setpoint and mode change) require validation on specific installations
- Checksum calculation may need adjustment based on your GS500Z firmware version

### Future Enhancements
- Add support for additional sensors (filters, pumps, etc.)
- Implement diagnostics platform
- Add support for multiple spas
- Enhanced error recovery
- Configurable temperature units (C/F)

---

## Legend
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

---

For upgrade instructions and breaking changes, please refer to the [README.md](README.md).
