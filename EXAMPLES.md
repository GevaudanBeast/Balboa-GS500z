# Exemples d'utilisation de l'intégration Balboa GS500Z

Ce document contient des exemples pratiques d'utilisation de l'intégration.

## 📊 Carte Lovelace

### Carte thermostat simple

```yaml
type: thermostat
entity: climate.spa
```

### Carte détaillée avec informations

```yaml
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.spa
    name: Spa

  - type: entities
    title: Informations Spa
    entities:
      - entity: climate.spa
        name: Température actuelle
        type: attribute
        attribute: current_temperature
      - entity: climate.spa
        name: Température cible
        type: attribute
        attribute: temperature
      - entity: climate.spa
        name: Mode
        type: attribute
        attribute: preset_mode
      - entity: binary_sensor.spa_heater
        name: Chauffage
```

### Carte personnalisée avec boutons

```yaml
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.spa
    name: Spa

  - type: horizontal-stack
    cards:
      - type: button
        name: Standard
        icon: mdi:sun-thermometer
        tap_action:
          action: call-service
          service: climate.set_preset_mode
          service_data:
            entity_id: climate.spa
            preset_mode: standard

      - type: button
        name: Eco
        icon: mdi:leaf
        tap_action:
          action: call-service
          service: climate.set_preset_mode
          service_data:
            entity_id: climate.spa
            preset_mode: eco

      - type: button
        name: Sleep
        icon: mdi:sleep
        tap_action:
          action: call-service
          service: climate.set_preset_mode
          service_data:
            entity_id: climate.spa
            preset_mode: sleep
```

## 🤖 Automatisations

### 1. Préchauffage quotidien

Chauffe le spa à 38°C tous les jours à 17h.

```yaml
automation:
  - alias: "Spa - Préchauffage quotidien"
    description: "Chauffe le spa à 38°C à 17h"
    trigger:
      - platform: time
        at: "17:00:00"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 38
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: standard
```

### 2. Mode économique la nuit

Passe en mode ECO à 23h et revient en ST le matin.

```yaml
automation:
  - alias: "Spa - Mode ECO nuit"
    description: "Passe en mode ECO à 23h"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: eco

  - alias: "Spa - Mode ST matin"
    description: "Passe en mode Standard à 7h"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: standard
```

### 3. Mode sommeil si absent

Passe en mode SL quand personne n'est à la maison.

```yaml
automation:
  - alias: "Spa - Mode Sleep si absent"
    description: "Mode sommeil quand personne à la maison"
    trigger:
      - platform: state
        entity_id: zone.home
        to: "0"
    condition:
      - condition: state
        entity_id: climate.spa
        attribute: preset_mode
        state: standard
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: sleep

  - alias: "Spa - Mode Standard si présent"
    description: "Mode standard quand quelqu'un rentre"
    trigger:
      - platform: state
        entity_id: zone.home
        from: "0"
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: standard
```

### 4. Notification quand la température est atteinte

Envoie une notification quand le spa atteint la température cible.

```yaml
automation:
  - alias: "Spa - Notification température atteinte"
    description: "Notifie quand la température cible est atteinte"
    trigger:
      - platform: template
        value_template: >
          {{ states('climate.spa') | float >=
             state_attr('climate.spa', 'temperature') | float }}
    condition:
      - condition: state
        entity_id: binary_sensor.spa_heater
        state: "on"
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          title: "🌡️ Spa prêt"
          message: "Le spa a atteint {{ state_attr('climate.spa', 'temperature') }}°C"
```

### 5. Alerte chauffage toujours actif

Alerte si le chauffage reste actif trop longtemps (possible problème).

```yaml
automation:
  - alias: "Spa - Alerte chauffage prolongé"
    description: "Alerte si chauffage actif > 4h"
    trigger:
      - platform: state
        entity_id: binary_sensor.spa_heater
        to: "on"
        for:
          hours: 4
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Spa - Alerte"
          message: "Le chauffage du spa est actif depuis plus de 4 heures"
          data:
            priority: high
```

### 6. Planification hebdomadaire

Différentes températures selon les jours de la semaine.

```yaml
automation:
  - alias: "Spa - Température week-end"
    description: "38°C le week-end"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: time
        weekday:
          - sat
          - sun
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 38

  - alias: "Spa - Température semaine"
    description: "35°C en semaine"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 35
```

### 7. Contrôle vocal

Créez des scripts pour contrôler le spa à la voix.

```yaml
script:
  spa_chauffer:
    alias: "Chauffer le spa"
    sequence:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 38
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: standard
      - service: tts.google_translate_say
        data:
          entity_id: media_player.salon
          message: "Le spa va chauffer à 38 degrés"

  spa_eco:
    alias: "Spa mode économique"
    sequence:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: eco
      - service: tts.google_translate_say
        data:
          entity_id: media_player.salon
          message: "Le spa passe en mode économique"
```

