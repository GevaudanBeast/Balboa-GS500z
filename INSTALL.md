# Installation Guide — Balboa GS500Z / GS501Z+

> **FR** : Ce guide couvre l'installation complète : matériel, firmware
> ESPHome, intégration Home Assistant et dashboard Lovelace. Aucun
> composant HACS n'est requis.
>
> **EN**: This guide covers the full installation: hardware, ESPHome
> firmware, Home Assistant integration and Lovelace dashboard. No HACS
> component required.

---

## FR — Table des matières / EN — Table of contents

1. [Prérequis / Prerequisites](#1-prérequis--prerequisites)
2. [Câblage matériel / Hardware wiring](#2-câblage-matériel--hardware-wiring)
3. [Firmware ESPHome](#3-firmware-esphome)
4. [Découverte dans Home Assistant / Discovery in Home Assistant](#4-découverte-dans-home-assistant--discovery-in-home-assistant)
5. [Dashboard Lovelace](#5-dashboard-lovelace)
6. [Vérification / Verification](#6-vérification--verification)
7. [Dépannage / Troubleshooting](#7-dépannage--troubleshooting)

---

## 1. Prérequis / Prerequisites

### FR — Matériel / EN — Hardware

| Composant / Component | Quantité / Qty | Note |
|---|---|---|
| Spa Balboa GS500Z/GS501Z+ + VL403 | 1 | — |
| ESP8266 NodeMCU v2 | 1 | Pas d'ESP32-C6 mono-cœur / No ESP32-C6 single-core |
| Module TTL485 (MAX485) | 1 | Sur/On J18 |
| Optocoupleurs TLP281-4 ou/or 4× EL817 | 1 | Sur/On J1 |
| Résistances 220 Ω | 4 | Si EL817 nus / If raw EL817 |
| Câble RJ45 + Dupont | — | T568B recommandé / recommended |
| Alimentation 5 V régulée | 1 | Via USB ou/or VIN NodeMCU |

### FR — Logiciel / EN — Software

- **Home Assistant** ≥ 2023.1 avec intégration ESPHome / with ESPHome integration
- **Python** ≥ 3.8 (pour flasher l'ESP / to flash the ESP)
- **ESPHome CLI** : `pip install esphome`

### FR — Avertissement / EN — Warning

⚠️ **FR** : Avant toute intervention sur le spa, **couper l'alimentation**
au disjoncteur.

⚠️ **EN**: Before any intervention on the spa, **cut power** at the breaker.

---

## 2. Câblage matériel / Hardware wiring

### 2.1 Module TTL485 sur J18 (lecture RS-485 / RS-485 reading)

| TTL485 | ESP8266 NodeMCU |
|---|---|
| VCC | 3V3 |
| GND | GND |
| TXD | D2 (GPIO4) — **TXD du module, pas RXD / module TXD, not RXD** |
| D+ / A | J18 borne / terminal A |
| D− / B | J18 borne / terminal B |

### 2.2 Optocoupleurs TLP281-4 sur J1 (boutons VL403 / VL403 buttons)

| Canal / Channel | ESP GPIO | NodeMCU | Pin RJ45 VL403 | Couleur / Color |
|---|---|---|---|---|
| IN1 = BLOWER | GPIO14 | D5 | pin 7 | Orange |
| IN2 = POMPE/PUMP | GPIO12 | D6 | pin 3 | Jaune / Yellow |
| IN3 = TEMP | GPIO13 | D7 | pin 8 | Gris / Grey |
| IN4 = LIGHT | **GPIO15** | **D8** | pin 2 | Bleu / Blue |

> ⚠️ **FR** : Ne **PAS** utiliser GPIO16 (D0) pour les sorties optocoupleur :
> transitoire HIGH au boot (cf. FIX-1 firmware v1.5.3).
>
> ⚠️ **EN**: Do **NOT** use GPIO16 (D0) for optocoupler outputs:
> HIGH glitch at boot (see FIX-1 firmware v1.5.3).

### 2.3 Côté VL403 / VL403 side

- HVCC module → pin 1 RJ45 (Marron/Brown, Commun +5 V)
- HGND module → GND côté/side VL403
- **Retirer les cavaliers rouges d'isolation / Remove red isolation jumpers**

Pinout complet / Full pinout : `BUS_J1_PROTOCOL.md` §1.

### 2.4 Alimentation / Power supply

⚠️ **FR** : Alimenter le NodeMCU via **VIN à 5 V** (USB ou alim externe).
Le côté IN du module optocoupleur nécessite 5 V — un GPIO 3,3 V seul est
insuffisant pour déclencher de manière fiable.

⚠️ **EN**: Power the NodeMCU via **VIN at 5 V** (USB or external supply).
The optocoupler module IN side requires 5 V — a 3.3 V GPIO alone is not
enough to trigger reliably.

---

## 3. Firmware ESPHome

### 3.1 FR — Préparer les secrets / EN — Prepare secrets

```bash
cd esphome-tools/balboa-spa-control
cp secrets.yaml.example secrets.yaml
```

**FR** : Éditer `secrets.yaml` et renseigner :

**EN**: Edit `secrets.yaml` and fill in:

```yaml
wifi_ssid: "VotreSSID"
wifi_password: "VotreMotDePasse"
ap_password: "MotDePasseAPFallback"
api_encryption_key: "..."   # openssl rand -base64 32
ota_password: "..."
```

### 3.2 FR — Installer ESPHome / EN — Install ESPHome

```bash
pip install esphome
```

### 3.3 FR — Flasher l'ESP / EN — Flash the ESP

**FR** : Connecter l'ESP8266 NodeMCU en USB, puis :

**EN**: Connect the ESP8266 NodeMCU via USB, then:

```bash
esphome run balboa-spa-control-v1.5.3.yaml
```

**FR** : Les mises à jour suivantes peuvent se faire **en OTA** (sans fil)
via la même commande, sans connexion USB.

**EN**: Subsequent updates can be done **OTA** (wirelessly) via the same
command, without USB connection.

### 3.4 FR — Vérifier les logs / EN — Check logs

```bash
esphome logs balboa-spa-control-v1.5.3.yaml
```

**FR** : Vous devez voir des trames `[643F2B...]` toutes les ~100 ms ainsi
que des lignes `[balboa]` indiquant le décodage.

**EN**: You should see `[643F2B...]` frames every ~100 ms plus `[balboa]`
log lines showing the decoding.

---

## 4. Découverte dans Home Assistant / Discovery in Home Assistant

### 4.1 FR — Ajouter l'intégration ESPHome / EN — Add the ESPHome integration

**FR** : Home Assistant détecte automatiquement le périphérique ESPHome sur
le réseau. Sinon :

**EN**: Home Assistant automatically detects the ESPHome device on the
network. Otherwise:

1. **FR** : Paramètres → Appareils et services → + Ajouter une intégration → ESPHome.
   **EN**: Settings → Devices and services → + Add integration → ESPHome.
2. **FR** : Hôte : adresse IP de l'ESP (ex: `192.168.1.50`).
   **EN**: Host: ESP IP address (e.g. `192.168.1.50`).
3. **FR** : Renseigner la **clé API** de `secrets.yaml`.
   **EN**: Enter the **API key** from `secrets.yaml`.

### 4.2 FR — Entités créées automatiquement / EN — Auto-created entities

**FR** : Toutes les entités du firmware sont découvertes automatiquement.

**EN**: All firmware entities are auto-discovered.

| Entité / Entity | Type |
|---|---|
| `sensor.balboa_spa_control_01_spa_eau_temp` | Température eau / Water temp |
| `sensor.balboa_spa_control_02_spa_consigne` | Consigne / Setpoint |
| `text_sensor.balboa_spa_control_03_spa_mode` | Mode ST/ECO/SL |
| `binary_sensor.balboa_spa_control_04a_spa_chauffage` | Chauffage / Heater |
| `binary_sensor.balboa_spa_control_04b_spa_lumiere` | Lumière / Light |
| `text_sensor.balboa_spa_control_05_spa_diag` | Diagnostic |
| `button.balboa_spa_control_03a..03f` | Boutons VL403 + combos |

Liste complète / Full list : `esphome-tools/balboa-spa-control/README.md`.

---

## 5. Dashboard Lovelace

### 5.1 FR — Créer les helpers / EN — Create helpers

**FR** : Avant d'utiliser le dashboard, créer dans HA → Paramètres → Assistants :

**EN**: Before using the dashboard, create in HA → Settings → Helpers:

| Helper | Type | Note |
|---|---|---|
| `input_boolean.spa_temp_pending` | Input Boolean | Changement consigne en cours / Setpoint change in progress |

### 5.2 FR — Installer le dashboard / EN — Install the dashboard

1. **FR** : HA → Vue d'ensemble → ⋮ → Modifier le tableau de bord → ⋮ → Éditeur YAML.
   **EN**: HA → Overview → ⋮ → Edit dashboard → ⋮ → YAML editor.
2. **FR** : Copier le contenu de `lovelace/spa-dashboard.yaml`.
   **EN**: Copy the contents of `lovelace/spa-dashboard.yaml`.
3. **FR** : Sauvegarder.
   **EN**: Save.

> **FR** : Certaines entités du dashboard correspondent au firmware v1.6+
> (à venir). Voir `lovelace/README.md` pour le statut détaillé.
>
> **EN**: Some dashboard entities correspond to firmware v1.6+ (upcoming).
> See `lovelace/README.md` for the detailed status.

---

## 6. Vérification / Verification

### 6.1 FR — Tester la lecture / EN — Test reading

**FR** : Vérifier que `sensor.balboa_spa_control_01_spa_eau_temp` affiche
une température cohérente (~30-40 °C selon le mode).

**EN**: Check that `sensor.balboa_spa_control_01_spa_eau_temp` shows a
sensible temperature (~30-40 °C depending on mode).

### 6.2 FR — Tester un bouton / EN — Test a button

**FR** : Appuyer sur `button.balboa_spa_control_03a_spa_btn_lumiere`. La
lumière du spa doit s'allumer/s'éteindre.

**EN**: Press `button.balboa_spa_control_03a_spa_btn_lumiere`. The spa
light should toggle.

### 6.3 FR — Tester le mode / EN — Test the mode

**FR** : Appuyer sur `button.balboa_spa_control_03e_spa_btn_mode`. Le mode
doit cycler ST → ECO → SL → ST.

**EN**: Press `button.balboa_spa_control_03e_spa_btn_mode`. The mode should
cycle ST → ECO → SL → ST.

---

## 7. Dépannage / Troubleshooting

### FR — Pas de trame RS-485 / EN — No RS-485 frames

- **FR** : Vérifier le câblage TTL485 (TXD du module → D2 ESP, pas l'inverse).
  Vérifier que J18 fournit bien des trames (oscilloscope ou TTL485 → PC).
- **EN**: Check TTL485 wiring (module TXD → ESP D2, not the reverse). Check
  J18 actually outputs frames (scope or TTL485 → PC).

### FR — Bouton Light s'active au boot / EN — Light button triggers at boot

- **FR** : Vous utilisez GPIO16. Migrer vers GPIO15 (D8) — cf. FIX-1 v1.5.3.
- **EN**: You are using GPIO16. Migrate to GPIO15 (D8) — see FIX-1 v1.5.3.

### FR — Boutons ne déclenchent rien / EN — Buttons trigger nothing

- **FR** : Vérifier l'alimentation 5 V du module optocoupleur (côté IN).
  Vérifier les cavaliers rouges retirés. Vérifier le pinout RJ45.
- **EN**: Check the 5 V supply on the optocoupler module (IN side). Check
  red jumpers removed. Check RJ45 pinout.

### FR — ESP redémarre / EN — ESP reboots

- **FR** : Vérifier que vous êtes sur le firmware v1.5.3 (FIX-2 supprime
  la fragmentation heap qui causait des WDT toutes les 20-155 min).
- **EN**: Check you are on firmware v1.5.3 (FIX-2 removes heap
  fragmentation causing WDT every 20-155 min).

### FR — Mode SL confondu avec ECO / EN — SL mode confused with ECO

- **FR** : Le firmware utilise `b18 == 0x08` pour SL (et non `b23`), ce qui
  évite le piège du `b23=0x00` en SL stabilisé.
- **EN**: The firmware uses `b18 == 0x08` for SL (not `b23`), avoiding the
  `b23=0x00` issue in stabilized SL.

---

## FR — Pour aller plus loin / EN — Going further

- `HARDWARE.md` — architecture matérielle complète / full hardware architecture
- `BUS_J1_PROTOCOL.md` — protocole bus J1 / J1 bus protocol
- `PROTOCOL.md` — protocole RS-485 / RS-485 protocol
- `APPROACHES_TESTED.md` — historique des pistes / approaches history
