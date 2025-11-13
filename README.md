# Balboa GS500Z Home Assistant Integration

[![Validate](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Validate/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Hassfest](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Hassfest/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Release](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Release/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Intégration Home Assistant pour **superviser** un spa Balboa GS500Z via un module RS-485 WiFi EW11A.

> 🚀 **Première installation ?** Suivez le [**Guide de démarrage rapide (5 minutes)**](QUICKSTART.md)

> ⚠️ **Mode lecture seule** : Cette intégration permet de **lire** l'état du spa (température, mode, chauffage) mais **ne peut pas le contrôler** via RS-485. Le VL403 utilise un protocole propriétaire. Pour le contrôle, voir la [solution IR avec ESP32](#-contrôle-du-spa-solution-ir).

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 🚀 Commencer en 5 minutes
- **[IR_CONTROL.md](IR_CONTROL.md)** - 🎯 Contrôler le spa avec ESP32
- **[PROTOCOL.md](PROTOCOL.md)** - 🔧 Détails techniques RS-485
- **[EXAMPLES.md](EXAMPLES.md)** - 💡 Exemples d'automatisations
- **[INSTALL.md](INSTALL.md)** - 📦 Guide d'installation détaillé

---

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

## 🔧 Installation rapide

### Via HACS (recommandé)

1. **HACS** → **Intégrations** → **⋮** → **Dépôts personnalisés**
2. Ajoutez : `https://github.com/GevaudanBeast/Balboa-GS500z`
3. Recherchez "Balboa GS500Z" → **Télécharger**
4. **Redémarrez** Home Assistant

### Configuration

1. **Paramètres** → **Appareils et services** → **+ Ajouter**
2. Recherchez "Balboa GS500Z"
3. Entrez l'adresse IP de votre EW11A et le port (8899)

✅ **C'est prêt !** Vos entités `climate.spa` et `binary_sensor.spa_heater` sont créées.

📖 **Guide détaillé** : [QUICKSTART.md](QUICKSTART.md) (branchement, configuration EW11A, etc.)

## 🎮 Utilisation

### Entités créées

- `climate.spa` - Température, mode, consigne
- `binary_sensor.spa_heater` - État du chauffage

### Exemple : Notification quand le spa est prêt

```yaml
automation:
  - alias: "Spa prêt"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('climate.spa', 'current_temperature') >=
             state_attr('climate.spa', 'temperature') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🔥 Spa prêt !"
          message: "Le spa a atteint {{ state_attr('climate.spa', 'temperature') }}°C"
```

### Carte Lovelace simple

```yaml
type: thermostat
entity: climate.spa
name: Mon Spa
```

📖 **Plus d'exemples** : [EXAMPLES.md](EXAMPLES.md) (automations, cartes Lovelace avancées, etc.)

## 🔌 Configuration EW11A (résumé)

Paramètres requis :
- **Mode** : TCP Server
- **Baud Rate** : 9600
- **Port** : 8899

📖 **Guide complet** : [QUICKSTART.md](QUICKSTART.md) (branchement, configuration WiFi, etc.)

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

## 🆘 Dépannage

### ❌ "Impossible de se connecter"

1. Vérifiez l'adresse IP de l'EW11A (peut changer au redémarrage)
2. Testez : `telnet <IP_EW11A> 8899`
3. Vérifiez que l'EW11A est allumé

### ❌ "Le mode change tout le temps"

**C'est normal !** En mode ECO, le spa alterne automatiquement entre Standard/Eco/Sommeil pour économiser l'énergie.

### ❌ "Les valeurs ne se mettent pas à jour"

1. Allez dans les **Options** de l'intégration
2. Augmentez "Fiabilité des données" à **7** ou **10**

### 💡 Activer les logs détaillés

```yaml
# configuration.yaml
logger:
  logs:
    custom_components.balboa_gs500z: debug
```

📖 **Plus d'aide** : [Issues GitHub](https://github.com/GevaudanBeast/Balboa-GS500z/issues)

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
