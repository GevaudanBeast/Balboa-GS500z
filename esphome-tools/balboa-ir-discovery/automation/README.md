# 🤖 Automation - Génération automatique de configuration

Ce dossier contient les scripts pour **automatiser** la génération de votre télécommande IR après la découverte.

---

## 📋 Contenu du dossier

| Fichier | Description |
|---------|-------------|
| **generate_remote_config.py** | Script Python de génération automatique |
| **custom_names.json.example** | Template pour noms personnalisés |
| **discovered_codes.json.example** | Exemple de codes découverts |
| **README.md** | Ce fichier |

---

## 🚀 Utilisation rapide

### Méthode 1 : Depuis Home Assistant (recommandé)

```bash
# Générer depuis le sensor Home Assistant
python3 generate_remote_config.py \
  --ha-entity sensor.balboa_ir_discovery_codes_decouverts_json \
  --ha-url http://homeassistant.local:8123 \
  --ha-token VOTRE_TOKEN_LONGUE_DUREE \
  --output ../balboa-ir-remote.yaml
```

### Méthode 2 : Depuis un fichier JSON

```bash
# Exporter les codes depuis HA, puis générer
python3 generate_remote_config.py \
  --json discovered_codes.json \
  --output ../balboa-ir-remote.yaml
```

### Méthode 3 : Avec noms personnalisés

```bash
# 1. Copier et éditer le fichier de noms
cp custom_names.json.example custom_names.json
nano custom_names.json

# 2. Générer avec les noms personnalisés
python3 generate_remote_config.py \
  --json discovered_codes.json \
  --names custom_names.json \
  --output ../balboa-ir-remote.yaml
```

---

## 📖 Guide détaillé

### Étape 1 : Obtenir un token Home Assistant

