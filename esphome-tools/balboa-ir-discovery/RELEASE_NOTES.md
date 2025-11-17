# 🎉 Balboa IR Discovery Tool v2.0.0

**Date de sortie** : 17 novembre 2025

## 🚀 Nouveauté Majeure : Automatisation Post-Découverte

Cette version majeure transforme complètement l'expérience utilisateur en automatisant le workflow complet **de la découverte au contrôle** en moins d'une heure !

---

## ✨ Nouveautés

### 🤖 Export JSON Automatique
- **Nouveau sensor** : `sensor.balboa_ir_discovery_codes_decouverts_json`
- Sauvegarde automatique des codes validés
- Format JSON structuré avec timestamp
- Accessible directement dans Home Assistant

### 🐍 Script Python de Génération Automatique
**Nouveau fichier** : `automation/generate_remote_config.py`

Génère automatiquement votre configuration ESPHome de télécommande IR :
```bash
python3 generate_remote_config.py \
  --ha-entity sensor.balboa_ir_discovery_codes_decouverts_json \
  --ha-token VOTRE_TOKEN \
  --output balboa-ir-remote.yaml
```

**Fonctionnalités** :
- Lecture depuis Home Assistant API ou fichier JSON
- Support des noms personnalisés pour les boutons
- Détection intelligente des fonctions (température, mode, etc.)
- Interface CLI complète avec `--help`
- Type hints et docstrings complets

### 📱 8 Exemples de Dashboards Lovelace
**Nouveau fichier** : `examples/lovelace_dashboards.yaml`

Dashboards prêts à copier-coller :
1. **Simple** - Layout vertical basique
2. **Horizontal** - Boutons en ligne
3. **Avec État RS-485** - Combinaison lecture + contrôle
4. **Minimaliste** - Carte unique
5. **Picture Elements** - Style télécommande visuelle
6. **Avec Scripts** - Appuis multiples
7. **Avec Notifications** - Confirmations automatiques
8. **Mobile-Friendly** - Gros boutons pour smartphone

### 🎨 Template de Télécommande IR
**Nouveau fichier** : `examples/balboa-ir-remote.yaml`

Configuration ESPHome complète avec :
- Boutons pour tous les modes (ECO, Standard, Sleep)
- Contrôle de température (+/-)
- Chauffage, Jets, Lumières
- Prêt à flasher sur ESP32

### 📚 Guide Post-Découverte Complet
**Nouveau fichier** : `docs/AFTER_DISCOVERY.md`

Guide détaillé avec **3 méthodes** :
1. **Automatique** (recommandée) - Script Python + génération auto
2. **Semi-automatique** - Export manuel + script
3. **Manuelle** - Création manuelle de la config

Inclut :
- Workflow de bout en bout
- Intégration avec RS-485 existante
- Exemples de dashboards
- FAQ complète

### 🗑️ Bouton "Effacer Codes"
Nouvelle fonctionnalité dans l'interface de découverte pour réinitialiser la liste des codes découverts.

---

## 🔧 Améliorations

### Sécurité
- **Fallback AP password** maintenant configurable via substitutions
- Plus besoin de modifier le YAML, simple substitution
- Documentation améliorée sur la sécurité

### Documentation
- **Guide de contribution** (CONTRIBUTING.md) - 250+ lignes
- **automation/README.md** - 400 lignes de documentation du script
- **PROJECT_SUMMARY_V2.md** - Statistiques complètes du projet
- README.md mis à jour avec section automatisation

### Technique
- Stockage persistant des codes découverts
- Text sensor JSON pour export facile
- Script Python avec type hints et docstrings
- Gestion d'erreurs robuste (requests optionnel)
- Templates YAML pour génération automatique

---

## 📊 Workflow Complet (45 minutes)

