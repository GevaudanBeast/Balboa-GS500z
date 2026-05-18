# Balboa Spa Control — ESPHome firmware

Firmware ESPHome pour ESP8266 NodeMCU pilotant l'integration spa Balboa
GS501Z + panneau VL403 :

- **Lecture** RS-485 via module TTL485 (MAX485) cable sur J18
  (format ASCII HEX type EW11A : `[HEX54CHARS]`).
- **Ecriture** : simulation des 4 boutons du VL403 (Light / Pump / Blower /
  Temp) via 4 optocoupleurs TLP281-4 (ou equivalents) sur J1.
- Combinaisons VL403 exposees comme boutons HA :
  **Mode** (Temp + Light) et **Cycles filtration** (Temp + Pump).

## Versions

| Version | Date | Notes |
|---------|------|-------|
| **v1.5.3** | 2026-05-11 | FIX-1 : `opto_light` GPIO16 → GPIO15 (D0 envoyait un transitoire HIGH au boot → declenchement parasite du bouton Light). FIX-2 : `last_raw_frame` et `diag_code` passes de `std::string` a `char[]` statique (fragmentation heap → crash/WDT toutes les 20-155 min). |
| v1.5.2 | — | Optimisations RAM : logger INFO, buffers statiques, `web_server` retire, sensors update 10s, perte signal a 200s. |

La version courante (recommandee) est **v1.5.3**.

## Cablage

### TTL485 (RS-485 lecture, J18)

| Module TTL485 | ESP8266 NodeMCU |
|---|---|
| VCC | 3V3 |
| GND | GND |
| TXD | D2 (GPIO4) — **TXD du module**, pas RXD |
| D+ / A | J18 borne A |
| D- / B | J18 borne B |

### TLP281-4 (simulation boutons VL403, J1)

| Canal | ESP GPIO | Pin RJ45 VL403 | Couleur |
|---|---|---|---|
| IN1 → OUT1 = BLOWER | D5 (GPIO14) | pin 7 | Orange |
| IN2 → OUT2 = POMPE  | D6 (GPIO12) | pin 3 | Jaune |
| IN3 → OUT3 = TEMP   | D7 (GPIO13) | pin 8 | Gris |
| IN4 → OUT4 = LIGHT  | **D8 (GPIO15)** | pin 2 | Bleu |

> ⚠️ **GPIO16 (D0) interdit** pour les sorties optocoupleur : son domaine
> RTC genere un transitoire HIGH au boot qui declenche le bouton associe
> a chaque redemarrage (cf. FIX-1 v1.5.3). Utiliser GPIO15 (D8) qui
> demarre LOW grace au pull-down hardware NodeMCU.

Cote VL403 :

- HVCC module → pin 1 RJ45 (Marron, Commun +5 V VL403)
- HGND module → GND cote VL403 (ou laisser flottant si module anode-commun)
- **Retirer les cavaliers rouges d'isolation** entre cote LED et cote sortie.

Pour le pinout VL403 complet, voir `HARDWARE.md` §3 et `BUS_J1_PROTOCOL.md` §1.

## Installation

1. Copier `secrets.yaml.example` vers `secrets.yaml` et renseigner :
   - SSID + mot de passe WiFi principal
   - Mot de passe du fallback AP
   - Cle API (`openssl rand -base64 32`)
   - Mot de passe OTA
2. Flasher l'ESP avec ESPHome :
   ```bash
   esphome run balboa-spa-control-v1.5.3.yaml
   ```
3. Ajouter l'integration ESPHome dans Home Assistant — toutes les entites
   (capteurs et boutons) sont decouvertes automatiquement.

## Entites exposees

### Capteurs

| Entite | Description |
|---|---|
| `sensor.01_spa_eau_temp` | Temperature eau (°C entier, update 10 s) |
| `sensor.02_spa_consigne` | Consigne (°C entier, update 10 s) |
| `binary_sensor.04a_spa_chauffage` | Chauffage actif (b19 bit 0) |
| `binary_sensor.04b_spa_lumiere` | Lumiere allumee |
| `text_sensor.03_spa_mode` | Mode : `ST` / `ECO` / `SL` |
| `text_sensor.05_spa_diag` | Code diag : `OK` / `HH` / `OH` / `IC` / `COMM` |
| `text_sensor.09_spa_trame_brute` | Trame ASCII HEX brute (update 120 s) |
| `binary_sensor.98_spa_en_ligne` | Etat connexion API |
| `sensor.91_spa_wifi_signal` | RSSI WiFi |
| `sensor.92_spa_uptime` | Uptime ESP |
| `text_sensor.93_spa_ip` | IP courante |

### Boutons (simulation VL403)

| Entite | Action |
|---|---|
| `button.03a_spa_btn_lumiere` | Light ON/OFF |
| `button.03b_spa_btn_pompe` | Pump LOW/HIGH/OFF |
| `button.03c_spa_btn_blower` | Blower ON/OFF |
| `button.03d_spa_btn_temp` | Temp +/- (1 incrément) |
| `button.03e_spa_btn_mode` | Cycle Mode : ST → ECO → SL → ST |
| `button.03f_spa_btn_cycles` | Cycles filtration |
| `button.06_spa_dump_trame` | Dump trame courante dans les logs |
| `button.97_spa_redemarrer_esp` | Redemarrage ESP |

## Logique de decodage RS-485

Trame Balboa : header `64 3F 2B`, 27 octets, encadree par `[` et `]`.

| Octet (0-indexe) | Valeur |
|---|---|
| 3 | Temperature eau (× 0.5 °C) |
| 5 | Consigne (× 0.5 °C) |
| 6 | Compteur — **ignore** |
| 18 | Lumiere (bits 1-2) + diagnostics (bits 6-7) + SL (== 0x08) |
| 19 | Chauffage (bit 0), priming (bit 2) |
| 20 | Lumiere alternative (== 0x02) |
| 23 | Mode ST (bit 5) |

Detection mode :
- `SL`  si `b18 == 0x08`
- `ST`  si pas SL et `b23 & 0x20`
- `ECO` sinon

Diagnostics :
- `HH` si `b18 & 0x40` (surchauffe haute)
- `OH` si `b18 & 0x80` (overheat)
- `IC` si `b19 & 0x04` (priming / init)
- `COMM` si aucune trame depuis ~200 s

> Note : le composant HA Python (`custom_components/balboa_gs500z`) utilise
> une logique de detection de mode legerement differente (v5.8.4) basee sur
> `b23` avec memoire SL de 120 s pour gerer le cas ou `b23` retombe a
> `0x00` une fois SL stabilise. Le firmware ESPHome ici utilise `b18`
> comme signal SL principal, ce qui est plus simple et fiable cote bord.

## Optimisations RAM (v1.5.2 + v1.5.3)

- Logger `INFO` (pas de `DEBUG`) — reduit drastiquement les strings dynamiques.
- Buffers de parsing 100 % statiques (`char[512]` + `uint8_t[27]`).
- Globales `char[]` au lieu de `std::string` (FIX-2) — pas de fragmentation
  heap a 10-12 trames/seconde.
- `web_server` desactive (~15-20 KB RAM liberes).
- `update_interval` 10 s sur les sensors, 120 s sur la trame brute.

## Voir aussi

- `../../HARDWARE.md` — architecture materielle complete
- `../../BUS_J1_PROTOCOL.md` — pinout VL403 et plan de cablage J1
- `../../PROTOCOL.md` — protocole RS-485 J18 complet
- `../../README.md` — integration Home Assistant Python
