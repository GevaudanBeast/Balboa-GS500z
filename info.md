# Balboa GS500Z Spa - Home Assistant Integration

**🇫🇷 Version française** | **[🇬🇧 English version](#english-version)**

---

## Description courte

Intégration Home Assistant pour **superviser en temps réel** votre spa Balboa GS500Z via RS-485 (module EW11A WiFi). Affiche la température, le mode de fonctionnement et l'état du chauffage.

⚠️ **Mode lecture seule** : Cette intégration permet de lire l'état du spa mais ne peut pas le contrôler via RS-485. Pour le contrôle, voir la [solution IR avec ESP32](IR_CONTROL.md).

## Fonctionnalités

✅ Température de l'eau en temps réel
✅ Température de consigne
✅ Mode de fonctionnement (Standard, Économique, Sommeil)
✅ État du chauffage (actif/inactif)
✅ Validation des données par fenêtre glissante
✅ Auto-reconnexion TCP
✅ Configuration via l'interface Home Assistant

## Liens utiles

- 📖 [Documentation complète](README.md)
- 🚀 [Guide de démarrage rapide (5 min)](QUICKSTART.md)
- 🎯 [Contrôle IR avec ESP32](IR_CONTROL.md)
- 🔧 [Détails du protocole RS-485](PROTOCOL.md)
- 💡 [Exemples d'automatisations](EXAMPLES.md)

---

## English version

### Short description

Home Assistant integration to **monitor in real-time** your Balboa GS500Z spa via RS-485 (EW11A WiFi module). Displays temperature, operating mode, and heater status.

⚠️ **Read-only mode**: This integration can read the spa state but cannot control it via RS-485. For control, see the [IR solution with ESP32](IR_CONTROL.en.md).

### Features

✅ Real-time water temperature
✅ Target temperature setpoint
✅ Operating mode (Standard, Economy, Sleep)
✅ Heater status (active/inactive)
✅ Sliding window data validation
✅ Automatic TCP reconnection
✅ Configuration via Home Assistant UI

### Useful links

- 📖 [Full documentation](README.en.md)
- 🚀 [Quick start guide (5 min)](QUICKSTART.en.md)
- 🎯 [IR control with ESP32](IR_CONTROL.en.md)
- 🔧 [RS-485 protocol details](PROTOCOL.en.md)
- 💡 [Automation examples](EXAMPLES.en.md)

---

**Made with ❤️ for the Home Assistant community**
