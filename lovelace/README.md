# Dashboard Lovelace — Balboa GS501Z + VL403

> **FR** Ce fichier documente le tableau de bord Lovelace cible et le statut
> d'implémentation de chaque entité requise.
>
> **EN** This file documents the target Lovelace dashboard and the
> implementation status of each required entity.

---

## FR — Installation / EN — Installation

**FR** : Ouvrir Home Assistant → Tableau de bord → Modifier → Editeur YAML,
puis coller le contenu de `spa-dashboard.yaml`.

**EN**: Open Home Assistant → Dashboard → Edit → YAML editor, then paste the
contents of `spa-dashboard.yaml`.

---

## FR — Structure du dashboard

Le dashboard est composé de deux sections :

1. **Grille 3×2** — contrôles principaux (thermostat, blower, lumière, pompe,
   mode, cycles filtration).
2. **Carte détails** — température de sortie réchauffeur, état heater,
   indicateur de saisie en cours.

## EN — Dashboard structure

The dashboard has two sections:

1. **3×2 Grid** — main controls (thermostat, blower, light, pump, mode,
   filtration cycles).
2. **Details card** — heater outlet temperature, heater status, pending input
   indicator.

---

## FR — Statut des entités requises

## EN — Required entities status

| Entité / Entity | Source | Statut / Status |
|---|---|---|
| `climate.spa_balboa` | Composant HA / HA component | ✅ Implémenté |
| `switch.spa_blower` | Template HA (wraps bouton ESPHome) | ❌ A créer |
| `switch.spa_lumiere` | Template HA (wraps bouton ESPHome) | ❌ A créer |
| `sensor.balboa_spa_control_02b_spa_pompe` | Firmware ESPHome v1.6+ | ❌ A ajouter au firmware |
| `sensor.spa_mode` | Firmware ESPHome (renommage) | ❌ Actuellement `text_sensor.balboa_spa_control_03_spa_mode` |
| `sensor.balboa_spa_control_06b_spa_cycles` | Firmware ESPHome v1.6+ | ❌ A ajouter au firmware |
| `button.balboa_spa_control_05a_spa_btn_mode` | Firmware ESPHome v1.6+ | ❌ Actuellement `03e_spa_btn_mode` |
| `button.balboa_spa_control_06a_spa_btn_cycles` | Firmware ESPHome v1.6+ | ❌ Actuellement `03f_spa_btn_cycles` |
| `script.spa_cycle_pompe` | Script HA | ❌ A créer |
| `sensor.balboa_spa_control_04d_spa_temperature_sortie_rechauffeur` | Firmware ESPHome v1.6+ | ❌ A ajouter au firmware |
| `binary_sensor.balboa_spa_control_07a_spa_status_heater` | Firmware ESPHome v1.6+ | ❌ Actuellement `04a_spa_chauffage` |
| `input_boolean.spa_temp_pending` | Helper HA | ❌ A créer dans HA |
| `binary_sensor.balboa_spa_control_08a_spa_mode_saisie_temp` | Firmware ESPHome v1.6+ | ❌ A ajouter au firmware |

---

## FR — Entités ESPHome disponibles (firmware v1.5.3)

Les entités ci-dessous sont **déjà disponibles** avec le firmware actuel.
Elles peuvent être utilisées dans un dashboard simplifié en attendant
la mise à jour vers v1.6+.

## EN — Available ESPHome entities (firmware v1.5.3)

The following entities are **already available** with the current firmware.
They can be used in a simplified dashboard while waiting for the v1.6+ update.

