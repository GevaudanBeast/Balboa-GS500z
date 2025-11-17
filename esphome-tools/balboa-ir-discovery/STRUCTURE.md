# Structure du projet

## 📂 Arborescence

```
balboa-ir-discovery/
│
├── 📄 README.md                          # Documentation principale
├── 📄 LICENSE                            # License MIT
├── 📄 CHANGELOG.md                       # Historique des versions
├── 📄 STRUCTURE.md                       # Ce fichier
├── 📄 .gitignore                         # Fichiers à ignorer par Git
│
├── 🔧 balboa-ir-discovery.yaml          # ⭐ Configuration ESPHome principale
├── 🔧 secrets.yaml.example              # Template du fichier de secrets
│
├── 📁 docs/                              # Documentation détaillée
│   ├── 📄 SETUP.md                      # Guide d'installation complet
│   ├── 📄 USAGE.md                      # Guide d'utilisation détaillé
│   └── 📄 QUICKSTART.md                 # Démarrage rapide (5 minutes)
│
└── 📁 examples/                          # Exemples et templates
    └── 📄 discovered_codes_template.md  # Template pour documenter les résultats
```

## 📖 Description des fichiers

### Fichiers principaux

| Fichier | Description | À modifier ? |
|---------|-------------|--------------|
| `balboa-ir-discovery.yaml` | Configuration ESPHome complète | ⚠️ Seulement GPIO/délais |
| `secrets.yaml.example` | Template pour vos secrets (WiFi, API) | ✅ Copier en `secrets.yaml` |
| `README.md` | Documentation principale du projet | ❌ Sauf contribution |

### Documentation

| Fichier | Public cible | Temps de lecture |
|---------|--------------|------------------|
| `QUICKSTART.md` | Débutants pressés | 3 minutes |
| `SETUP.md` | Tous niveaux | 15 minutes |
| `USAGE.md` | Utilisateurs après installation | 20 minutes |

### Exemples

| Fichier | Usage |
|---------|-------|
| `discovered_codes_template.md` | Template pour documenter vos codes découverts |

## 🔧 Fichiers générés (non versionnés)

Ces fichiers sont créés automatiquement et **ne doivent PAS être commités** :

```
balboa-ir-discovery/
├── secrets.yaml                 # 🔒 Vos secrets (WiFi, API)
├── .esphome/                    # Build cache ESPHome
│   ├── build/
│   └── ...
└── *.log                        # Logs de debug
```

## 🎯 Workflow d'utilisation

```
1. 📥 Télécharger le projet
   └─> balboa-ir-discovery/

2. 📝 Copier secrets.yaml.example → secrets.yaml
   └─> Éditer secrets.yaml avec vos infos

3. 🔌 Câbler ESP32 + LED IR
   └─> Voir docs/SETUP.md

4. 💾 Flasher l'ESP32
   └─> ESPHome Dashboard → INSTALL

5. 🏠 Ajouter à Home Assistant
   └─> Automatique via ESPHome

6. 🚀 Lancer la découverte
   └─> Interface HA → Démarrer

7. 📊 Documenter les résultats
   └─> examples/discovered_codes_template.md
```

## 🔍 Fichiers par cas d'usage

### Installation rapide (5 min)

```
📄 docs/QUICKSTART.md
🔧 balboa-ir-discovery.yaml
🔧 secrets.yaml.example
```

### Installation détaillée

```
📄 docs/SETUP.md
📄 README.md
🔧 balboa-ir-discovery.yaml
🔧 secrets.yaml.example
```

### Utilisation quotidienne

```
📄 docs/USAGE.md
🔧 balboa-ir-discovery.yaml (référence)
```

### Documentation des résultats

```
📄 examples/discovered_codes_template.md
```

### Contribution au projet

```
📄 README.md
📄 CHANGELOG.md
📄 LICENSE
📄 tous les fichiers de docs/
```

## 🛠️ Fichiers techniques

### Configuration ESPHome

Le fichier `balboa-ir-discovery.yaml` contient :

