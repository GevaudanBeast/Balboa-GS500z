# Guide d'Installation — Balboa GS500Z
# Installation Guide — Balboa GS500Z

> **FR** : Ce guide vous accompagne pas à pas dans l'installation et la
> configuration complète : matériel, firmware ESPHome, intégration HA et
> dashboard Lovelace.
>
> **EN**: This guide walks you through the complete installation and
> configuration: hardware, ESPHome firmware, HA integration and Lovelace
> dashboard.

## FR — Table des matières / EN — Table of contents

1. [Prérequis / Prerequisites](#prérequis--prerequisites)
2. [Installation du matériel / Hardware installation](#installation-du-matériel--hardware-installation)
3. [Firmware ESPHome](#firmware-esphome)
4. [Configuration de l'EW11A / EW11A configuration](#configuration-de-lew11a--ew11a-configuration) *(optionnel si TTL485 seul / optional if TTL485 only)*
5. [Installation de l'intégration HA / HA integration installation](#installation-de-lintégration--ha-integration-installation)
6. [Dashboard Lovelace](#dashboard-lovelace)
7. [Vérification / Verification](#vérification--verification)
8. [Dépannage / Troubleshooting](#dépannage--troubleshooting)

## 🔧 Prérequis / Prerequisites

### FR — Matériel requis / EN — Required hardware

- ✅ Spa Balboa avec carte de contrôle **GS500Z** / Balboa spa with **GS500Z** controller board
- ✅ Clavier Balboa **VL403** / Balboa **VL403** keypad
- ✅ Module **TTL485 (MAX485)** sur J18 pour la lecture RS-485 / **TTL485 (MAX485)** module on J18 for RS-485 reading
- ✅ **ESP8266 NodeMCU v2** + **optocoupleurs TLP281-4** sur J1 pour le contrôle / **ESP8266 NodeMCU v2** + **TLP281-4 optocouplers** on J1 for control
- ✅ Home Assistant (version 2023.1 ou supérieure / or higher)

> Le module **EW11A** reste utilisable comme passerelle RS-485→WiFi à la place
> du TTL485 — la configuration reste identique côté HA. /
> The **EW11A** module can still be used as an RS-485→WiFi bridge instead of
> the TTL485 — the HA configuration remains identical.

### Connaissances requises

- 🔨 Câblage électrique de base (raccordement RS-485)
- 💻 Utilisation de Home Assistant
- 🌐 Configuration réseau de base (adresse IP, port)

### Avertissement de sécurité

⚠️ **Attention** : Avant toute intervention sur le spa, coupez l'alimentation électrique au disjoncteur.

## 🔌 Installation du matériel

### Étape 1 : Localiser les connexions RS-485

1. Ouvrez le compartiment électronique du spa
2. Localisez la carte de contrôle GS500Z
3. Repérez les bornes RS-485 :
   - Généralement étiquetées **A**, **B**, **GND** (ou **+**, **-**, **⏚**)
   - Consultez le manuel de votre spa si nécessaire

### Étape 2 : Raccordement du module EW11A

#### Schéma de câblage

```
┌──────────────────────────┐
│   Carte GS500Z           │
│                          │
│   RS-485  A ●────────────┼──── A (ou +)
│           B ●────────────┼──── B (ou -)
│         GND ●────────────┼──── GND
└──────────────────────────┘
                            │
                            │
                    ┌───────┴──────┐
                    │   EW11A      │
                    │              │
                    │  [WiFi Icon] │
                    └──────────────┘
```

#### Raccordement physique

1. **Connexion A** (ou +) :
   - Reliez la borne A de la GS500Z à la borne A de l'EW11A
   - Utilisez un fil de couleur distinctive (ex: rouge)

2. **Connexion B** (ou -) :
   - Reliez la borne B de la GS500Z à la borne B de l'EW11A
   - Utilisez un fil de couleur différente (ex: noir)

3. **Connexion GND** :
   - Reliez la masse GND de la GS500Z à la masse de l'EW11A
   - Utilisez un fil vert/jaune ou blanc

4. **Alimentation de l'EW11A** :
   - Selon le modèle, alimentez l'EW11A en 5V ou 12V
   - Utilisez une alimentation dédiée ou la sortie auxiliaire du spa (si disponible)

### Étape 3 : Vérification du câblage

- ✅ Les connexions sont bien serrées
- ✅ Aucun fil dénudé ne touche le châssis
- ✅ Les polarités A/B sont respectées
- ✅ L'EW11A s'allume (LED allumée)

## ⚡ Firmware ESPHome

> **FR** : Cette section décrit l'installation du firmware ESPHome sur
> l'ESP8266 NodeMCU qui pilote les optocoupleurs J1.
>
> **EN**: This section describes installing the ESPHome firmware on the
> ESP8266 NodeMCU that drives the J1 optocouplers.

### FR — Prérequis ESPHome / EN — ESPHome prerequisites

```bash
pip install esphome
```

### FR — Étape 1 : Créer le fichier secrets

**FR** : Copier le template et renseigner vos valeurs :

**EN**: Copy the template and fill in your values:

```bash
cd esphome-tools/balboa-spa-control
cp secrets.yaml.example secrets.yaml
# Editer secrets.yaml avec votre SSID, mot de passe WiFi, cle API, mot de passe OTA
# Edit secrets.yaml with your SSID, WiFi password, API key, OTA password
```

Générer une clé API / Generate an API key:

```bash
openssl rand -base64 32
```

### FR — Étape 2 : Flasher l'ESP / EN — Step 2: Flash the ESP

**FR** : Connecter l'ESP8266 NodeMCU en USB, puis :

**EN**: Connect the ESP8266 NodeMCU via USB, then:

```bash
esphome run esphome-tools/balboa-spa-control/balboa-spa-control-v1.5.3.yaml
```

**FR** : Les mises à jour suivantes peuvent se faire en OTA (sans fil).

**EN**: Subsequent updates can be done OTA (wirelessly).

### FR — Étape 3 : Vérifier dans HA / EN — Step 3: Check in HA

**FR** : L'ESP apparaît automatiquement dans HA → Paramètres → Appareils
et services → ESPHome. Accepter l'intégration. Toutes les entités
(`sensor.*`, `binary_sensor.*`, `button.*`) sont découvertes automatiquement.

**EN**: The ESP appears automatically in HA → Settings → Devices and services
→ ESPHome. Accept the integration. All entities (`sensor.*`, `binary_sensor.*`,
`button.*`) are discovered automatically.

> Voir `esphome-tools/balboa-spa-control/README.md` pour la liste complète
> des entités et le câblage détaillé TTL485 + TLP281-4. /
> See `esphome-tools/balboa-spa-control/README.md` for the full entity list
> and detailed TTL485 + TLP281-4 wiring.

---

## 📡 Configuration de l'EW11A

### Étape 1 : Connexion au module

1. **Branchez l'EW11A**
2. **Connectez-vous au réseau WiFi de l'EW11A** :
   - Nom du réseau : généralement `EW11A_XXXXXX`
   - Mot de passe : consultez le manuel (souvent `12345678` ou vide)

3. **Ouvrez votre navigateur** et allez à :
   - Adresse : `http://192.168.4.1` (ou adresse par défaut du module)

### Étape 2 : Configuration WiFi

Dans l'interface web de l'EW11A :

1. **Allez dans "Network Settings"** (ou "Paramètres réseau")
2. **Configurez le WiFi** :
   - Mode : **Station** (client WiFi)
   - SSID : Nom de votre réseau WiFi
   - Mot de passe : Mot de passe de votre réseau
3. **Sauvegardez** et **redémarrez** le module

### Étape 3 : Configuration RS-485

Dans l'interface web de l'EW11A :

1. **Allez dans "Serial Settings"** (ou "Paramètres série")
2. **Configurez les paramètres RS-485** :
   ```
   Baud Rate:    9600
   Data Bits:    8
   Stop Bits:    1
   Parity:       None
   Flow Control: None
   ```

### Étape 4 : Configuration TCP

1. **Allez dans "Network Protocol"** (ou "Protocole réseau")
2. **Configurez le mode TCP** :
   ```
   Protocol:    TCP Server
   Local Port:  8899 (ou port de votre choix)
   ```
3. **Sauvegardez** et **redémarrez**

### Étape 5 : Trouver l'adresse IP de l'EW11A

Après redémarrage, l'EW11A se connecte à votre réseau WiFi.

**Option 1 : Via l'interface du routeur**
- Consultez la liste des appareils connectés
- Cherchez `EW11A` ou l'adresse MAC notée sur le module

**Option 2 : Via un scan réseau**
```bash
# Linux/Mac
nmap -sn 192.168.1.0/24

# Windows (avec nmap installé)
nmap -sn 192.168.1.0/24
```

**Option 3 : Via une app mobile**
- Installez "Fing" ou "Network Scanner"
- Scannez votre réseau local

### Étape 6 : Tester la connexion

```bash
# Remplacez 192.168.1.100 par l'IP de votre EW11A
telnet 192.168.1.100 8899
```

Si tout fonctionne, vous devriez voir des trames défiler :
```
[643F2B...]
[643F2B...]
[643F2B...]
```

Tapez `Ctrl+]` puis `quit` pour quitter telnet.

✅ **Parfait !** L'EW11A fonctionne correctement.

## 💾 Installation de l'intégration

### Méthode 1 : HACS (Recommandée)

1. **Ouvrez HACS** dans Home Assistant
   - Menu → HACS

2. **Ajoutez le dépôt** :
   - Cliquez sur les 3 points (⋮) en haut à droite
   - Choisissez "Custom repositories"
   - Ajoutez :
     ```
     https://github.com/GevaudanBeast/Balboa-GS500z
     ```
   - Catégorie : **Integration**
   - Cliquez sur "Add"

3. **Installez l'intégration** :
   - Recherchez "Balboa GS500Z"
   - Cliquez sur "Download"
   - Redémarrez Home Assistant

### Méthode 2 : Installation manuelle

1. **Téléchargez l'intégration** :
   ```bash
   cd /config
   git clone https://github.com/GevaudanBeast/Balboa-GS500z.git
   ```

2. **Copiez les fichiers** :
   ```bash
   cp -r Balboa-GS500z/custom_components/balboa_gs500z custom_components/
   ```

3. **Vérifiez la structure** :
   ```
   /config/custom_components/balboa_gs500z/
   ├── __init__.py
   ├── manifest.json
   ├── config_flow.py
   ├── const.py
   ├── coordinator.py
   ├── tcp_client.py
   ├── climate.py
   ├── binary_sensor.py
   ├── services.yaml
   ├── strings.json
   └── translations/
       ├── en.json
       └── fr.json
   ```

4. **Redémarrez Home Assistant**

## ⚙️ Configuration dans Home Assistant

### Étape 1 : Ajouter l'intégration

1. **Allez dans les paramètres** :
   - Menu → Paramètres → Appareils et services

2. **Ajoutez l'intégration** :
   - Cliquez sur "+ Ajouter une intégration"
   - Recherchez "Balboa GS500Z"
   - Cliquez sur l'intégration

### Étape 2 : Configuration initiale

Dans le formulaire de configuration :

```
┌──────────────────────────────────────────┐
│ Configuration du Spa Balboa GS500Z      │
├──────────────────────────────────────────┤
│                                          │
│ Adresse IP de l'hôte:                    │
│ [192.168.1.100        ]                  │
│                                          │
│ Port:                                    │
│ [8899                 ]                  │
│                                          │
│         [Annuler]      [Soumettre]       │
└──────────────────────────────────────────┘
```

- **Host** : Adresse IP de votre EW11A (ex: `192.168.1.100`)
- **Port** : Port TCP configuré (par défaut : `8899`)

3. **Cliquez sur "Soumettre"**

L'intégration va tester la connexion. Si tout se passe bien, vous verrez :

```
✅ Configuration réussie
```

### Étape 3 : Options avancées (optionnel)

1. **Cliquez sur "Configurer"** sur la carte de l'intégration

2. **Ajustez les options** :

```
┌──────────────────────────────────────────┐
│ Options Balboa GS500Z                    │
├──────────────────────────────────────────┤
│                                          │
│ Taille de la fenêtre glissante (3-20):   │
│ [5                    ]                  │
│                                          │
│ ☑ Activer le garde-fou d'ordre          │
│                                          │
│         [Annuler]      [Soumettre]       │
└──────────────────────────────────────────┘
```

- **Fenêtre glissante** : Nombre de trames pour validation (défaut : 5)
  - Plus petit = réponse plus rapide, moins fiable
  - Plus grand = plus fiable, réponse plus lente

- **Garde-fou d'ordre** : Respecte la séquence ST→ECO→SL→ST
  - ✅ Activé : sécurisé, évite les erreurs
  - ❌ Désactivé : permet toutes les transitions

3. **Cliquez sur "Soumettre"**

## 🖥️ Dashboard Lovelace

> **FR** : Le dashboard cible est disponible dans `lovelace/spa-dashboard.yaml`.
> Certaines entités ne sont pas encore implémentées dans le firmware v1.5.3 —
> voir `lovelace/README.md` pour le statut détaillé.
>
> **EN**: The target dashboard is available in `lovelace/spa-dashboard.yaml`.
> Some entities are not yet implemented in firmware v1.5.3 —
> see `lovelace/README.md` for the detailed status.

### FR — Installation du dashboard / EN — Dashboard installation

1. **FR** : Aller dans HA → Vue d'ensemble → Modifier le tableau de bord → ⋮ → Éditeur YAML.
   **EN**: Go to HA → Overview → Edit dashboard → ⋮ → YAML editor.

2. **FR** : Coller le contenu de `lovelace/spa-dashboard.yaml`.
   **EN**: Paste the contents of `lovelace/spa-dashboard.yaml`.

3. **FR** : Sauvegarder. Les entités manquantes apparaîtront avec une erreur
   jusqu'à leur implémentation dans le firmware v1.6+.
   **EN**: Save. Missing entities will show an error until they are implemented
   in firmware v1.6+.

### FR — Helpers HA à créer / EN — HA helpers to create

**FR** : Avant d'utiliser le dashboard, créer dans HA → Paramètres → Assistants :

**EN**: Before using the dashboard, create in HA → Settings → Helpers:

| Helper | Type | Description FR | EN |
|---|---|---|---|
| `input_boolean.spa_temp_pending` | Input Boolean | Changement de consigne en cours | Setpoint change in progress |

---

## ✅ Vérification / Verification

### FR — Vérifier les entités créées / EN — Check created entities

1. **Allez dans Paramètres → Appareils et services**
2. **Cliquez sur "Balboa GS500Z"**
3. **Vérifiez les entités** :

```
Appareil : Balboa GS500Z Spa

Entités :
┌─────────────────────────────────────────────┐
│ climate.spa              │ 37°C → 38°C  [ST]│
│ binary_sensor.spa_heater │ Actif            │
└─────────────────────────────────────────────┘
```

### Tester le contrôle

1. **Allez dans Outils de développement → Services**

2. **Testez le changement de température** :
   ```yaml
   service: climate.set_temperature
   target:
     entity_id: climate.spa
   data:
     temperature: 38
   ```

3. **Testez le changement de mode** :
   ```yaml
   service: climate.set_preset_mode
   target:
     entity_id: climate.spa
   data:
     preset_mode: eco
   ```

4. **Observez les logs** :
   - Paramètres → Système → Logs
   - Cherchez `balboa_gs500z`
   - Vérifiez qu'il n'y a pas d'erreurs

### Tester la carte thermostat

1. **Créez un tableau de bord de test** :
   - Allez dans Vue d'ensemble
   - Cliquez sur "Modifier le tableau de bord"
   - Ajoutez une carte "Thermostat"
   - Sélectionnez `climate.spa`

2. **Testez l'interface** :
   - Changez la température avec le curseur
   - Changez le mode avec les boutons
   - Vérifiez que les valeurs se mettent à jour

## 🐛 Dépannage

### Problème : "Échec de connexion"

**Symptôme** : Message d'erreur lors de la configuration.

**Solutions** :
1. Vérifiez l'adresse IP de l'EW11A :
   ```bash
   ping 192.168.1.100
   ```
2. Vérifiez le port :
   ```bash
   telnet 192.168.1.100 8899
   ```
3. Vérifiez que l'EW11A est en mode TCP Server
4. Vérifiez le pare-feu de Home Assistant

### Problème : Entités indisponibles

**Symptôme** : `climate.spa` et `binary_sensor.spa_heater` sont "Indisponibles".

**Solutions** :
1. Vérifiez les logs (Paramètres → Système → Logs)
2. Vérifiez la connexion réseau
3. Redémarrez l'intégration :
   - Paramètres → Appareils et services
   - Balboa GS500Z → ⋮ → Recharger

### Problème : Valeurs ne se mettent pas à jour

**Symptôme** : Les températures restent figées.

**Solutions** :
1. Activez les logs debug :
   ```yaml
   # configuration.yaml
   logger:
     default: info
     logs:
       custom_components.balboa_gs500z: debug
   ```
2. Observez les trames dans les logs
3. Augmentez la fenêtre glissante dans les options
4. Vérifiez que le spa envoie bien des trames :
   ```bash
   telnet 192.168.1.100 8899
   ```

### Problème : Commandes ne fonctionnent pas

**Symptôme** : Changement de température ou mode sans effet.

**Note** : L'implémentation des commandes d'écriture est une base qui peut nécessiter des ajustements.

**Solutions** :
1. Activez les logs debug
2. Observez les commandes envoyées dans les logs
3. Vérifiez que les trames sont bien envoyées à l'EW11A
4. Consultez [PROTOCOL.md](PROTOCOL.md) pour ajuster les commandes
5. Ouvrez une issue sur GitHub avec vos logs

### Problème : Perte de connexion fréquente

**Symptôme** : L'intégration se déconnecte souvent.

**Solutions** :
1. Vérifiez la qualité du signal WiFi de l'EW11A
2. Rapprochez l'EW11A du routeur ou ajoutez un répéteur
3. Utilisez un canal WiFi moins encombré
4. Vérifiez l'alimentation de l'EW11A (tension stable)

## 📚 Ressources supplémentaires

- [README.md](README.md) - Vue d'ensemble et fonctionnalités
- [PROTOCOL.md](PROTOCOL.md) - Détails du protocole RS-485
- [EXAMPLES.md](EXAMPLES.md) - Exemples d'automatisations
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guide de contribution

## 💬 Support

Si vous rencontrez des problèmes :

1. **Consultez les logs** avec debug activé
2. **Recherchez dans les issues existantes** sur GitHub
3. **Ouvrez une nouvelle issue** avec :
   - Description détaillée
   - Logs pertinents
   - Version HA et version intégration
   - Configuration matérielle

---

**Félicitations !** Votre spa Balboa GS500Z est maintenant connecté à Home Assistant ! 🎉