| Entité / Entity | Type | Description FR | EN description |
|---|---|---|---|
| `sensor.balboa_spa_control_01_spa_eau_temp` | Sensor | Température eau | Water temperature |
| `sensor.balboa_spa_control_02_spa_consigne` | Sensor | Consigne | Setpoint |
| `text_sensor.balboa_spa_control_03_spa_mode` | Text sensor | Mode ST/ECO/SL | Mode ST/ECO/SL |
| `binary_sensor.balboa_spa_control_04a_spa_chauffage` | Binary sensor | Chauffage actif | Heater active |
| `binary_sensor.balboa_spa_control_04b_spa_lumiere` | Binary sensor | Lumière | Light |
| `text_sensor.balboa_spa_control_05_spa_diag` | Text sensor | Code diagnostic | Diagnostic code |
| `button.balboa_spa_control_03a_spa_btn_lumiere` | Button | Bouton lumière | Light button |
| `button.balboa_spa_control_03b_spa_btn_pompe` | Button | Bouton pompe | Pump button |
| `button.balboa_spa_control_03c_spa_btn_blower` | Button | Bouton blower | Blower button |
| `button.balboa_spa_control_03d_spa_btn_temp` | Button | Bouton temp (+1 cran) | Temp button (+1 step) |
| `button.balboa_spa_control_03e_spa_btn_mode` | Button | Cycle mode ST→ECO→SL | Mode cycle ST→ECO→SL |
| `button.balboa_spa_control_03f_spa_btn_cycles` | Button | Cycles filtration | Filtration cycles |
| `text_sensor.balboa_spa_control_09_spa_trame_brute` | Text sensor | Trame RS-485 brute | Raw RS-485 frame |
| `sensor.balboa_spa_control_91_spa_wifi_signal` | Sensor | RSSI WiFi | WiFi RSSI |
| `sensor.balboa_spa_control_92_spa_uptime` | Sensor | Uptime ESP | ESP uptime |
| `text_sensor.balboa_spa_control_93_spa_ip` | Text sensor | IP courante | Current IP |
| `binary_sensor.balboa_spa_control_98_spa_en_ligne` | Binary sensor | ESP en ligne | ESP online |

---

## FR — Éléments HA à créer manuellement

## EN — HA elements to create manually

### `switch.spa_blower` et `switch.spa_lumiere`

**FR** : Template switches qui wrappent les boutons ESPHome. Nécessitent
de connaître l'état courant (via `binary_sensor.04b_spa_lumiere`) pour
pouvoir exposer un vrai ON/OFF.

**EN**: Template switches wrapping ESPHome buttons. Require knowledge of
current state (via `binary_sensor.04b_spa_lumiere`) to expose true ON/OFF.

### `input_boolean.spa_temp_pending`

**FR** : Helper HA à créer dans Paramètres → Assistants → Entrée booléenne.
Indique qu'un changement de consigne de température est en cours.

**EN**: HA helper to create in Settings → Helpers → Input Boolean.
Indicates that a temperature setpoint change is in progress.

### `script.spa_cycle_pompe`

**FR** : Script HA qui cycle la pompe (OFF → LOW → HIGH). A définir dans
`scripts.yaml` ou via l'éditeur de scripts HA.

**EN**: HA script that cycles the pump (OFF → LOW → HIGH). To be defined in
`scripts.yaml` or via the HA script editor.

---

## FR — Roadmap firmware v1.6+

## EN — Firmware v1.6+ roadmap

Les entités suivantes sont prévues dans le firmware v1.6+ :

The following entities are planned for firmware v1.6+:

- Renommage des boutons `03x` → `05a` (mode) / `06a` (cycles)
- Ajout sensor pompe `02b_spa_pompe` (état OFF/LOW/HIGH)
- Ajout sensor cycles `06b_spa_cycles`
- Ajout sensor température sortie réchauffeur `04d`
- Ajout binary_sensor heater `07a` (renumérotation de `04a`)
- Ajout binary_sensor mode saisie température `08a`

---

## Voir aussi / See also

- `../HARDWARE.md` — architecture matérielle / hardware architecture
- `../esphome-tools/balboa-spa-control/README.md` — firmware ESPHome
- `../README.md` — intégration Home Assistant / Home Assistant integration