| Section | Lignes approx. | Description |
|---------|----------------|-------------|
| `substitutions` | 1-30 | Variables de configuration |
| `esphome` | 31-60 | Config de base ESP32 |
| `wifi`, `api`, `ota` | 61-90 | Connectivité |
| `remote_transmitter/receiver` | 91-130 | Composants IR |
| `globals` | 131-180 | Variables globales |
| `sensor`, `text_sensor` | 181-260 | Capteurs de progression |
| `number`, `select` | 261-330 | Paramètres configurables |
| `button` | 331-550 | Boutons de contrôle |
| `script` | 551-fin | Logique de découverte |

### Secrets (secrets.yaml)

```yaml
wifi_ssid: "..."              # Nom WiFi
wifi_password: "..."          # Mot de passe WiFi
api_encryption_key: "..."     # Clé API HA (base64)
ota_password: "..."           # Mot de passe OTA
```

## 📐 Architecture logicielle

```
┌─────────────────────────────────────────────────────┐
│              Home Assistant                         │
│  ┌───────────────────────────────────────────────┐  │
│  │         Interface utilisateur                 │  │
│  │  [▶️ Démarrer] [⏸️ Pause] [✅ Ça marche!]    │  │
│  │  Progression: 25% | Codes: 65/256            │  │
│  └───────────────────────────────────────────────┘  │
│                      ⬇️ API                         │
└─────────────────────────────────────────────────────┘
                       ⬇️
┌─────────────────────────────────────────────────────┐
│              ESPHome (ESP32)                        │
│  ┌───────────────────────────────────────────────┐  │
│  │  Script: discovery_loop                       │  │
│  │    ├─> Incrémente code                        │  │
│  │    ├─> Appelle send_current_code              │  │
│  │    └─> Attend délai                           │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Script: send_current_code                    │  │
│  │    ├─> Sélectionne protocole                  │  │
│  │    ├─> Encode le code IR                      │  │
│  │    └─> Envoie via remote_transmitter          │  │
│  └───────────────────────────────────────────────┘  │
│                      ⬇️ GPIO4                       │
└─────────────────────────────────────────────────────┘
                       ⬇️
┌─────────────────────────────────────────────────────┐
│              LED IR 940nm                           │
│            (Émission infrarouge)                    │
└─────────────────────────────────────────────────────┘
                       ⬇️
┌─────────────────────────────────────────────────────┐
│              Spa Balboa GS500Z                      │
│          (Récepteur IR intégré)                     │
└─────────────────────────────────────────────────────┘
```

## 🔄 Cycle de vie d'une découverte

```
1. [Utilisateur] Clique "▶️ Démarrer"
   ⬇️
2. [ESP32] discovery_active = true
   ⬇️
3. [ESP32] Boucle while (current_code <= end_code)
   ⬇️
4. [ESP32] Appelle send_current_code()
   ⬇️
5. [ESP32] Encode et envoie via IR
   ⬇️
6. [Spa] Reçoit le code IR
   ⬇️
7. [Spa] Réagit (ou pas)
   ⬇️
8. [Utilisateur] Observe le spa
   ⬇️
9a. [Si réaction] Clique "✅ Ça marche!"
    ⬇️
    [ESP32] Log WARN avec le code validé

9b. [Sinon] Attend ou clique "⏭️ Suivant"
    ⬇️
10. [ESP32] current_code++
    ⬇️
11. Retour à l'étape 3 (tant que current_code <= end_code)
    ⬇️
12. [ESP32] discovery_active = false
    ⬇️
13. [ESP32] Statut = "Terminé !"
```

## 📊 Flux de données

```
Configuration (HA)
    ⬇️
[Protocole, Code Début, Code Fin]
    ⬇️
Variables globales (ESP32)
    ⬇️
Scripts de découverte
    ⬇️
remote_transmitter
    ⬇️
LED IR
    ⬇️
Spa Balboa
    ⬇️
Observation humaine
    ⬇️
Validation (Bouton HA)
    ⬇️
Logs (ESP32)
    ⬇️
Documentation (Utilisateur)
```

---

**Cette structure est conçue pour être simple, modulaire et facile à maintenir.**
