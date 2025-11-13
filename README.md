# Balboa GS500Z Home Assistant Integration

[![Validate](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Validate/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Hassfest](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Hassfest/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Release](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Release/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Intégration Home Assistant complète pour contrôler un spa Balboa GS500Z via un module RS-485 WiFi EW11A.

## 🎯 Fonctionnalités

- **Climate Entity** : Contrôle complet du spa
  - Température de l'eau en temps réel
  - Réglage de la température cible
  - Modes de fonctionnement : Standard (ST), Économique (ECO), Sommeil (SL)

- **Binary Sensor** : État du chauffage (actif/inactif)

- **Services** :
  - `balboa_gs500z.set_temperature` : Définir la température cible
  - `balboa_gs500z.set_mode` : Changer le mode de fonctionnement

- **Fonctionnalités avancées** :
  - Fenêtre glissante pour validation des données (évite les lectures erronées)
  - Garde-fou d'ordre des modes (respecte la séquence ST→ECO→SL→ST)
  - Auto-reconnexion TCP en cas de déconnexion
  - Configuration modifiable après installation

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

### Exemples d'automatisations

#### Régler la température à 38°C à 18h

```yaml
automation:
  - alias: "Spa - Chauffer à 18h"
    trigger:
      - platform: time
        at: "18:00:00"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.spa
        data:
          temperature: 38
```

#### Passer en mode ECO la nuit

```yaml
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
          message: "Le chauffage du spa est actif"
```

### Utilisation des services

#### Service set_temperature

```yaml
service: balboa_gs500z.set_temperature
data:
  temperature: 38
```

#### Service set_mode

```yaml
service: balboa_gs500z.set_mode
data:
  mode: "eco"  # Options: "standard", "eco", "sleep"
```

## 🔌 Configuration EW11A

Le module EW11A doit être configuré en mode TCP Server :

- **Mode** : TCP Server
- **Baud Rate** : 9600
- **Data Bits** : 8
- **Stop Bits** : 1
- **Parity** : None
- **Port** : 8899 (ou autre port de votre choix)

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
- Désactivez temporairement le garde-fou d'ordre

### Les commandes ne fonctionnent pas

⚠️ **Note importante** : L'implémentation actuelle des commandes d'écriture (setpoint et mode) est une base à affiner selon votre configuration spécifique. Le protocole exact pour envoyer des commandes au GS500Z peut nécessiter des ajustements basés sur vos tests.

Pour déboguer :
1. Activez les logs debug (voir ci-dessous)
2. Observez les trames dans les logs
3. Ajustez les méthodes `build_setpoint_command()` et `build_mode_command()` dans `tcp_client.py`

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
- Les commandes d'écriture nécessitent une validation sur votre installation
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
