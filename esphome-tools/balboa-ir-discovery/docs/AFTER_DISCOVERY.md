# 🎉 Et après la découverte ?

**Félicitations ! Vous avez découvert des codes IR qui fonctionnent.**

Ce guide vous explique comment transformer ces découvertes en télécommande fonctionnelle dans Home Assistant.

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Méthode 1 - Automatique (recommandée)](#méthode-1---automatique-recommandée)
3. [Méthode 2 - Semi-automatique](#méthode-2---semi-automatique)
4. [Méthode 3 - Manuelle](#méthode-3---manuelle)
5. [Créer un dashboard Lovelace](#créer-un-dashboard-lovelace)
6. [Intégration avec l'intégration Balboa existante](#intégration-avec-lintégration-balboa-existante)
7. [FAQ](#faq)

---

## 🎯 Vue d'ensemble

Après la découverte, vous avez trois options :

| Méthode | Difficulté | Temps | Flexibilité |
|---------|-----------|-------|-------------|
| **Automatique** | ⭐ Facile | 10 min | ★★★ |
| **Semi-automatique** | ⭐⭐ Moyenne | 20 min | ★★★★ |
| **Manuelle** | ⭐⭐⭐ Avancée | 1h | ★★★★★ |

**Recommandation** : Commencez par la **méthode automatique** !

---

## 🤖 Méthode 1 - Automatique (recommandée)

### Principe

Un script Python lit automatiquement les codes depuis Home Assistant et génère la configuration ESPHome.

### Prérequis

- ✅ Codes découverts (disponibles dans HA)
- ✅ Python 3 installé
- ✅ Token Home Assistant

### Étapes

#### 1. Obtenir un token Home Assistant

1. Ouvrez **Home Assistant**
2. Profil (en bas à gauche) → **Tokens d'accès longue durée**
3. **Créer un token** → Nom : `Balboa IR Generator`
4. **Copier le token**  (important : il ne sera affiché qu'une fois !)

#### 2. Installer le module requests (si nécessaire)

```bash
pip install requests
```

#### 3. Générer la configuration automatiquement

```bash
cd esphome-tools/balboa-ir-discovery/automation/

python3 generate_remote_config.py \
  --ha-entity sensor.balboa_ir_discovery_codes_decouverts_json \
  --ha-url http://homeassistant.local:8123 \
  --ha-token VOTRE_TOKEN_ICI \
  --output ../balboa-ir-remote.yaml
```

**Sortie attendue** :

```
📥 Chargement des codes découverts...
✅ 6 code(s) chargé(s)
⚙️  Génération de la configuration ESPHome...
💾 Écriture dans ../balboa-ir-remote.yaml...
✅ Configuration générée avec succès !

📄 Fichier: balboa-ir-remote.yaml
📊 6 bouton(s) créé(s)
```

#### 4. Vérifier la configuration générée

Ouvrez `balboa-ir-remote.yaml` :

```yaml
button:
  # Code 0x00000042
  - platform: template
    name: "Code 0x00000042"
    icon: "mdi:remote"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x42
```

#### 5. Personnaliser les noms (optionnel)

Créez `custom_names.json` :

```json
{
  "0x00000042": "Mode ECO",
  "0x00000043": "Mode Standard",
  "0x00000050": "Température +"
}
```

Re-générez avec les noms :

```bash
python3 generate_remote_config.py \
  --ha-entity sensor.balboa_ir_discovery_codes_decouverts_json \
  --ha-token VOTRE_TOKEN \
  --names custom_names.json \
  --output ../balboa-ir-remote.yaml
```

#### 6. Flasher un ESP32

```bash
cd ..
esphome run balboa-ir-remote.yaml
```

#### 7. Ajouter à Home Assistant

Home Assistant détecte automatiquement le nouvel appareil ESPHome !

**✅ Terminé ! Vos boutons sont maintenant disponibles dans HA.**

---

## 🔀 Méthode 2 - Semi-automatique

### Principe

Exporter manuellement les codes, puis utiliser le script de génération.

### Étapes

#### 1. Exporter les codes depuis Home Assistant

1. **Outils de développement** → **États**
2. Chercher `sensor.balboa_ir_discovery_codes_decouverts_json`
3. Copier le contenu de **"state"**
4. Coller dans un fichier `discovered_codes.json`

Exemple :

```json
[
  {"protocol":"NEC","code":"0x00000042","code_dec":66,"timestamp":12345},
  {"protocol":"NEC","code":"0x00000050","code_dec":80,"timestamp":12347}
]
```

#### 2. Créer un fichier de noms personnalisés

Créez `custom_names.json` :

```json
{
  "0x00000042": "Mode ECO",
  "0x00000050": "Température +"
}
```

#### 3. Générer la configuration

```bash
cd automation/
python3 generate_remote_config.py \
  --json discovered_codes.json \
  --names custom_names.json \
  --output ../balboa-ir-remote.yaml
```

#### 4. Flasher et utiliser

Comme dans la méthode automatique (étapes 6-7).

---

## ✍️ Méthode 3 - Manuelle

### Principe

Écrire manuellement la configuration ESPHome.

### Template de base

Créez `balboa-ir-remote.yaml` :

```yaml
substitutions:
  device_name: "balboa-ir-remote"
  friendly_name: "Balboa IR Remote"

esphome:
  name: ${device_name}

esp32:
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

logger:

remote_transmitter:
  pin: GPIO4
  carrier_duty_percent: 50%

button:
  # Mode ECO
  - platform: template
    name: "Mode ECO"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x42

  # Température +
  - platform: template
    name: "Température +"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x50
```

### Ajouter vos codes découverts

Pour chaque code découvert, ajoutez un bouton :

**Pour NEC** :
```yaml
  - platform: template
    name: "Nom du bouton"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0xAAAA  # 16 bits supérieurs du code
          command: 0xCC    # 8 bits inférieurs du code
```

**Calcul de l'adresse et commande** :

Code: `0x00000042`
- Adresse: `0x0000` (bits 16-31)
- Commande: `0x42` (bits 0-7)

Code: `0x12340056`
- Adresse: `0x1234` (bits 16-31)
- Commande: `0x56` (bits 0-7)

---

## 🎨 Créer un dashboard Lovelace

### Dashboard de base

```yaml
type: vertical-stack
cards:
  # En-tête
  - type: markdown
    content: |
      ## 🏊 Contrôle Spa Balboa
      Télécommande IR

  # Contrôles de mode
  - type: entities
    title: Modes de fonctionnement
    entities:
      - entity: button.balboa_ir_remote_mode_eco
        name: Mode ECO
      - entity: button.balboa_ir_remote_mode_standard
        name: Mode Standard
      - entity: button.balboa_ir_remote_mode_sleep
        name: Mode Sleep

  # Contrôle température
  - type: horizontal-stack
    cards:
      - type: button
        entity: button.balboa_ir_remote_temperature
        name: Temp -
        icon: mdi:thermometer-minus
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.balboa_ir_remote_temperature_moins
      - type: button
        entity: button.balboa_ir_remote_temperature_plus
        name: Temp +
        icon: mdi:thermometer-plus
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.balboa_ir_remote_temperature_plus

  # Chauffage
  - type: button
    entity: button.balboa_ir_remote_chauffage
    name: Chauffage ON/OFF
    icon: mdi:radiator
```

### Dashboard avancé avec status

Si vous utilisez aussi l'intégration Balboa RS-485 :

```yaml
type: vertical-stack
cards:
  # État actuel du spa (depuis RS-485)
  - type: entities
    title: État du spa
    entities:
      - entity: climate.balboa_gs500z
        name: Température
      - entity: sensor.balboa_gs500z_mode
        name: Mode actuel
      - entity: binary_sensor.balboa_gs500z_heater
        name: Chauffage

  # Contrôles IR
  - type: entities
    title: Télécommande IR
    entities:
      - entity: button.balboa_ir_remote_mode_eco
      - entity: button.balboa_ir_remote_temperature_plus
```

Voir plus d'exemples dans **[../examples/lovelace_dashboards.yaml](../examples/lovelace_dashboards.yaml)**

---

## 🔗 Intégration avec l'intégration Balboa existante

Si vous utilisez déjà l'intégration Balboa (RS-485 via EW11A), vous pouvez combiner les deux :

### Architecture complète

```
┌────────────────────────────────────────────────────┐
│ Spa Balboa GS500Z                                  │
│                                                    │
│  ┌────────────┐          ┌────────────┐           │
│  │ Récepteur  │◄─────────│  ESP32     │           │
│  │ IR         │   IR     │  émetteur  │           │
│  └────────────┘          └────────────┘           │
│                                ▲                   │
│  ┌────────────┐                │                   │
│  │ Port       │                │                   │
│  │ RS-485     │◄───────────────┘                   │
│  └────────────┘         WiFi                       │
│       │                                            │
└───────┼────────────────────────────────────────────┘
        │
        │ RS-485
        ▼
   ┌────────────┐
   │  EW11A     │
   │  (WiFi)    │
   └────────────┘
        │
        │ TCP/IP
        ▼
   ┌────────────────────────────────┐
   │  Home Assistant                │
   │                                │
   │  ┌──────────────────────────┐  │
   │  │ Intégration Balboa       │  │
   │  │ (lecture RS-485)         │  │
   │  │ - État actuel            │  │
   │  │ - Température            │  │
   │  │ - Mode                   │  │
   │  └──────────────────────────┘  │
   │                                │
   │  ┌──────────────────────────┐  │
   │  │ ESPHome IR Remote        │  │
   │  │ (envoi commandes IR)     │  │
   │  │ - Boutons de contrôle    │  │
   │  └──────────────────────────┘  │
   └────────────────────────────────┘
```

### Automatisations combinées

Exemple : Notification quand le mode change suite à une commande IR

```yaml
automation:
  - alias: "Spa - Confirmation Mode ECO"
    trigger:
      - platform: state
        entity_id: button.balboa_ir_remote_mode_eco
    action:
      # Attendre que le spa réagisse
      - delay: 5

      # Vérifier l'état via RS-485
      - condition: state
        entity_id: sensor.balboa_gs500z_mode
        state: "ECO"

      # Notification
      - service: notify.mobile_app
        data:
          message: "Spa passé en mode ECO ✅"
```

---

## ❓ FAQ

### Q1 : Puis-je utiliser le même ESP32 pour découverte ET contrôle ?

**R** : Oui ! Deux options :

**Option A** : Flasher `balboa-ir-remote.yaml` par-dessus (vous perdez l'outil de découverte)

**Option B** : Garder `balboa-ir-discovery.yaml` et ajouter les boutons manuellement dedans

**Option C** : Utiliser deux ESP32 (un pour découverte, un pour contrôle)

### Q2 : Comment savoir quel bouton fait quoi ?

Référez-vous à votre documentation lors de la découverte :

1. Consultez les logs de découverte
2. Consultez `examples/discovered_codes_template.md` que vous avez rempli
3. Testez chaque bouton et notez l'effet

### Q3 : Certains codes ne fonctionnent plus

Possible que :
- Le spa nécessite un état spécifique
- Il y a des interférences IR
- Le code nécessite plusieurs appuis

**Solution** : Re-testez avec l'outil de découverte en mode manuel

### Q4 : Puis-je créer une entité Climate au lieu de boutons ?

**R** : Oui ! Mais c'est plus complexe. Vous devez :

1. Avoir des codes pour :
   - Température + et -
   - Modes (ECO, ST, SL)
   - Idéalement : lecture température actuelle (via RS-485)

2. Créer une entité `climate` dans ESPHome :

```yaml
climate:
  - platform: thermostat
    name: "Spa Balboa"
    sensor: sensor.balboa_temperature  # Via RS-485
    min_temperature: 26
    max_temperature: 40
    visual:
      min_temperature: 26
      max_temperature: 40
      temperature_step: 0.5
    heat_action:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x50  # Temp +
```

**Recommandation** : Commencez avec des boutons, puis améliorez progressivement.

### Q5 : Comment partager mes découvertes avec la communauté ?

1. Documentez vos codes dans `examples/discovered_codes_template.md`
2. Créez une issue sur GitHub avec vos résultats
3. Précisez le modèle exact de votre spa

---

## 🎓 Prochaines étapes

Maintenant que vous avez votre télécommande IR :

1. **Créez un dashboard Lovelace** - Voir exemples
2. **Automatisations** - Déclenchez des actions basées sur l'heure, météo, etc.
3. **Intégration vocale** - "Alexa, mets le spa en mode ECO"
4. **Notifications** - Alertes quand la température est atteinte

---

## 📚 Ressources

- **[automation/README.md](../automation/README.md)** - Guide du script automatique
- **[examples/lovelace_dashboards.yaml](../examples/lovelace_dashboards.yaml)** - Exemples de dashboards
- **[USAGE.md](USAGE.md)** - Guide d'utilisation de la découverte

---

**Félicitations ! Vous avez maintenant un contrôle IR complet de votre spa ! 🎉**

*N'oubliez pas de partager vos codes découverts avec la communauté !*