1. Ouvrez **Home Assistant**
2. Cliquez sur votre profil (en bas à gauche)
3. Allez dans **"Tokens d'accès longue durée"**
4. Cliquez sur **"Créer un token"**
5. Donnez-lui un nom : `Balboa IR Generator`
6. Copiez le token (il ne sera affiché qu'une fois !)

### Étape 2 : Récupérer les codes découverts

Deux options :

#### Option A : Directement depuis Home Assistant (automatique)

Le script va lire le sensor `sensor.balboa_ir_discovery_codes_decouverts_json` directement depuis HA.

**Avantages** :
- ✅ Automatique, pas besoin d'exporter
- ✅ Toujours à jour

#### Option B : Export manuel

1. Ouvrez **Home Assistant**
2. Allez dans **Outils de développement** → **États**
3. Cherchez `sensor.balboa_ir_discovery_codes_decouverts_json`
4. Copiez le contenu de **"state"** (le JSON)
5. Collez-le dans un fichier `discovered_codes.json`

### Étape 3 : Personnaliser les noms (optionnel)

Si vous voulez donner des noms explicites aux boutons :

1. Copiez le template :
   ```bash
   cp custom_names.json.example custom_names.json
   ```

2. Éditez `custom_names.json` :
   ```json
   {
     "0x00000042": "Mode ECO",
     "0x00000043": "Mode Standard",
     "0x00000050": "Température +"
   }
   ```

3. Générez avec `--names custom_names.json`

**Si vous ne spécifiez pas de noms**, le script va :
- Essayer de deviner la fonction (température, mode, etc.)
- Utiliser un nom générique : "Code 0x00000042"

### Étape 4 : Générer la configuration

```bash
python3 generate_remote_config.py \
  --ha-entity sensor.balboa_ir_discovery_codes_decouverts_json \
  --ha-url http://homeassistant.local:8123 \
  --ha-token VOTRE_TOKEN \
  --names custom_names.json \
  --output ../balboa-ir-remote.yaml \
  --verbose
```

**Sortie attendue** :
```
📥 Chargement des codes découverts...
✅ 6 code(s) chargé(s)
📥 Chargement des noms personnalisés depuis custom_names.json...
✅ 3 nom(s) personnalisé(s) chargé(s)
⚙️  Génération de la configuration ESPHome...
💾 Écriture dans ../balboa-ir-remote.yaml...
✅ Configuration générée avec succès !

📄 Fichier: /path/to/balboa-ir-remote.yaml
📊 6 bouton(s) créé(s)

🚀 Prochaines étapes:
   1. Vérifiez le fichier généré
   2. Personnalisez les noms de boutons si nécessaire
   3. Flashez un nouvel ESP32 avec cette configuration
   4. Ajoutez l'appareil à Home Assistant
   5. Profitez de votre télécommande IR ! 🎉
```

### Étape 5 : Vérifier la configuration générée

Ouvrez `balboa-ir-remote.yaml` et vérifiez :

```yaml
button:
  # Mode ECO
  - platform: template
    name: "Mode ECO"
    icon: "mdi:cog"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x42
      - logger.log:
          format: "📡 Envoi Mode ECO: 0x00000042"
          level: INFO
```

### Étape 6 : Flasher un ESP32

1. Copiez `balboa-ir-remote.yaml` dans votre dossier ESPHome
2. Créez/vérifiez le fichier `secrets.yaml`
3. Flashez un nouvel ESP32 (ou réutilisez celui de la découverte)

```bash
esphome run balboa-ir-remote.yaml
```

---

## 🔧 Options du script

### Options de base

| Option | Description | Exemple |
|--------|-------------|---------|
| `--json FILE` | Charger depuis fichier JSON | `--json codes.json` |
| `--ha-entity ID` | Charger depuis Home Assistant | `--ha-entity sensor.balboa_...` |
| `--output FILE` | Fichier de sortie | `--output remote.yaml` |

### Options Home Assistant

| Option | Description | Défaut |
|--------|-------------|--------|
| `--ha-url URL` | URL de Home Assistant | `http://homeassistant.local:8123` |
| `--ha-token TOKEN` | Token d'accès | (requis si --ha-entity) |

### Options de personnalisation

| Option | Description |
|--------|-------------|
| `--names FILE` | Fichier JSON avec noms personnalisés |
| `--verbose` | Mode verbeux (affiche plus d'infos) |

---

## 📊 Format des fichiers

### discovered_codes.json

```json
[
  {
    "protocol": "NEC",
    "code": "0x00000042",
    "code_dec": 66,
    "timestamp": 12345
  }
]
```

### custom_names.json

```json
{
  "0x00000042": "Mode ECO",
  "0x00000043": "Mode Standard"
}
```

---

## 🎯 Workflow complet automatisé

```
┌─────────────────────────────────────────────────────────┐
│ 1. DÉCOUVERTE                                           │
│    ▶️ Démarrer → Observer → ✅ Valider                 │
│    Codes stockés automatiquement dans                   │
│    sensor.balboa_ir_discovery_codes_decouverts_json     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. PERSONNALISATION (optionnel)                         │
│    Éditer custom_names.json                             │
│    {"0x42": "Mode ECO", "0x50": "Temp+"}                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. GÉNÉRATION AUTOMATIQUE                               │
│    python3 generate_remote_config.py                    │
│      --ha-entity sensor.balboa_ir_discovery_...         │
│      --ha-token TOKEN                                   │
│      --names custom_names.json                          │
│    → balboa-ir-remote.yaml créé automatiquement !       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. FLASH ESP32                                          │
│    esphome run balboa-ir-remote.yaml                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. CONTRÔLE DANS HOME ASSISTANT                         │
│    Boutons automatiquement disponibles !                │
│    ✅ Mode ECO   ✅ Temp+   ✅ Chauffage                │
└─────────────────────────────────────────────────────────┘
```

**Temps total** : ~10 minutes (après la découverte)

---

## 🆘 Dépannage

### Erreur : Module 'requests' non installé

```bash
pip install requests
```

### Erreur : Connexion à Home Assistant impossible

Vérifiez :
- ✅ URL correcte (`--ha-url`)
- ✅ Token valide (`--ha-token`)
- ✅ Home Assistant accessible depuis votre machine

### Erreur : Aucun code découvert

Lancez d'abord la découverte avec `balboa-ir-discovery.yaml` !

### Les boutons générés ne fonctionnent pas

Vérifiez :
- ✅ LED IR correctement câblée
- ✅ LED pointée vers le spa
- ✅ Protocole correct dans les codes découverts

---

## 💡 Astuces

### Exporter les codes pour backup

```bash
# Depuis le script
python3 generate_remote_config.py \
  --ha-entity sensor.balboa_ir_discovery_codes_decouverts_json \
  --ha-token TOKEN \
  --json backup_codes.json

# Ou manuellement depuis HA
# Copiez le state du sensor dans un fichier
```

### Re-générer après de nouvelles découvertes

Simplement relancez le script, il lira automatiquement les derniers codes depuis HA.

### Fusionner plusieurs sessions de découverte

Éditez manuellement le JSON pour combiner les codes :

```json
[
  ...codes_session_1,
  ...codes_session_2
]
```

---

## 📚 Voir aussi

- **[../README.md](../README.md)** - Documentation principale
- **[../docs/USAGE.md](../docs/USAGE.md)** - Guide d'utilisation de la découverte
- **[../docs/AFTER_DISCOVERY.md](../docs/AFTER_DISCOVERY.md)** - Guide complet post-découverte

---

**Automatisation = Gain de temps ! 🚀**
