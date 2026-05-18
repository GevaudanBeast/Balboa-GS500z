# Balboa GS500Z/GS501Z+ — ESPHome + Home Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ESPHome](https://img.shields.io/badge/ESPHome-1.5.3-blue.svg)](esphome-tools/balboa-spa-control/)

> **FR** : Intégration Home Assistant pour spa Balboa GS500Z/GS501Z+ avec
> panneau VL403, basée sur **ESPHome** (pas de composant HACS).
> Lecture RS-485 via J18 + contrôle des boutons via J1 (optocoupleurs).
>
> **EN**: Home Assistant integration for Balboa GS500Z/GS501Z+ spa with VL403
> panel, **ESPHome-based** (no HACS component required).
> RS-485 reading via J18 + button control via J1 (optocouplers).

---

## FR — Approche / EN — Approach

**FR** : Ce projet **n'est pas un composant HACS**. Il s'appuie sur :

1. Un **firmware ESPHome** sur un ESP8266 NodeMCU qui :
   - Lit le bus RS-485 du spa via un module TTL485 sur J18
   - Simule les boutons du panneau VL403 via 4 optocoupleurs TLP281-4 sur J1
2. La **découverte native ESPHome** dans Home Assistant (toutes les entités
   apparaissent automatiquement après ajout de l'intégration ESPHome).
3. Un **dashboard Lovelace** (YAML) fourni dans `lovelace/`.

**EN**: This project is **not a HACS component**. It relies on:

1. An **ESPHome firmware** on an ESP8266 NodeMCU that:
   - Reads the spa RS-485 bus via a TTL485 module on J18
   - Simulates VL403 panel buttons via 4 TLP281-4 optocouplers on J1
2. **Native ESPHome discovery** in Home Assistant (all entities appear
   automatically after adding the ESPHome integration).
3. A **Lovelace dashboard** (YAML) provided in `lovelace/`.

---

## FR — Fonctionnalités / EN — Features

### FR — Lecture (opérationnelle) / EN — Reading (operational)

- Température eau / Water temperature
- Consigne de température / Target setpoint
- Mode : Standard (ST), Économique (ECO), Sommeil (SL) / Mode: Standard (ST), Eco (ECO), Sleep (SL)
- État du chauffage / Heater state
- État pompe (OFF/LOW/HIGH) / Pump state
- État blower, lumière / Blower, light states
- Codes diagnostic (HH, OH, IC, COMM) / Diagnostic codes

### FR — Contrôle (opérationnel via boutons) / EN — Control (operational via buttons)

- Light / Blower / Pump / Temp : pression sur bouton ESPHome / ESPHome button press
- Mode (ST→ECO→SL) : combinaison Temp+Light / Temp+Light combination
- Cycles filtration / Filtration cycles : combinaison Temp+Pump / Temp+Pump combination

---

## FR — Architecture matérielle / EN — Hardware architecture

```
                  ┌──────────────────────────────┐
                  │   Carte Balboa GS501Z+       │
                  │                              │
        J18 ──────┤ RS-485 (lecture/read-only)   │
                  │                              │
        J1 ───────┤ Bus boutons (VL403)          │
                  │                              │
        J2 ───────┤ VL403 panneau physique       │
                  │   (panel)                    │
                  └──────────────────────────────┘
                          │             │
                          │ J18         │ J1
                          ▼             ▼
                  ┌──────────┐   ┌──────────────┐
                  │ TTL485   │   │ TLP281-4 ×4  │
                  │ MAX485   │   │ (boutons)    │
                  └────┬─────┘   └──────┬───────┘
                       │ TXD            │ IN1..IN4
                       ▼                ▼
                  ┌──────────────────────────────┐
                  │      ESP8266 NodeMCU         │
                  │      ESPHome v1.5.3          │
                  └─────────────┬────────────────┘
                                │ WiFi
                                ▼
                  ┌──────────────────────────────┐
                  │      Home Assistant          │
                  │  Native ESPHome integration  │
                  └──────────────────────────────┘
```

Voir / See : `HARDWARE.md`, `BUS_J1_PROTOCOL.md`.

---

## FR — Prérequis / EN — Prerequisites

| Hardware | Quantité / Quantity | Note |
|---|---|---|
| Spa Balboa GS500Z ou/or GS501Z+ + panneau/panel VL403 | 1 | — |
| ESP8266 NodeMCU v2 | 1 | Pas d'ESP32-C6 mono-coeur / No ESP32-C6 single-core |
| Module TTL485 (MAX485) | 1 | RS-485 → TTL sur/on J18 |
| Optocoupleurs TLP281-4 (ou/or 4× EL817) | 1 | Simulation boutons J1 / J1 button sim |
| Câbles RJ45 + Dupont | — | T568B |
| Home Assistant 2023.1+ | — | Avec/with ESPHome integration |

---

## FR — Installation rapide / EN — Quick install

```bash
# 1. Cloner / Clone
git clone https://github.com/GevaudanBeast/Balboa-GS500z.git
cd Balboa-GS500z/esphome-tools/balboa-spa-control

# 2. Configurer les secrets / Configure secrets
cp secrets.yaml.example secrets.yaml
# Éditer secrets.yaml avec votre WiFi + clé API
# Edit secrets.yaml with your WiFi + API key

# 3. Flasher / Flash
pip install esphome
esphome run balboa-spa-control-v1.5.3.yaml

# 4. Dans Home Assistant / In Home Assistant :
# - L'ESP apparaît dans ESPHome → Accepter
# - The ESP appears in ESPHome → Accept
# - Coller lovelace/spa-dashboard.yaml dans un dashboard
# - Paste lovelace/spa-dashboard.yaml in a dashboard
```

Guide complet / Full guide : `INSTALL.md`.

---

## FR — Entités exposées / EN — Exposed entities

Toutes les entités sont préfixées `balboa_spa_control_` (nom du device ESPHome).

All entities are prefixed `balboa_spa_control_` (ESPHome device name).

| Entité / Entity | Type | FR | EN |
|---|---|---|---|
| `sensor.*_01_spa_eau_temp` | Sensor | Température eau | Water temp |
| `sensor.*_02_spa_consigne` | Sensor | Consigne | Setpoint |
| `text_sensor.*_03_spa_mode` | Text | Mode ST/ECO/SL | Mode |
| `binary_sensor.*_04a_spa_chauffage` | Binary | Chauffage | Heater |
| `binary_sensor.*_04b_spa_lumiere` | Binary | Lumière | Light |
| `text_sensor.*_05_spa_diag` | Text | Diagnostic | Diagnostic |
| `button.*_03a..03f` | Buttons | Boutons VL403 + combos | VL403 buttons + combos |
| `binary_sensor.*_98_spa_en_ligne` | Binary | ESP en ligne | ESP online |

Liste complète / Full list : `esphome-tools/balboa-spa-control/README.md`.

---

## FR — Dashboard Lovelace / EN — Lovelace dashboard

Un dashboard prêt à l'emploi est fourni dans `lovelace/spa-dashboard.yaml`.

A ready-to-use dashboard is provided in `lovelace/spa-dashboard.yaml`.

![Aperçu / Preview](docs/screenshot-lovelace.png)

Voir `lovelace/README.md` pour le détail des entités et helpers requis.

See `lovelace/README.md` for the entity and helper details.

---

## FR — Documentation / EN — Documentation

| Fichier / File | FR | EN |
|---|---|---|
| `HARDWARE.md` | Architecture matérielle, câblage, composants | Hardware architecture, wiring, components |
| `BUS_J1_PROTOCOL.md` | Bus J1/J2, pinout VL403, plan câblage optocoupleurs | J1/J2 bus, VL403 pinout, optocoupler wiring |
| `PROTOCOL.md` | Protocole RS-485 complet, mapping bytes | Full RS-485 protocol, byte mapping |
| `esphome-tools/balboa-spa-control/README.md` | Firmware ESPHome v1.5.3 | ESPHome firmware v1.5.3 |
| `lovelace/README.md` | Dashboard cible + statut entités | Target dashboard + entity status |
| `IR_CODES.md` | Codes IR (approche alternative) | IR codes (alternative approach) |
| `APPROACHES_TESTED.md` | Pistes testées et résultats | Tested approaches and results |
| `INSTALL.md` | Guide d'installation détaillé | Detailed installation guide |
| `CHANGELOG.md` | Historique des changements | Change history |

---

## FR — Limitations connues / EN — Known limitations

- **J18 lecture seule / read-only** : pas d'écriture possible via RS-485.
  Le contrôle passe par J1 (boutons). / No write via RS-485. Control goes
  through J1 (buttons).
- **GPIO16 (D0) interdit/forbidden** pour les sorties optocoupleur :
  transitoire HIGH au boot (cf./see FIX-1 firmware v1.5.3).
- **HY-M154** : module à vérifier au multimètre avant câblage
  (cathode/anode-commun). / Module to check with multimeter before wiring
  (common cathode/anode).
- **ESP32-C6 mono-cœur / single-core** : déconseillé pour combiner RS-485 +
  WiFi temps réel. / Not recommended for combining real-time RS-485 + WiFi.

---

## FR — Compatibilité / EN — Compatibility

| Spa / Panel | Statut / Status | Note |
|---|---|---|
| GS500Z / VL403 | ✅ Validé / Validated | Configuration de référence |
| GS501Z+ / VL403 | ✅ Validé / Validated | Identique côté soft / Same software |
| GS510SZ / VL700S | ❌ Non compatible | Voir/See MagnusPer (architecture différente) |
| GS100 / VL260 | ❌ Non compatible | Voir/See kgstorm (UART) |

---

## FR — Licence et contribution / EN — License and contribution

MIT — voir/see `LICENSE`.

**FR** : Issues et pull requests bienvenus. Le projet vise à rester simple
(firmware ESPHome + YAML), pas un composant HACS.

**EN**: Issues and pull requests welcome. The project aims to stay simple
(ESPHome firmware + YAML), not a HACS component.

Voir / See `CONTRIBUTING.md`.
