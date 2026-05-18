# Balboa GS500Z/GS501Z+ — Home Assistant Integration

[![Validate](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Validate/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Hassfest](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Hassfest/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **FR** : Intégration Home Assistant pour le spa Balboa GS500Z/GS501Z+ avec
> panneau VL403. Lecture RS-485 via J18, contrôle des boutons via J1.
>
> **EN**: Home Assistant integration for Balboa GS500Z/GS501Z+ spa with VL403
> panel. RS-485 reading via J18, button control via J1.

> **Etat du projet (mai 2026) :**
> La **lecture RS-485** via J18 est pleinement operationnelle.
> Le **controle** (boutons, mode, cycles) est operationnel via firmware
> ESPHome v1.5.3 + optocoupleurs TLP281-4 sur J1 (VL403).
> Le dashboard Lovelace cible est disponible dans `lovelace/`.
>
> **Project status (May 2026):**
> **RS-485 reading** via J18 is fully operational.
> **Control** (buttons, mode, filtration cycles) is operational via ESPHome
> firmware v1.5.3 + TLP281-4 optocouplers on J1 (VL403).
> The target Lovelace dashboard is available in `lovelace/`.

---

## Fonctionnalites actuelles / Current features

### FR — Lecture (operationnelle) / EN — Reading (operational)

- Temperature de l'eau en temps reel / Real-time water temperature
- Consigne de temperature / Target temperature (setpoint)
- Mode de fonctionnement : Standard (ST), Economique (ECO), Sommeil (SL) / Operating mode: Standard (ST), Eco (ECO), Sleep (SL)
- Etat du chauffage (actif/inactif) / Heater state (on/off)
- Etat de la pompe (OFF/LOW/HIGH) / Pump state (OFF/LOW/HIGH)
- Etat du blower / Blower state
- Etat de la lumiere / Light state

### FR — Controle (operationnel via ESPHome) / EN — Control (operational via ESPHome)

- **Light / Blower / Pump / Temp** : via optocoupleurs TLP281-4 sur J1 (firmware ESPHome v1.5.3)
- **Mode** (ST→ECO→SL) : combinaison Temp+Light via optocoupleurs
- **Cycles filtration** : combinaison Temp+Pump via optocoupleurs
- **Temperature de consigne** : N pressions Temp via ESPHome (a implementer dans HA)
- **Light / Blower / Pump / Temp** : via TLP281-4 optocouplers on J1 (ESPHome firmware v1.5.3)
- **Mode** (ST→ECO→SL): Temp+Light combination via optocouplers
- **Filtration cycles**: Temp+Pump combination via optocouplers
- **Temperature setpoint**: N Temp button presses via ESPHome (to implement in HA)

---

## Prerequis / Prerequisites

**FR** :
- Home Assistant 2023.1 ou superieur
- Spa Balboa GS500Z ou GS501Z+ avec panneau VL403
- Module RS-485 TTL485 (MAX485) sur J18, 9600 baud
- ESP8266 NodeMCU + optocoupleurs TLP281-4 sur J1 (firmware ESPHome v1.5.3)

**EN**:
- Home Assistant 2023.1 or higher
- Balboa GS500Z or GS501Z+ spa with VL403 panel
- RS-485 TTL485 (MAX485) module on J18, 9600 baud
- ESP8266 NodeMCU + TLP281-4 optocouplers on J1 (ESPHome firmware v1.5.3)

---

## Installation

### HACS (recommande)

1. HACS -> Integrations -> menu (...)  -> Depots personnalises
2. Ajouter : `https://github.com/GevaudanBeast/Balboa-GS500z`
3. Rechercher "Balboa GS500Z" et installer
4. Redemarrer Home Assistant

### Manuelle

Copier `custom_components/balboa_gs500z/` dans votre dossier `custom_components/`.

---

## Configuration

1. Configuration -> Integrations -> + Ajouter une integration
2. Rechercher "Balboa GS500Z Spa"
3. Renseigner l'adresse IP de l'EW11A et le port (defaut : 8899)

### Options

- **Taille fenetre glissante** (3-20) : nombre de trames pour validation (defaut : 5)
- **Garde-fou d'ordre** : valide les transitions ST->ECO->SL->ST (defaut : active)

---

## Entites creees / Exposed entities

### FR — Composant HA (`custom_components/balboa_gs500z`)

| Entite | Type | Description |
|--------|------|-------------|
| `climate.spa_balboa` | Climate | Temperature, consigne, mode ST/ECO/SL |
| `binary_sensor.spa_heater` | Binary sensor | Etat chauffage / Heater state |

### FR — Firmware ESPHome (`balboa-spa-control`) / EN — ESPHome firmware

| Entite | Type | Description FR | EN |
|--------|------|---|---|
| `sensor.*_01_spa_eau_temp` | Sensor | Temperature eau | Water temp |
| `sensor.*_02_spa_consigne` | Sensor | Consigne | Setpoint |
| `text_sensor.*_03_spa_mode` | Text sensor | Mode ST/ECO/SL | Mode |
| `binary_sensor.*_04a_spa_chauffage` | Binary sensor | Chauffage | Heater |
| `binary_sensor.*_04b_spa_lumiere` | Binary sensor | Lumiere | Light |
| `text_sensor.*_05_spa_diag` | Text sensor | Diagnostic (OK/HH/OH/IC/COMM) | Diagnostic |
| `button.*_03a` a `03f` | Buttons | Boutons VL403 + combinaisons | VL403 buttons + combos |
| `sensor.*_91_spa_wifi_signal` | Sensor | RSSI WiFi | WiFi RSSI |
| `binary_sensor.*_98_spa_en_ligne` | Binary sensor | ESP en ligne | ESP online |

> Le prefixe `*` correspond a `balboa_spa_control` (nom du device ESPHome).
> Voir `lovelace/README.md` pour la liste complete et le statut de chaque entite.
>
> The `*` prefix corresponds to `balboa_spa_control` (ESPHome device name).
> See `lovelace/README.md` for the full list and implementation status.

---

## Configuration EW11A

| Parametre | Valeur |
|-----------|--------|
| Mode | TCP Server |
| Baud Rate | 9600 |
| Data Bits | 8 |
| Stop Bits | 1 |
| Parity | None |
| Port | 8899 |

---

## Exemples d'automatisations

```yaml
# Passer en mode ECO la nuit
automation:
  - alias: "Spa - Mode ECO la nuit"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: "eco"
```

---

## Architecture technique

```
custom_components/balboa_gs500z/
  __init__.py        # Setup integration
  manifest.json      # Metadonnees HACS
  const.py           # Constantes protocole
  config_flow.py     # Configuration UI
  tcp_client.py      # Client TCP EW11A — parsing trames RS-485
  coordinator.py     # Fenetre glissante + memoire SL (v5.8.4)
  climate.py         # Entite climate
  binary_sensor.py   # Entite heater
  services.yaml      # Definition services HA
  strings.json       # Traductions
  translations/      # EN + FR
```

---

## Protocole RS-485

Les trames sont au format `[643F2B...]` (27 octets, 54 chars hex).

| Byte | Role | Note |
|------|------|------|
| 3 | Temperature eau | valeur * 0.5 = degC |
| 5 | Consigne | valeur * 0.5 = degC |
| 17 | Pompe + Blower | bit7=blower, bits0-6=vitesse pompe |
| 19 | Heater | bit0 = ON/OFF (universel tous modes) |
| 20 | Lumiere | 0x02/0x03 = ON |
| 23 | Mode | 0x20=ST, 0x00=ECO, 0x40=SL, 0x60=transitoire |

Documentation complete : `PROTOCOL.md`

---

## Debogage

### Activer les logs debug

```yaml
logger:
  default: info
  logs:
    custom_components.balboa_gs500z: debug
```

### Tester la connexion

```bash
telnet <IP_EW11A> 8899
```

---

## Limitations connues / Known limitations

- **J18 lecture seule / J18 read-only** : `set_temperature` et `set_mode`
  dans le composant HA sont des stubs. Le controle passe par le firmware
  ESPHome sur J1 (boutons VL403). /
  `set_temperature` and `set_mode` in the HA component are stubs. Control
  goes through the ESPHome firmware on J1 (VL403 buttons).
- **WiFi ESP marginal** (~-77 dBm) : stable uniquement alimente via USB. /
  Stable only when powered via USB.
- **Mode SL** : b23 peut valoir 0x00 une fois SL stabilise (identique a ECO).
  Resolu par la memoire SL de 120 s dans le coordinateur. /
  b23 can be 0x00 once SL is stable (same as ECO). Resolved by the 120s SL
  memory in the coordinator.
- **GPIO16 (D0) interdit** pour les sorties optocoupleur : transitoire HIGH
  au boot (cf. FIX-1 firmware v1.5.3). Utiliser GPIO15 (D8). /
  GPIO16 (D0) must not be used for optocoupler outputs: HIGH glitch at boot
  (see FIX-1 firmware v1.5.3). Use GPIO15 (D8) instead.

---

## Documentation

| Fichier / File | Contenu FR | EN content |
|---------|---------|---------|
| `PROTOCOL.md` | Protocole RS-485 complet, mapping bytes, algo v5.8.4 | Full RS-485 protocol, byte mapping, v5.8.4 algo |
| `HARDWARE.md` | Architecture materielle, cablage, composants | Hardware architecture, wiring, components |
| `BUS_J1_PROTOCOL.md` | Protocole bus J1/J2 + plan cablage optocoupleurs | J1/J2 bus protocol + optocoupler wiring |
| `esphome-tools/balboa-spa-control/README.md` | Firmware ESPHome v1.5.3, entites, GPIO | ESPHome firmware v1.5.3, entities, GPIO |
| `lovelace/README.md` | Dashboard Lovelace cible + statut entites | Target Lovelace dashboard + entity status |
| `APPROACHES_TESTED.md` | Toutes les pistes testees et leurs resultats | All tested approaches and results |
| `IR_CODES.md` | Codes IR confirmes + resultats brute force | Confirmed IR codes + brute force results |
| `INSTALL.md` | Instructions d'installation detaillees | Detailed installation instructions |

---

## Licence

MIT — voir `LICENSE`.

## Contribution

Issues et pull requests bienvenus.
Voir `CONTRIBUTING.md` pour les conventions.
