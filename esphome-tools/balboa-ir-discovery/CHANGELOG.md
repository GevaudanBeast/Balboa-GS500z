# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.0] - 2024-01-XX

### ✨ Ajouté

- 🎯 Découverte automatique de codes IR avec validation humaine
- 📡 Support de 6 protocoles IR : NEC, RC5, RC6, Samsung, LG, Sony
- 🎮 Interface Home Assistant complète avec boutons de contrôle
- 📊 Capteurs de progression en temps réel
- ⏸️ Fonction pause/reprise de la découverte
- 🔄 Mode manuel pour tester des codes spécifiques
- 📝 Logs structurés avec marquage des codes validés
- 🔧 Configuration flexible via substitutions YAML
- 📚 Documentation complète :
  - Guide d'installation (SETUP.md)
  - Guide d'utilisation (USAGE.md)
  - Démarrage rapide (QUICKSTART.md)
  - README principal
  - Template de documentation des codes découverts
- 🎨 Interface utilisateur intuitive avec emojis
- 🔌 Support optionnel RS-485 pour validation future
- 📱 Support récepteur IR pour capture de codes existants

### 🔧 Configuration

- GPIO configurables pour émetteur/récepteur IR
- Délai entre codes ajustable
- Plage de codes personnalisable
- Sélection de protocole dynamique

### 📖 Documentation

- Installation complète avec schémas de câblage
- Exemples d'utilisation
- FAQ et dépannage
- Bonnes pratiques
- Template de documentation des résultats

### 🛠️ Technique

- Code ESPHome optimisé avec lambdas C++
- Gestion d'état avec variables globales
- Scripts réutilisables
- Logs multi-niveaux (INFO, WARN, DEBUG)
- Support de tous les ESP32

## [Non publié]

### 🚀 Prochaines fonctionnalités

- [ ] Validation automatique via RS-485
- [ ] Export JSON des codes découverts
- [ ] Import de codes connus pour tests rapides
- [ ] Graphiques de progression dans Home Assistant
- [ ] Base de données communautaire des codes
- [ ] Apprentissage de télécommande existante (capture IR)
- [ ] Mode "smart scan" avec détection automatique de plages intéressantes
- [ ] Notification Home Assistant quand un code est découvert
- [ ] Historique des codes testés
- [ ] Statistiques de découverte avancées

---

**Format des versions** : MAJEUR.MINEUR.CORRECTIF

- **MAJEUR** : Changements incompatibles de l'API
- **MINEUR** : Ajout de fonctionnalités rétrocompatibles
- **CORRECTIF** : Corrections de bugs rétrocompatibles
