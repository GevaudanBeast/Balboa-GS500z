# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-14

### Changed
- **🔒 Major security and code quality improvements** (complete 3-phase code review)
- **📚 Bilingual documentation** (French and English versions)
- **⚠️ READ-ONLY MODE**: Integration converted to monitoring-only after extensive RS-485 write testing
  - VL403 keypad uses proprietary protocol (not standard RS-485)
  - Write operations removed from integration
  - IR control solution documented as alternative (see IR_CONTROL.md)

### Added
- **Security improvements**:
  - Buffer overflow protection in TCP client (4096 bytes max)
  - Callback task tracking to prevent silent crashes
  - Input validation with multiple layers
  - Race condition protection with asyncio.Lock
  - Comprehensive error handling throughout
- **Documentation**:
  - README.en.md (complete English translation)
  - info.md (bilingual short description for HACS)
  - LANGUAGE_VERSIONS.md (translation status tracking)
  - IR_CONTROL.md (complete guide for ESP32 IR control solution)
  - Enhanced docstrings and inline comments in all Python files
- **Code quality**:
  - Complete type hints across all modules
  - Detailed method documentation
  - Robust cleanup in __init__.py with timeout handling
  - Frame validation in coordinator with sanity checks

### Removed
- Write services (`balboa_gs500z.set_temperature`, `balboa_gs500z.set_mode`)
  - Not functional due to VL403 proprietary protocol
  - Use physical keypad or IR control (ESP32) instead
  - See IR_CONTROL.md for control solution

### Fixed
- TCP client resource cleanup on error
- Proper connection timeout handling
- Graceful handling of corrupted RS-485 frames
- Entity availability checks now include data validation

### Security
- Buffer overflow protection in TCP client
- Safe callback execution with exception handling
- Input validation for all configuration parameters
- Protection against race conditions in data updates

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
