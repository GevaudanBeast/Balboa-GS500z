# Balboa GS500Z Home Assistant Integration

[![Validate](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Validate/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Hassfest](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Hassfest/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Release](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Release/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Intégration Home Assistant pour **superviser** un spa Balboa GS500Z via un module RS-485 WiFi EW11A.

> ⚠️ **Mode lecture seule** : Cette intégration permet de **lire** l'état du spa (température, mode, chauffage) mais **ne peut pas le contrôler** via RS-485. Le VL403 utilise un protocole propriétaire. Pour le contrôle, voir la [solution IR avec ESP32](#-contrôle-du-spa-solution-ir).

## 🎯 Fonctionnalités

### Supervision RS-485 (lecture seule)

- **Climate Entity** : Affichage de l'état du spa
  - 🌡️ Température de l'eau en temps réel
  - 🎯 Température de consigne actuelle
  - 🔄 Mode de fonctionnement : Standard (ST), Économique (ECO), Sommeil (SL)

- **Binary Sensor** : État du chauffage (actif/inactif)

- **Fonctionnalités avancées** :
  - Fenêtre glissante pour validation des données (évite les lectures erronées)
  - Auto-reconnexion TCP en cas de déconnexion
  - Configuration modifiable après installation
  - Analyse complète des 16 841 trames réelles validée ✅

### Contrôle du spa (solution à implémenter)

Pour contrôler le spa depuis Home Assistant :
- 🎯 **Solution recommandée** : Module IR + ESP32 avec ESPHome (voir [IR_CONTROL.md](IR_CONTROL.md))
- ⌨️ **Alternative** : Utilisation du clavier physique VL403

## 📋 Prérequis

- Home Assistant 2023.1 ou supérieur
- Module RS-485 WiFi EW11A configuré en mode TCP
- Spa Balboa GS500Z avec carte de contrôle et clavier VL403

## 🔧 Installation

### Méthode 1 : HACS (Recommandé)

1. Ouvrez HACS dans Home Assistant
2. Allez dans "Intégrations"
3. Cliquez sur le menu (⋮) → "Dépôts personnalisés"
4. Ajoutez ce dépôt : `https://github.com/GevaudanBeast/Balboa-GS500z`
5. Recherchez "Balboa GS500Z" et installez
6. Redémarrez Home Assistant

### Méthode 2 : Installation manuelle

1. Copiez le dossier `custom_components/balboa_gs500z` dans le dossier `custom_components` de votre installation Home Assistant
2. Redémarrez Home Assistant

## ⚙️ Configuration

### Configuration initiale

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez **Balboa GS500Z Spa**
4. Entrez les informations de connexion :
   - **Host** : Adresse IP de votre EW11A
   - **Port** : Port TCP (par défaut : 8899)
5. Cliquez sur **Soumettre**

L'intégration va tester la connexion et créer automatiquement les entités.

### Options de configuration

Après installation, vous pouvez configurer les options en cliquant sur **Configurer** :

- **Taille de la fenêtre glissante** (3-20) : Nombre de trames à conserver pour validation (défaut : 5)
- **Garde-fou d'ordre des modes** : Active/désactive la validation de l'ordre des transitions de mode (défaut : activé)

## 🎮 Utilisation

### Entités créées

- `climate.spa` : Contrôle du spa
- `binary_sensor.spa_heater` : État du chauffage

### Exemples d'automatisations (lecture seule)

#### Notification quand le chauffage s'allume

```yaml
automation:
  - alias: "Spa - Notification chauffage"
    trigger:
      - platform: state
        entity_id: binary_sensor.spa_heater
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Le chauffage du spa est actif 🔥"
```

#### Alerte si la température descend trop bas

```yaml
automation:
  - alias: "Spa - Alerte température basse"
    trigger:
      - platform: numeric_state
        entity_id: climate.spa
        value_template: "{{ state.attributes.current_temperature }}"
        below: 30
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Spa froid"
          message: "Température : {{ states.climate.spa.attributes.current_temperature }}°C"
```

#### Notification quand le spa atteint la température cible

```yaml
automation:
  - alias: "Spa - Prêt à utiliser"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('climate.spa', 'current_temperature') >=
             state_attr('climate.spa', 'temperature') }}
    condition:
      - condition: state
        entity_id: binary_sensor.spa_heater
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🌡️ Spa prêt !"
          message: "Le spa a atteint {{ states.climate.spa.attributes.temperature }}°C"
```

#### Suivi de l'utilisation du chauffage

```yaml
# Créer un helper "Temps d'utilisation du chauffage"
# Configuration → Appareils et services → Assistants → Créer un assistant
# Type : Historique

automation:
  - alias: "Spa - Statistiques chauffage"
    trigger:
      - platform: state
        entity_id: binary_sensor.spa_heater
        to: "off"
        for: "00:10:00"
    action:
      - service: notify.mobile_app
        data:
          message: "Chauffage éteint depuis 10 minutes. Mode : {{ state_attr('climate.spa', 'preset_mode') }}"
```

### Carte Lovelace pour supervision

```yaml
type: vertical-stack
cards:
  # État du spa
  - type: thermostat
    entity: climate.spa
    name: "Spa Balboa GS500Z"

  # Détails
  - type: entities
    title: "Détails"
    entities:
      - entity: climate.spa
        type: attribute
        attribute: current_temperature
        name: "Température actuelle"
      - entity: climate.spa
        type: attribute
        attribute: temperature
        name: "Consigne"
      - entity: climate.spa
        type: attribute
        attribute: preset_mode
        name: "Mode"
      - entity: binary_sensor.spa_heater
        name: "Chauffage"

  # Graphique historique
  - type: history-graph
    title: "Historique 24h"
    entities:
      - entity: climate.spa
        name: "Température"
      - entity: binary_sensor.spa_heater
        name: "Chauffage"
```

## 🔌 Configuration EW11A

Le module EW11A doit être configuré en mode TCP Server :

- **Mode** : TCP Server
- **Baud Rate** : 9600
- **Data Bits** : 8
- **Stop Bits** : 1
- **Parity** : None
- **Port** : 8899 (ou autre port de votre choix)

## 🎯 Contrôle du spa : Solution IR

### Pourquoi le contrôle RS-485 ne fonctionne pas ?

Après des tests approfondis, il a été confirmé que :
- ❌ Le clavier VL403 utilise un **protocole propriétaire** (non RS-485 standard)
- ❌ Brancher l'EW11A sur les connecteurs clavier provoque des dysfonctionnements (ex: pompe forcée)
- ✅ Le bus RS-485 est en **lecture seule** (monitoring/broadcast uniquement)

### Solution : Module IR + ESP32

Pour contrôler le spa depuis Home Assistant, utilisez :

| Composant | Rôle |
|-----------|------|
| **Module IR Balboa** | Récepteur infrarouge officiel (se branche sur GS500Z) |
| **ESP32 + ESPHome** | Émetteur IR pilotable depuis Home Assistant |

**Architecture complète** :

```
Home Assistant
     │
     ├──► Balboa GS500Z (cette intégration)
     │    └─► Lecture via RS-485 (EW11A)
     │
     └──► ESP32 ESPHome
          └─► Contrôle via IR → Module IR Balboa
```

### Guide complet : IR_CONTROL.md

📁 Voir **[IR_CONTROL.md](IR_CONTROL.md)** pour le guide complet :
- Matériel nécessaire (ESP32, LED IR, récepteur IR)
- Reverse engineering du protocole IR
- Configuration ESPHome complète
- Scripts Home Assistant pour contrôle transparent
- Exemples d'automatisations avec contrôle

**Avantages de cette solution** :
- ✅ Lecture temps réel (RS-485 via cette intégration)
- ✅ Écriture fonctionnelle (IR via ESP32)
- ✅ Aucune modification du spa
- ✅ Intégration native ESPHome
- ✅ Sécurisé (pas de risque électronique)

## 📡 Protocole RS-485

### Structure des trames

Les trames sont au format : `[643F2B...]` (27 octets = 54 caractères hex)

- **Header** : `64 3F 2B`
- **Byte 3** : Température eau (× 0.5°C)
- **Byte 5** : Température consigne (× 0.5°C)
- **Byte 19 bit 0** : État chauffage (1 = actif)
- **Byte 23** : Mode
  - `0x20` : ST (Standard)
  - `0x00` : ECO (Économique)
  - `0x40` : SL (Sommeil)
  - `0x60` : Transitoire (ignoré)

### Fenêtre glissante

L'intégration utilise une fenêtre glissante pour valider les données :
- Conserve les N dernières trames (défaut : 5)
- Nécessite 3 confirmations consécutives pour valider une valeur
- Tolérance pour les modes transitoires (0x60)

### Garde-fou d'ordre

Si activé, l'intégration respecte l'ordre de transition des modes du VL403 :
- ST → ECO
- ECO → SL (ou ECO → ST)
- SL → ST

Les transitions invalides sont bloquées pour éviter les erreurs.

## 🐛 Dépannage

### L'intégration ne se connecte pas

- Vérifiez que l'EW11A est accessible sur le réseau
- Testez la connexion : `telnet <IP_EW11A> 8899`
- Vérifiez les logs Home Assistant : **Configuration** → **Logs**

### Les valeurs ne se mettent pas à jour

- Vérifiez que le spa envoie bien des trames (regardez les logs en mode debug)
- Augmentez la taille de la fenêtre glissante dans les options
- Vérifiez que l'EW11A est bien branché sur les connecteurs RS-485 (pas sur les connecteurs clavier)

### Le mode ECO change constamment

⚠️ **Comportement normal** : Quand le mode ECO est sélectionné sur le VL403, le GS500Z alterne automatiquement entre ST/ECO/SL pour optimiser la consommation. L'intégration affiche le **mode RS-485 instantané**.

Distribution typique en mode ECO :
- 91.5% du temps : `standard` (0x20)
- 6.5% du temps : `eco` (0x00)
- 2% du temps : `sleep` (0x40)

Ceci n'est **pas un bug** - c'est le fonctionnement réel du spa. Voir [PROTOCOL.md](PROTOCOL.md) pour plus de détails.

### Je veux contrôler le spa depuis Home Assistant

Cette intégration est en **mode lecture seule**. Pour le contrôle :
- 📖 Consultez [IR_CONTROL.md](IR_CONTROL.md) pour la solution complète
- 🎯 Utilisez un module IR Balboa + ESP32 avec ESPHome
- ⚠️ **Ne tentez PAS** d'écrire directement sur le bus RS-485

### Activer les logs debug

Ajoutez dans `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.balboa_gs500z: debug
```

## 🏗️ Architecture technique

```
custom_components/balboa_gs500z/
├── __init__.py           # Point d'entrée, setup de l'intégration
├── manifest.json         # Métadonnées de l'intégration
├── const.py             # Constantes
├── config_flow.py       # Configuration initiale
├── tcp_client.py        # Client TCP pour EW11A
├── coordinator.py       # Coordinateur de données avec fenêtre glissante
├── climate.py           # Entity climate (spa)
├── binary_sensor.py     # Entity binary_sensor (chauffage)
├── services.yaml        # Définition des services
├── strings.json         # Chaînes de traduction
└── translations/
    ├── en.json         # Traduction anglaise
    └── fr.json         # Traduction française
```

## 🔐 Sécurité

Cette intégration est conçue pour une utilisation sur un réseau local. Aucune donnée n'est envoyée à l'extérieur.

## 📝 Licence

Ce projet est sous licence MIT.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## 📧 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez les logs Home Assistant

## ⚠️ Avertissements

- Cette intégration est fournie "telle quelle" sans garantie
- Testez d'abord sur un environnement de développement
- **Mode lecture seule** : Cette intégration ne peut pas contrôler le spa (voir [IR_CONTROL.md](IR_CONTROL.md) pour le contrôle)
- Ne branchez **jamais** l'EW11A sur les connecteurs du clavier VL403 (risque de dysfonctionnement)
- Branchez l'EW11A uniquement sur les connecteurs RS-485 prévus à cet effet
- Faites une sauvegarde de votre configuration Home Assistant avant installation

## 🙏 Remerciements

- Balboa pour le protocole GS500Z
- La communauté Home Assistant
- Tous les contributeurs

## 📚 Ressources

- [Documentation Home Assistant](https://www.home-assistant.io/)
- [HACS](https://hacs.xyz/)
- [Protocole RS-485](https://fr.wikipedia.org/wiki/EIA-485)

---

Made with ❤️ for the Home Assistant community