Puis configurez Alexa/Google Home pour appeler ces scripts :
- "Alexa, lance le script chauffer le spa"
- "Ok Google, active spa mode économique"

## 📈 Capteurs utiles

### Capteur de durée de chauffage

```yaml
sensor:
  - platform: history_stats
    name: Spa - Chauffage aujourd'hui
    entity_id: binary_sensor.spa_heater
    state: "on"
    type: time
    start: "{{ now().replace(hour=0, minute=0, second=0) }}"
    end: "{{ now() }}"
```

### Capteur de coût énergétique

Suppose 3kW de puissance de chauffage et 0.15€/kWh.

```yaml
sensor:
  - platform: template
    sensors:
      spa_heating_cost_today:
        friendly_name: "Coût chauffage spa aujourd'hui"
        unit_of_measurement: "€"
        value_template: >
          {{ (states('sensor.spa_chauffage_aujourd_hui') | float * 3 * 0.15) | round(2) }}
```

### Capteur de temps avant température cible

```yaml
sensor:
  - platform: template
    sensors:
      spa_time_to_target:
        friendly_name: "Temps avant température cible"
        unit_of_measurement: "min"
        value_template: >
          {% set current = state_attr('climate.spa', 'current_temperature') | float %}
          {% set target = state_attr('climate.spa', 'temperature') | float %}
          {% set diff = target - current %}
          {% if diff > 0 and is_state('binary_sensor.spa_heater', 'on') %}
            {{ (diff * 30) | round(0) }}
          {% else %}
            0
          {% endif %}
```

## 🎨 Graphiques

### Carte historique de température

```yaml
type: history-graph
entities:
  - entity: climate.spa
    name: Température actuelle
    attribute: current_temperature
  - entity: climate.spa
    name: Température cible
    attribute: temperature
  - entity: binary_sensor.spa_heater
    name: Chauffage
hours_to_show: 24
refresh_interval: 0
```

### Carte statistiques

```yaml
type: statistics-graph
entities:
  - sensor.spa_water_temperature
stat_types:
  - mean
  - min
  - max
period: day
```

## 🔔 Notifications avancées

### Notification avec actions

```yaml
automation:
  - alias: "Spa - Notification interactive"
    trigger:
      - platform: time
        at: "17:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "🛁 Spa"
          message: "Voulez-vous chauffer le spa ?"
          data:
            actions:
              - action: "spa_heat_38"
                title: "Chauffer à 38°C"
              - action: "spa_heat_40"
                title: "Chauffer à 40°C"
              - action: "spa_eco"
                title: "Mode ECO"

  - alias: "Spa - Action chauffer 38"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "spa_heat_38"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 38

  - alias: "Spa - Action chauffer 40"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "spa_heat_40"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 40

  - alias: "Spa - Action ECO"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "spa_eco"
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: eco
```

## 🏠 Intégration avec d'autres équipements

### Contrôle des lumières

Allume les lumières du jardin quand le spa chauffe le soir.

```yaml
automation:
  - alias: "Spa - Lumières jardin"
    trigger:
      - platform: state
        entity_id: binary_sensor.spa_heater
        to: "on"
    condition:
      - condition: sun
        after: sunset
    action:
      - service: light.turn_on
        target:
          entity_id: light.jardin
        data:
          brightness: 150
```

### Intégration avec la météo

Ajuste la température selon la météo.

```yaml
automation:
  - alias: "Spa - Température selon météo"
    trigger:
      - platform: time
        at: "16:00:00"
    action:
      - choose:
          - conditions:
              - condition: numeric_state
                entity_id: weather.home
                attribute: temperature
                below: 10
            sequence:
              - service: climate.set_temperature
                target:
                  entity_id: climate.spa
                data:
                  temperature: 40
          - conditions:
              - condition: numeric_state
                entity_id: weather.home
                attribute: temperature
                above: 20
            sequence:
              - service: climate.set_temperature
                target:
                  entity_id: climate.spa
                data:
                  temperature: 35
        default:
          - service: climate.set_temperature
            target:
              entity_id: climate.spa
            data:
              temperature: 38
```

## 🔧 Scripts utiles

### Script de maintenance

```yaml
script:
  spa_maintenance_mode:
    alias: "Mode maintenance spa"
    sequence:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 30
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: sleep
      - service: notify.mobile_app
        data:
          message: "Spa en mode maintenance (30°C, Sleep)"
```

### Script de vacances

```yaml
script:
  spa_vacation_mode:
    alias: "Mode vacances spa"
    sequence:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 20
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: sleep
      - service: notify.mobile_app
        data:
          message: "Spa en mode vacances (20°C, Sleep)"
```

## 📱 Widgets mobiles

### Widget simple (iOS/Android)

Créez un widget qui affiche :
- Température actuelle
- Température cible
- État du chauffage
- Boutons rapides pour les modes

Configuration via l'app Home Assistant mobile.

---

N'hésitez pas à adapter ces exemples à vos besoins spécifiques !
