# 🎯 Contrôle IR du spa Balboa GS500Z

Ce document décrit le projet de contrôle du spa via infrarouge (IR) en utilisant un ESP32/ESP8266 et ESPHome.

## 📋 Table des matières

- [Contexte](#contexte)
- [Architecture complète](#architecture-complète)
- [Matériel nécessaire](#matériel-nécessaire)
- [Étapes du projet](#étapes-du-projet)
- [Phase 1 : Reverse Engineering IR](#phase-1--reverse-engineering-ir)
- [Phase 2 : Configuration ESP32](#phase-2--configuration-esp32)
- [Phase 3 : Intégration Home Assistant](#phase-3--intégration-home-assistant)
- [Exemples de configuration](#exemples-de-configuration)
- [Dépannage](#dépannage)

---

## 🎯 Contexte

### Pourquoi le contrôle IR ?

L'intégration `balboa_gs500z` permet de **lire** l'état du spa via RS-485 (EW11A), mais **ne peut pas écrire** de commandes :

- ❌ Le VL403 utilise un protocole propriétaire (non RS-485)
- ❌ Brancher l'EW11A sur le clavier cause des dysfonctionnements
- ✅ Le module IR officiel Balboa est prévu pour le contrôle

### Solution : Module IR + ESP32

Le module IR Balboa permet de contrôler le spa sans fil. En combinant :
- **Module IR Balboa** (récepteur sur le spa)
- **ESP32 + émetteur IR** (pilotable via ESPHome)
- **ESPHome** (intégration native avec Home Assistant)

On obtient un **contrôle complet** du spa depuis Home Assistant !

---

## 🏗️ Architecture complète

```
┌─────────────────────────────────────────────────────────┐
│              Home Assistant                              │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
             │ État (lecture)           │ Commandes (écriture)
             ▼                          ▼
    ┌──────────────┐           ┌──────────────┐
    │   EW11A      │           │   ESP32      │
    │  RS-485/TCP  │           │  ESPHome     │
    └──────┬───────┘           └──────┬───────┘
           │                          │
           │ RS-485                   │ IR (38kHz)
           ▼                          ▼
    ┌──────────────┐           ┌──────────────┐
    │   GS500Z     │◄──────────┤   Module IR  │
    │   (Carte)    │           │   Balboa     │
    └──────────────┘           └──────────────┘
           ▲
           │ Propriétaire
           │
    ┌──────────────┐
    │   VL403      │
    │  (Clavier)   │
    └──────────────┘
```

### Flux de données

1. **Lecture** : GS500Z → RS-485 → EW11A → HA → `climate.spa`
2. **Écriture** : HA → ESP32 → IR → Module IR → GS500Z

---

## 🛠️ Matériel nécessaire

### Module IR Balboa

- **Module infrarouge officiel Balboa** pour GS500Z
- Compatible avec la carte GS500Z
- Se branche sur un connecteur dédié de la carte

> **Note** : Ce module est nécessaire car le GS500Z n'a pas de récepteur IR intégré

### ESP32 ou ESP8266

| Composant | Recommandation | Prix indicatif |
|-----------|----------------|----------------|
| ESP32 DevKit | Préféré (plus puissant, WiFi stable) | 5-10€ |
| ESP8266 NodeMCU | Alternative économique | 3-5€ |

### Émetteur/Récepteur IR

| Composant | Usage | Référence |
|-----------|-------|-----------|
| Émetteur IR | Envoyer des commandes au spa | LED IR 940nm (ex: TSAL6200) |
| Récepteur IR | Capturer les codes de la télécommande | TSOP38238, VS1838B |
| Transistor | Amplifier le signal IR | 2N2222, PN2222A, BC547 |
| Résistances | Circuit IR | 220Ω (émetteur), 10kΩ (pull-up) |

### Schéma de câblage

```
ESP32 / ESP8266
┌─────────────────┐
│                 │
│  GPIO4  ────────┼──► [220Ω] ──► LED IR (TSAL6200)
│  (TX IR)        │                    │
│                 │                    └──► GND
│                 │
│  GPIO5  ────────┼──► Récepteur IR (VS1838B)
│  (RX IR)        │    [Vcc, GND, Signal]
│                 │
│  3V3    ────────┼──► Alimentation composants
│  GND    ────────┼──► Masse commune
│                 │
└─────────────────┘
```

---

## 📐 Étapes du projet

Le projet se déroule en 3 phases :

1. **Reverse Engineering IR** : Découvrir le protocole IR
2. **Configuration ESP32** : Programmer l'ESP avec ESPHome
3. **Intégration Home Assistant** : Créer les services et automations

---

## 🔍 Phase 1 : Reverse Engineering IR

### Objectif

Identifier les codes IR pour chaque commande du spa.

### Option A : Avec télécommande existante (idéal)

Si vous avez une télécommande IR Balboa :

1. **Capturer les codes IR**

   Configuration ESPHome pour le récepteur :

   ```yaml
   # esphome-ir-receiver.yaml
   esphome:
     name: spa-ir-receiver
     platform: ESP32
     board: nodemcu-32s

   wifi:
     ssid: "VotreSSID"
     password: "VotreMotDePasse"

   logger:
     level: DEBUG

   api:
     encryption:
       key: "votre_clé_api"

   ota:
     password: "votre_mdp_ota"

   remote_receiver:
     pin: GPIO5
     dump: all  # Affiche tous les codes IR reçus
     tolerance: 50%
   ```

2. **Appuyer sur chaque bouton** de la télécommande et noter les codes dans les logs ESPHome :

   ```
   [remote.raw] Received Raw: 9000, -4500, 560, -560, 560, -1690, ...
   [remote.nec] Received NEC: address=0x00FF, command=0x12
   ```

3. **Documenter les codes** :

   | Bouton | Protocole | Adresse | Commande | Code brut |
   |--------|-----------|---------|----------|-----------|
   | Temp + | NEC | 0x00FF | 0x12 | ... |
   | Temp - | NEC | 0x00FF | 0x13 | ... |
   | Mode | NEC | 0x00FF | 0x14 | ... |
   | Lumière | NEC | 0x00FF | 0x15 | ... |

### Option B : Sans télécommande (bruteforce)

Si vous n'avez pas la télécommande, il faut tester les codes IR possibles.

#### Protocoles IR courants

Les spas utilisent généralement :
- **NEC** (le plus courant)
- **RC5**
- **RC6**
- **Samsung**

#### Script de bruteforce

Configuration ESPHome pour tester automatiquement :

```yaml
# esphome-ir-bruteforce.yaml
esphome:
  name: spa-ir-bruteforce
  platform: ESP32
  board: nodemcu-32s

wifi:
  ssid: "VotreSSID"
  password: "VotreMotDePasse"

logger:
  level: INFO

api:
  encryption:
    key: "votre_clé_api"

ota:
  password: "votre_mdp_ota"

remote_transmitter:
  pin: GPIO4
  carrier_duty_percent: 50%

# Services pour tester les codes
api:
  services:
    # Test protocole NEC
    - service: test_nec_code
      variables:
        address: int
        command: int
      then:
        - remote_transmitter.transmit_nec:
            address: !lambda 'return address;'
            command: !lambda 'return command;'

    # Test protocole RC5
    - service: test_rc5_code
      variables:
        address: int
        command: int
      then:
        - remote_transmitter.transmit_rc5:
            address: !lambda 'return address;'
            command: !lambda 'return command;'
```

#### Script Python pour Home Assistant

Créer une automation HA pour tester systématiquement :

```python
# scripts/bruteforce_ir.py
import time

# Protocole NEC : adresses et commandes courantes
addresses = [0x00, 0x01, 0xFF, 0x00FF, 0xFFFF]
commands = range(0x00, 0xFF)

for addr in addresses:
    for cmd in commands:
        print(f"Testing NEC: address={hex(addr)}, command={hex(cmd)}")

        # Appeler le service ESPHome
        hass.services.call(
            'esphome',
            'spa_ir_bruteforce_test_nec_code',
            {'address': addr, 'command': cmd}
        )

        # Attendre 2 secondes et observer le spa
        time.sleep(2)

        # Demander à l'utilisateur si ça a fonctionné
        input("Le spa a-t-il réagi ? (Enter = non, 'y' = oui)")
```

#### Méthodologie

1. Lancer le script de bruteforce
2. Observer le spa après chaque code envoyé
3. Noter les codes qui provoquent une réaction
4. Affiner les tests autour des codes fonctionnels

> **Attention** : Le bruteforce peut prendre plusieurs heures. Patience !

---

## 🔧 Phase 2 : Configuration ESP32

Une fois les codes IR identifiés, configurer l'ESP32 pour l'utilisation finale.

### Configuration ESPHome complète

```yaml
# spa-ir-controller.yaml
esphome:
  name: spa-ir-controller
  platform: ESP32
  board: nodemcu-32s

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # IP fixe recommandée
  manual_ip:
    static_ip: 192.168.1.150
    gateway: 192.168.1.1
    subnet: 255.255.255.0

logger:
  level: INFO

api:
  encryption:
    key: !secret api_key

ota:
  password: !secret ota_password

# Émetteur IR
remote_transmitter:
  pin: GPIO4
  carrier_duty_percent: 50%

# LED de statut (optionnel)
status_led:
  pin:
    number: GPIO2
    inverted: true

# Boutons physiques (optionnel)
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      mode: INPUT_PULLUP
      inverted: true
    name: "Spa IR Button"
    on_press:
      - button.press: temp_up

# Boutons virtuels pour Home Assistant
button:
  - platform: template
    name: "Spa Temperature Up"
    id: temp_up
    icon: "mdi:thermometer-plus"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x00FF
          command: 0x12  # Remplacer par votre code
      - logger.log: "Sent: Temperature UP"

  - platform: template
    name: "Spa Temperature Down"
    id: temp_down
    icon: "mdi:thermometer-minus"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x00FF
          command: 0x13
      - logger.log: "Sent: Temperature DOWN"

  - platform: template
    name: "Spa Mode Cycle"
    id: mode_cycle
    icon: "mdi:sync"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x00FF
          command: 0x14
      - logger.log: "Sent: Mode CYCLE"

  - platform: template
    name: "Spa Light Toggle"
    id: light_toggle
    icon: "mdi:lightbulb"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x00FF
          command: 0x15
      - logger.log: "Sent: Light TOGGLE"

  - platform: template
    name: "Spa Pump Toggle"
    id: pump_toggle
    icon: "mdi:pump"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x00FF
          command: 0x16
      - logger.log: "Sent: Pump TOGGLE"
```

### Fichier secrets.yaml

```yaml
# secrets.yaml
wifi_ssid: "VotreSSID"
wifi_password: "VotreMotDePasseWiFi"
api_key: "votre_clé_api_32_caractères"
ota_password: "votre_mdp_ota"
```

### Compiler et flasher

```bash
# Installer ESPHome
pip install esphome

# Compiler la configuration
esphome compile spa-ir-controller.yaml

# Flasher l'ESP32 (USB la première fois)
esphome upload spa-ir-controller.yaml

# Ensuite, mise à jour OTA possible
esphome upload spa-ir-controller.yaml --device 192.168.1.150
```

---

## 🏠 Phase 3 : Intégration Home Assistant

### Ajout de l'ESP32 dans HA

L'ESP32 devrait apparaître automatiquement dans **Configuration → Intégrations → ESPHome**.

Sinon, l'ajouter manuellement :
1. Configuration → Intégrations → Ajouter une intégration
2. Rechercher "ESPHome"
3. Entrer l'IP : `192.168.1.150`
4. Entrer la clé API (depuis `secrets.yaml`)

### Entités créées

```
button.spa_temperature_up
button.spa_temperature_down
button.spa_mode_cycle
button.spa_light_toggle
button.spa_pump_toggle
```

### Script Home Assistant : Changement de température

Pour reproduire le comportement `set_temperature` :

```yaml
# scripts.yaml
spa_set_temperature:
  alias: "Spa: Set Temperature"
  fields:
    target_temp:
      description: "Target temperature in °C"
      example: 38
  sequence:
    - variables:
        current_temp: "{{ state_attr('climate.spa', 'temperature') | int }}"
        diff: "{{ (target_temp | int) - (current_temp | int) }}"

    - choose:
        # Si température à augmenter
        - conditions:
            - condition: template
              value_template: "{{ diff > 0 }}"
          sequence:
            - repeat:
                count: "{{ diff }}"
                sequence:
                  - service: button.press
                    target:
                      entity_id: button.spa_temperature_up
                  - delay:
                      seconds: 1

        # Si température à diminuer
        - conditions:
            - condition: template
              value_template: "{{ diff < 0 }}"
          sequence:
            - repeat:
                count: "{{ diff | abs }}"
                sequence:
                  - service: button.press
                    target:
                      entity_id: button.spa_temperature_down
                  - delay:
                      seconds: 1
```

### Script : Changement de mode

```yaml
spa_set_mode:
  alias: "Spa: Set Mode"
  fields:
    target_mode:
      description: "Target mode: standard, eco, sleep"
      example: "eco"
  sequence:
    - variables:
        current_mode: "{{ state_attr('climate.spa', 'preset_mode') }}"
        mode_sequence: ["standard", "eco", "sleep"]
        current_idx: "{{ mode_sequence.index(current_mode) }}"
        target_idx: "{{ mode_sequence.index(target_mode) }}"
        presses: "{{ (target_idx - current_idx) % 3 }}"

    - repeat:
        count: "{{ presses }}"
        sequence:
          - service: button.press
            target:
              entity_id: button.spa_mode_cycle
          - delay:
              seconds: 2
```

### Carte Lovelace intégrée

```yaml
# configuration.yaml ou ui-lovelace.yaml
type: vertical-stack
cards:
  # État actuel (lecture RS-485)
  - type: thermostat
    entity: climate.spa
    name: "État du spa (RS-485)"

  # Contrôles IR
  - type: entities
    title: "Contrôle IR"
    entities:
      - entity: button.spa_temperature_up
        name: "Température +"
      - entity: button.spa_temperature_down
        name: "Température -"
      - entity: button.spa_mode_cycle
        name: "Changer mode"
      - entity: button.spa_light_toggle
        name: "Lumière"
      - entity: button.spa_pump_toggle
        name: "Pompe"

  # Raccourci température
  - type: entities
    title: "Température rapide"
    entities:
      - type: buttons
        entities:
          - entity: script.spa_set_temperature
            name: "36°C"
            tap_action:
              action: call-service
              service: script.spa_set_temperature
              data:
                target_temp: 36
          - entity: script.spa_set_temperature
            name: "38°C"
            tap_action:
              action: call-service
              service: script.spa_set_temperature
              data:
                target_temp: 38
          - entity: script.spa_set_temperature
            name: "40°C"
            tap_action:
              action: call-service
              service: script.spa_set_temperature
              data:
                target_temp: 40
```

---

## 🧪 Exemples d'automations

### Automation : Préchauffage du spa

```yaml
automation:
  - alias: "Spa: Preheat for evening"
    trigger:
      - platform: time
        at: "17:00:00"
    condition:
      - condition: time
        weekday:
          - fri
          - sat
    action:
      # Régler à 38°C
      - service: script.spa_set_temperature
        data:
          target_temp: 38

      # Passer en mode Standard (chauffe rapide)
      - service: script.spa_set_mode
        data:
          target_mode: "standard"

      # Notification
      - service: notify.mobile_app
        data:
          title: "Spa préchauffé"
          message: "Le spa chauffe pour 19h 🔥"
```

### Automation : Mode ECO la nuit

```yaml
automation:
  - alias: "Spa: ECO mode at night"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: script.spa_set_mode
        data:
          target_mode: "eco"
```

---

## 🔧 Dépannage

### L'ESP32 ne se connecte pas au WiFi

- Vérifier les identifiants WiFi dans `secrets.yaml`
- S'assurer que le réseau est en 2.4 GHz (ESP32 ne supporte pas 5 GHz)
- Consulter les logs série : `esphome logs spa-ir-controller.yaml`

### Les codes IR ne fonctionnent pas

1. **Vérifier la portée** :
   - LED IR doit pointer vers le module IR Balboa
   - Distance maximale : environ 5 mètres
   - Éviter les obstacles

2. **Vérifier le câblage** :
   - Résistance 220Ω en série avec la LED IR
   - LED IR dans le bon sens (+ vers résistance, - vers GND)
   - Transistor correctement branché si utilisé

3. **Vérifier les codes** :
   - Re-capturer les codes avec le récepteur IR
   - Tester manuellement dans ESPHome → Devices → spa-ir-controller → Boutons

4. **Augmenter la puissance IR** :
   - Utiliser un transistor pour amplifier le signal
   - Utiliser plusieurs LEDs IR en parallèle

### Le spa réagit mal aux commandes

- **Ajouter des délais** entre les commandes (2-3 secondes)
- **Répéter les codes** 2-3 fois pour assurer la réception :

  ```yaml
  button:
    - platform: template
      name: "Spa Temperature Up"
      on_press:
        - repeat:
            count: 3
            sequence:
              - remote_transmitter.transmit_nec:
                  address: 0x00FF
                  command: 0x12
              - delay: 100ms
  ```

---

## 📚 Ressources

### Documentation officielle

- [ESPHome Remote Transmitter](https://esphome.io/components/remote_transmitter.html)
- [ESPHome Remote Receiver](https://esphome.io/components/remote_receiver.html)
- [Home Assistant ESPHome Integration](https://www.home-assistant.io/integrations/esphome/)

### Protocoles IR

- [NEC Protocol](https://www.sbprojects.net/knowledge/ir/nec.php)
- [RC5 Protocol](https://www.sbprojects.net/knowledge/ir/rc5.php)
- [Analyse IR avec Logic Analyzer](https://sigrok.org/)

### Matériel recommandé

- LED IR : TSAL6200, VSLY5850
- Récepteur IR : TSOP38238, VS1838B
- Transistor : 2N2222, PN2222A, BC547

---

## 🤝 Contribuer

Si vous réussissez le reverse engineering du protocole IR :

1. Documenter les codes IR dans une issue GitHub
2. Partager votre configuration ESPHome
3. Proposer une pull request avec un fichier `IR_CODES.md`

Cela aidera toute la communauté des utilisateurs de Balboa GS500Z !

---

**Bon courage pour le projet IR ! 🎯**