```
┌─────────────────────────────────────────────────────────┐
│ 1. DÉCOUVERTE (30 min)                                  │
│    ▶️ Démarrer → Observer → ✅ Valider                 │
│    Codes stockés auto dans sensor HA                    │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. GÉNÉRATION AUTO (1 min)                              │
│    python3 generate_remote_config.py ...                │
│    → balboa-ir-remote.yaml créé !                       │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. FLASH ESP32 (5 min)                                  │
│    esphome run balboa-ir-remote.yaml                    │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. CONTRÔLE HA (immédiat)                               │
│    ✅ Boutons disponibles dans Home Assistant !         │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Fichiers Ajoutés

### Documentation (3 fichiers)
- `docs/AFTER_DISCOVERY.md` (450 lignes)
- `automation/README.md` (400 lignes)
- `CONTRIBUTING.md` (250 lignes)

### Automatisation (4 fichiers)
- `automation/generate_remote_config.py` (450 lignes)
- `automation/custom_names.json.example`
- `automation/discovered_codes.json.example`
- `PROJECT_SUMMARY_V2.md`

### Exemples (2 fichiers)
- `examples/balboa-ir-remote.yaml` (150 lignes)
- `examples/lovelace_dashboards.yaml` (600 lignes)

### Fichiers Modifiés
- `balboa-ir-discovery.yaml` - Export JSON + bouton effacer
- `README.md` - Section automatisation
- `CHANGELOG.md` - Versions 1.0.0 et 2.0.0

---

## 📈 Statistiques

- **Total fichiers** : 22 (+10 depuis v1.0.0)
- **Lignes de code/doc** : ~6 600 (+2 600)
- **Protocoles IR** : 6 supportés
- **Dashboards** : 8 exemples
- **Méthodes post-découverte** : 3 documentées

---

## 🎯 Installation

### Pour Nouveaux Utilisateurs

1. **Télécharger le projet** :
   ```bash
   git clone https://github.com/GevaudanBeast/Balboa-GS500z.git
   cd Balboa-GS500z/esphome-tools/balboa-ir-discovery
   ```

2. **Lire le guide rapide** :
   - `docs/QUICKSTART.md` (5 minutes)

3. **Suivre l'installation** :
   - `docs/SETUP.md` (installation complète)

### Pour Utilisateurs v1.0.0

**Migration simple** :

1. **Sauvegarder vos codes découverts** (si vous en avez)
2. **Mettre à jour les fichiers** :
   ```bash
   git pull origin main
   ```
3. **Flasher la nouvelle version** :
   ```bash
   esphome run balboa-ir-discovery.yaml
   ```
4. **Utiliser le script de génération** :
   ```bash
   python3 automation/generate_remote_config.py --help
   ```

**Note** : Vos codes découverts seront maintenant automatiquement sauvegardés dans Home Assistant !

---

## 📚 Documentation

### Guides Principaux
- **[README.md](README.md)** - Documentation principale
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Démarrage rapide (5 min)
- **[docs/SETUP.md](docs/SETUP.md)** - Installation complète
- **[docs/USAGE.md](docs/USAGE.md)** - Guide d'utilisation
- **[docs/AFTER_DISCOVERY.md](docs/AFTER_DISCOVERY.md)** - Post-découverte ⭐ NOUVEAU

### Automatisation
- **[automation/README.md](automation/README.md)** - Guide du script Python
- **[automation/generate_remote_config.py](automation/generate_remote_config.py)** - Script de génération

### Exemples
- **[examples/balboa-ir-remote.yaml](examples/balboa-ir-remote.yaml)** - Template de télécommande
- **[examples/lovelace_dashboards.yaml](examples/lovelace_dashboards.yaml)** - 8 dashboards

### Contribution
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guide de contribution ⭐ NOUVEAU

---

## 🐛 Corrections de Bugs

Aucun bug corrigé dans cette version (nouvelle fonctionnalité majeure).

---

## ⚠️ Breaking Changes

**Aucun** - Rétrocompatible avec v1.0.0

---

## 🔜 Prochaine Version (Roadmap)

Les fonctionnalités planifiées pour les versions futures :

- [ ] Validation automatique via RS-485
- [ ] Import de codes connus via interface HA
- [ ] Base de données communautaire des codes
- [ ] Mode "smart scan" intelligent
- [ ] Génération automatique d'entité Climate
- [ ] Interface web de mapping des codes

Voir [CHANGELOG.md](CHANGELOG.md) pour la roadmap complète.

---

## 🙏 Remerciements

Merci à tous les utilisateurs de la v1.0.0 pour vos retours et suggestions !

Cette version n'aurait pas été possible sans :
- La communauté **Home Assistant**
- L'équipe **ESPHome**
- Les utilisateurs qui ont partagé leurs codes découverts

---

## 📞 Support

- **Documentation** : Voir dossier `docs/`
- **Issues** : [GitHub Issues](../../issues)
- **Discussions** : [GitHub Discussions](../../discussions)
- **Forum Home Assistant** : Recherchez "Balboa IR Discovery"

---

## 📝 Notes de Migration

### Depuis v1.0.0

**Aucune action requise** - La nouvelle version est totalement compatible.

**Recommandations** :
1. Mettez à jour votre configuration
2. Profitez de l'export JSON automatique
3. Utilisez le script de génération pour créer votre télécommande
4. Explorez les nouveaux dashboards Lovelace

### Nouveaux Utilisateurs

Suivez simplement le [QUICKSTART.md](docs/QUICKSTART.md) !

---

## ⚖️ License

MIT License - Libre d'utilisation, modification et distribution

---

## 🎉 Conclusion

**Balboa IR Discovery Tool v2.0.0** rend la découverte et l'utilisation des codes IR **plus simple que jamais** :

✅ Découverte en 30 minutes
✅ Génération automatique en 1 minute
✅ Contrôle opérationnel en 45 minutes total

**Merci d'utiliser Balboa IR Discovery Tool !**

---

*Pour voir tous les changements en détail, consultez [CHANGELOG.md](CHANGELOG.md)*
