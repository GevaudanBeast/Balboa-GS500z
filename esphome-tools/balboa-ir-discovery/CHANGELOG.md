# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [2.0.0] - 2025-11-17

### ✨ Ajouté - Automatisation Post-Découverte

- 🤖 **Export JSON automatique** des codes découverts vers Home Assistant
  - Nouveau sensor : `sensor.balboa_ir_discovery_codes_decouverts_json`
  - Sauvegarde automatique lors de la validation
  - Format JSON structuré avec timestamp
- 🐍 **Script Python de génération automatique** (generate_remote_config.py)
  - Lecture depuis Home Assistant API ou fichier JSON
  - Génération automatique de configuration ESPHome
  - Support des noms personnalisés pour les boutons
  - Détection intelligente des fonctions (température, mode, etc.)
  - Interface CLI complète avec --help
- 📱 **8 exemples de dashboards Lovelace** prêts à l'emploi
  - Simple, horizontal, grid, picture-elements
  - Mobile-friendly, avec scripts, notifications
  - Combinaison avec état RS-485
- 🎨 **Template de télécommande IR** (balboa-ir-remote.yaml)
  - Configuration complète avec tous les contrôles
  - Boutons pour modes, température, chauffage
  - Prêt à flasher
- 📚 **Guide complet post-découverte** (AFTER_DISCOVERY.md)
  - 3 méthodes : automatique, semi-automatique, manuelle
  - Workflow de bout en bout
  - Intégration avec RS-485 existante
- 🗑️ **Bouton "Effacer Codes"** pour réinitialiser la liste

### 🔧 Améliorations

- Stockage persistant des codes découverts
- Text sensor JSON pour export facile
- Documentation du workflow complet (découverte → contrôle en 45 min)
- Exemples JSON pour custom names et discovered codes

### 📖 Documentation

- Guide automation/README.md (400 lignes)
- Guide AFTER_DISCOVERY.md (450 lignes)
- Exemples lovelace_dashboards.yaml (600 lignes)
- PROJECT_SUMMARY_V2.md avec statistiques complètes
- README.md mis à jour avec section automatisation

### 🛠️ Technique

- Script Python avec type hints et docstrings
- Gestion d'erreurs robuste (requests optionnel)
- Templates YAML pour génération automatique
- Support de tous les protocoles IR

## [1.0.0] - 2025-11-17

### ✨ Ajouté - Version Initiale

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
- [ ] Import de codes connus pour tests rapides via interface HA
- [ ] Graphiques de progression dans Home Assistant
- [ ] Base de données communautaire des codes
- [ ] Apprentissage de télécommande existante (capture IR améliorée)
- [ ] Mode "smart scan" avec détection automatique de plages intéressantes
- [ ] Notification Home Assistant quand un code est découvert
- [ ] Historique des codes testés avec horodatage
- [ ] Statistiques de découverte avancées
- [ ] Génération automatique d'entité Climate
- [ ] Interface web de mapping des codes

---

**Format des versions** : MAJEUR.MINEUR.CORRECTIF

- **MAJEUR** : Changements incompatibles de l'API
- **MINEUR** : Ajout de fonctionnalités rétrocompatibles
- **CORRECTIF** : Corrections de bugs rétrocompatibles
