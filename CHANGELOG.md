# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-04-21

### Changed
- `BUS_J1_PROTOCOL.md` : réécriture complète suite à la découverte du fonctionnement
  réel du VL403 — matrice de courts-circuits (pas de bus série multiplexé).
  Plan EL817 porte-OR abandonné, remplacé par 4 optocoupleurs individuels
  (TLP281-4 ou 4× EL817), un par fonction (TEMP/BLOWER/POMPE/LUMIÈRE)
- `APPROACHES_TESTED.md` : ajout section 3.6 (plan porte-OR abandonné) et
  section 3.7 (découverte majeure : VL403 = matrice courts-circuits avec pinout
  complet confirmé pin1=TEMP, pin2=BLOWER, pin6=POMPE, pin7=LUMIÈRE, pin8=COMMUN,
  et tableau des combinaisons de boutons)
- `HARDWARE.md` : mise à jour avec le vrai fonctionnement VL403 (courts-circuits),
  tableau des combinaisons, plan câblage optocoupleurs individuels

### Fixed
- Correction de la documentation BUS_J1_PROTOCOL.md qui décrivait à tort une
  architecture bus multiplexé (VL700S) non applicable au VL403

## [0.2.0] - 2026-04-21

### Added
- `HARDWARE.md` : architecture materielle complete (GS501Z+, VL403, EW11A, ESP8266)
- `APPROACHES_TESTED.md` : toutes les pistes explorees et leurs resultats
- `IR_CODES.md` : codes IR confirmes (Light/Blower/Pump) + resultats brute force 248 codes
- `BUS_J1_PROTOCOL.md` : protocole bus J1/J2 et plan de cablage EL817 (porte OR)

### Changed
- `tcp_client.py` : ajout parsing byte 17 (pompe LOW/HIGH, blower), byte 20 (lumiere),
  exposition des bytes bruts `_b19` et `_b23` dans la trame parsee
- `tcp_client.py` : decode mode depuis byte 23 (strictMode) au lieu de comparaisons
  directes sur MODE_ST/ECO/SL
- `tcp_client.py` : methodes `build_setpoint_command()` et `build_mode_command()`
  transformees en stubs explicites (levent NotImplementedError, J18 est RX-only)
- `coordinator.py` : ajout memoire SL v5.8.4 (fenetre 120s, seuil 2 observations)
  pour eviter la confusion SL/ECO apres stabilisation du mode SL
- `coordinator.py` : validation fenetre glissante etendue a pompe, blower, lumiere
  (vote majoritaire 2/3)
- `coordinator.py` : `async_set_temperature()` et `async_set_mode()` indiquent
  clairement que les commandes ne sont pas implementees (retournent False)
- `PROTOCOL.md` : mapping complet de tous les bytes confirmes (17/18/19/20/23),
  valeurs connues de b19, algorithme v5.8.4 avec memoire SL, garde-fou d'ordre
- `README.md` : reflet de l'etat reel du projet (lecture operationnelle,
  controle en developpement)

### Fixed
- Correction de la detection de mode SL qui retombait incorrectement en ECO
  apres stabilisation (b23=0x00 en SL stable)

## [0.1.1] - 2025-11-16

### Changed
- Version bump to 0.1.1
- Minor updates and improvements

## [0.1.0] - 2025-01-13

### Added
- GitHub Actions workflows for automated CI/CD
- Release automation script
- Development installation script
- Validation and testing scripts

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
