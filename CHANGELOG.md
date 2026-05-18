# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed (BREAKING)
- **`custom_components/balboa_gs500z/`** : suppression complete de l'ancien
  composant HACS. Le projet est desormais purement base sur **ESPHome**
  + decouverte native HA + dashboard Lovelace.
- **`hacs.json`** : supprime, le projet n'est plus un composant HACS.
- **`.github/workflows/`** : suppression des workflows Hassfest, HACS
  validation et release (lies au composant HA supprime).
- **`scripts/`** : suppression des scripts bash lies au composant HA.
- **`EXAMPLES.md`, `UX_ANALYSIS.md`, `UX_IMPROVEMENTS.md`** : suppression,
  contenu base sur l'ancien composant HACS.

### Changed
- `README.md` : reecriture complete bilingue FR/EN, focus sur l'approche
  ESPHome + Lovelace (plus de composant HACS), nouvelles tables d'entites
  et architecture materielle, badges adaptes.
- `INSTALL.md` : reecriture complete bilingue FR/EN, supprime l'installation
  du composant HACS, focus sur le flux ESPHome.
- `CONTRIBUTING.md` : reecriture bilingue FR/EN, conventions adaptees au
  scope reduit (firmware + Lovelace + docs).

### Added
- `lovelace/spa-dashboard.yaml` : dashboard Lovelace cible — grille 3×2
  (thermostat, blower, lumiere, pompe, mode, cycles) + carte details
  (temperature sortie rechauffeur, heater, saisie temp en cours).
  Les entites referancees incluent des entites cibles firmware v1.6+
  non encore implementees (voir `lovelace/README.md`).
- `lovelace/README.md` (FR + EN) : statut d'implementation de chaque
  entite Lovelace, liste des entites ESPHome v1.5.3 disponibles, roadmap
  v1.6+, helpers HA a creer.
- `esphome-tools/balboa-spa-control/balboa-spa-control-v1.5.3.yaml` :
  firmware ESPHome valide pour ESP8266 NodeMCU pilotant la lecture
  RS-485 (TTL485 sur J18) + simulation des boutons VL403 (TLP281-4 sur J1).
- `esphome-tools/balboa-spa-control/README.md` : documentation cablage,
  pinout, entites HA exposees, historique des versions.
- `esphome-tools/balboa-spa-control/secrets.yaml.example` : template de
  secrets (wifi, AP fallback, cle API, OTA).
- `.gitignore` : exclusion `esphome-tools/*/secrets.yaml`, `.esphome/`,
  `build/`.

### Fixed (firmware v1.5.3 vs v1.5.2)
- **[FIX-1]** `opto_light` deplace de GPIO16 (D0) vers GPIO15 (D8) —
  GPIO16 (domaine RTC) genere un transitoire HIGH au boot qui declenchait
  le bouton Light a chaque redemarrage de l'ESP. GPIO15 demarre LOW grace
  au pull-down hardware du NodeMCU.
- **[FIX-2]** Globales `last_raw_frame` et `diag_code` passees de
  `std::string` a `char[]` statique — les `std::string` fragmentaient
  le heap (~45 KB) a chaque trame (10-12 trames/s), provoquant des
  crash/WDT (reboots toutes les 20-155 min).

### Changed
- `README.md` : mise a jour statut projet (mai 2026), prerequis hardware
  (TTL485 + TLP281-4), section controle operationnel, entites ESPHome,
  limitations connues, table documentation — contenu FR + EN.
- `INSTALL.md` : ajout section firmware ESPHome (secrets, flash, decouverte
  HA) + section dashboard Lovelace (installation, helpers a creer) —
  contenu FR + EN. Mise a jour prerequis hardware.
- `HARDWARE.md` / `BUS_J1_PROTOCOL.md` : **alignement du pinout RJ45 VL403
  sur la convention du briefing** (loquet bas, lecture gauche→droite,
  face contacts visibles) :
  pin 1 = Marron (COMMUN +5 V), pin 2 = Bleu (LIGHT), pin 3 = Jaune (PUMP),
  pin 7 = Orange (BLOWER), pin 8 = Gris (TEMP). Les pins 4/5/6 (Vert/Rouge/Noir)
  portent vraisemblablement GND/Data/Clock du bus d'affichage 24-bit.
  Toutes les tables de combinaisons et de câblage ont été re-numérotées.
- `HARDWARE.md` : documentation des modules réellement utilisés —
  **TTL485 (MAX485)** côté J18 pour la lecture RS-485, et un module
  **optocoupleur PC817 ×4** côté J1 pour la simulation des boutons.
- `HARDWARE.md` : clarification de l'architecture J1/J2 partagée
  (ESP + HY-M154 sur J1, VL403 sur J2 — les deux cohabitent sans conflit
  puisque le VL403 n'est pas rétroéclairé).
- `HARDWARE.md` : ajout d'une section **alimentation 5 V** précisant que
  le module HY-M154 nécessite 5 V côté IN (un GPIO 3,3 V est insuffisant)
  et la procédure de câblage via VIN sur NodeMCU.
- `HARDWARE.md` : ajout d'une section **choix de l'ESP** (ESP8266 NodeMCU v2
  validé, ESP32-WROOM-32 dual-core recommandé en upgrade, ESP32-C6
  mono-core à éviter pour la combinaison RS-485 + WiFi temps réel).
- `HARDWARE.md` : ajout d'une **FAQ** (TTL485 + HY-M154, J2 pour
  l'optocoupleur, compatibilité carte kgstorm/VL260).
- `BUS_J1_PROTOCOL.md` : ajout du module **HY-M154** comme **candidat**
  (et non solution validée), avec encart de vérifications préalables :
  (1) alimentation 5 V côté IN obligatoire ; (2) **polarité côté sortie
  à mesurer au multimètre** — certains modules PC817 sont cathode-commun
  alors que le bus J1 est anode-commun. TLP281-4 ou 4× EL817 nus restent
  la solution de repli sûre.
- `BUS_J1_PROTOCOL.md` : ajout de l'option **bus partagé J1/J2** (sans
  splitter) en plus de l'option splitter existante. Précision sur le
  diviseur de tension 1 kΩ + 2 kΩ obligatoire pour toute lecture GPIO
  sur le bus J1 (5 V → 3,3 V).

### TODO (matériel à mesurer / valider)
- [ ] **HY-M154 polarité sortie** : mesurer cathode/anode commune au
  multimètre avant câblage définitif (cf. `BUS_J1_PROTOCOL.md` §2).
- [ ] **Pins 4/5/6 J1** : confirmer au multimètre que Vert=GND, Rouge=Data,
  Noir=Clock (hypothèse héritée du protocole kgstorm 24-bit).
- [ ] **Durées d'impulsion** : calibrer expérimentalement les durées
  minimales pour qu'un appui simulé soit reconnu par le VL403.

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
