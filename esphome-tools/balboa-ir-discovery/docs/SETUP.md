# Guide d'Installation - Balboa IR Discovery Tool

Ce guide vous accompagne pas à pas pour installer et configurer l'outil de découverte de commandes IR pour votre spa Balboa GS500Z.

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Matériel nécessaire](#matériel-nécessaire)
3. [Câblage du matériel](#câblage-du-matériel)
4. [Installation du logiciel](#installation-du-logiciel)
5. [Configuration](#configuration)
6. [Premier démarrage](#premier-démarrage)
7. [Dépannage](#dépannage)

---

## 🔧 Prérequis

### Logiciels requis

- **Home Assistant** installé et fonctionnel
- **ESPHome** installé (via add-on ou standalone)
- **Éditeur de texte** (VS Code, Notepad++, nano, etc.)

### Connaissances recommandées

- ✅ Utilisation de base de Home Assistant
- ✅ Connexion à un réseau Wi-Fi
- ✅ Câblage électronique de base (GPIO, GND, VCC)
- ⚠️ Pas besoin de connaissances en programmation !

---

## 🛠️ Matériel nécessaire

### Composants obligatoires

| Composant | Quantité | Prix approximatif | Lien exemple |
|-----------|----------|-------------------|--------------|
| **ESP32 DevKit** | 1 | ~5-10€ | ESP32-WROOM-32 |
| **Émetteur IR** (LED IR 940nm) | 1 | ~1€ | TSAL6200, VS1838B |
| **Résistance 100Ω** | 1 | ~0.10€ | Pour protéger la LED IR |
| **Transistor NPN** (2N2222 ou BC547) | 1 | ~0.20€ | Pour amplifier le signal IR |
| **Câbles Dupont** | 5-10 | ~2€ | Mâle-Femelle et Mâle-Mâle |
| **Breadboard** | 1 | ~2€ | Pour prototypage |
| **Alimentation USB** | 1 | ~5€ | Micro-USB 5V 1A minimum |

### Composants optionnels (recommandés)

| Composant | Usage | Prix approximatif |
|-----------|-------|-------------------|
| **Récepteur IR** (TSOP38238) | Capturer des codes IR existants | ~1€ |
| **Adaptateur RS-485** (MAX485) | Validation automatique future | ~2€ |
| **LED visible** | Indicateur visuel d'émission | ~0.10€ |
| **Boîtier plastique** | Protection du montage final | ~3€ |

### Où acheter ?

- 🇫🇷 **France** : Amazon.fr, Gotronic, Kubii
- 🇪🇺 **Europe** : AliExpress, Banggood, eBay
- 🏪 **Magasins locaux** : Boulanger (parfois), magasins d'électronique

---

## 🔌 Câblage du matériel

### Schéma de base (Émetteur IR uniquement)

```
ESP32                         Émetteur IR
┌─────────────┐              ┌──────────────┐
│             │              │              │
│   GPIO4 ────┼──────┬───────┤ Anode (+)    │
│             │      │       │              │
│             │    [100Ω]    └──────────────┘
│             │      │             │
│   GND ──────┼──────┴─────────────┘
│             │
│   5V/3.3V ──┼─── (alimentation)
└─────────────┘
```

### Schéma amélioré avec transistor (recommandé pour meilleure portée)

```
ESP32                    Transistor         Émetteur IR
┌─────────────┐         (2N2222)          ┌──────────────┐
│             │            ┌─E             │              │
│   GPIO4 ────┼────[1kΩ]──┤                │              │
│             │            │ B          ┌──┤ Anode (+)    │
│             │            C─┘          │  │              │
│             │             │         [100Ω]└──────────────┘
│   5V ───────┼─────────────┼───────────┤        │
│             │             │           │        │
│   GND ──────┼─────────────┴───────────┴────────┘
└─────────────┘
```

### Schéma complet (avec récepteur IR)

```
ESP32                    Émetteur IR              Récepteur IR
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│             │         │              │         │              │
│   GPIO4 ────┼─────────┤ Anode (+)    │         │   OUT ───────┼──── GPIO5
│             │         │              │         │              │
│   GPIO5 ────┼─────────┴──────────────┴─────────┤   VCC ───────┼──── 3.3V
│             │                                   │              │
│   3.3V ─────┼───────────────────────────────────┤   GND ───────┼──── GND
│             │                                   │              │
│   GND ──────┼───────────────────────────────────┴──────────────┘
└─────────────┘
```

### Tableau de connexion

| ESP32 Pin | Composant | Notes |
|-----------|-----------|-------|
| **GPIO4** | Émetteur IR | Via résistance 100Ω ou transistor |
| **GPIO5** | Récepteur IR (OUT) | Optionnel - pour capturer des codes |
| **3.3V** | Récepteur IR (VCC) | Ne PAS utiliser 5V pour le récepteur ! |
| **GND** | GND (tous composants) | Masse commune |
| **5V** | Émetteur IR (si transistor) | Pour plus de puissance |

### ⚠️ Points d'attention

1. **LED IR** : Elle émet de la lumière invisible ! Utilisez votre caméra de smartphone pour vérifier qu'elle émet (apparaît violet/blanc sur l'écran).
2. **Polarité** : Les LED IR ont une polarité ! Patte longue = Anode (+), patte courte = Cathode (-).
3. **Résistance** : Toujours mettre une résistance en série avec la LED pour éviter de la griller.
4. **Distance** : Avec un simple montage, portée ~2-5m. Avec transistor, portée ~5-10m.
5. **Angle** : Pointez la LED IR directement vers le récepteur IR du spa.

---

## 💻 Installation du logiciel

### Étape 1 : Préparer ESPHome

#### Via Home Assistant (recommandé)

1. Ouvrez Home Assistant
2. Allez dans **Paramètres** → **Modules complémentaires**
3. Cliquez sur **Boutique des modules complémentaires**
4. Recherchez **ESPHome**
5. Cliquez sur **Installer**
6. Une fois installé, cliquez sur **Démarrer**
7. Activez **Afficher dans la barre latérale**

#### Standalone (alternatif)

```bash
# Installation avec pip
pip3 install esphome

# Vérification
esphome version
```

### Étape 2 : Télécharger les fichiers

#### Option A : Cloner le dépôt Git

```bash
cd ~
git clone https://github.com/VotreUsername/Balboa-GS500z.git
cd Balboa-GS500z/esphome-tools/balboa-ir-discovery
```

#### Option B : Téléchargement manuel

1. Téléchargez les fichiers depuis GitHub
2. Créez un dossier `balboa-ir-discovery`
3. Placez-y les fichiers :
   - `balboa-ir-discovery.yaml`
   - `secrets.yaml.example`
   - `docs/` (dossier)

### Étape 3 : Copier les fichiers vers ESPHome

#### Via Home Assistant (interface web)

1. Ouvrez **ESPHome** dans la barre latérale
2. Cliquez sur **+ NEW DEVICE** (bas à droite)
3. Cliquez sur **SKIP** (on va utiliser notre fichier)
4. Téléversez le fichier `balboa-ir-discovery.yaml`

#### Via ligne de commande

```bash
# Si ESPHome installé standalone
cp balboa-ir-discovery.yaml /config/esphome/
cp secrets.yaml.example /config/esphome/secrets.yaml
```

---

## ⚙️ Configuration

### Étape 1 : Créer le fichier secrets.yaml

1. Copiez `secrets.yaml.example` vers `secrets.yaml`
2. Ouvrez `secrets.yaml` avec un éditeur de texte
3. Remplissez vos informations :

```yaml
# Configuration Wi-Fi
wifi_ssid: "VotreSSID"           # Nom de votre réseau Wi-Fi
wifi_password: "VotreMotDePasse"  # Mot de passe Wi-Fi

# Clé de chiffrement API (générez-en une)
api_encryption_key: "AbCdEfGhIjKlMnOpQrStUvWxYz012345=="

# Mot de passe OTA
ota_password: "votre_mot_de_passe"
```

### Étape 2 : Générer une clé API

```bash
# Linux/Mac
openssl rand -base64 32

# Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

Copiez le résultat dans `secrets.yaml` pour `api_encryption_key`.

### Étape 3 : Adapter les GPIO (si nécessaire)

Ouvrez `balboa-ir-discovery.yaml` et vérifiez la section `substitutions` :

```yaml
substitutions:
  # GPIO Pins - Adaptez selon votre ESP32
  ir_transmitter_pin: "GPIO4"    # Pin de l'émetteur IR
  ir_receiver_pin: "GPIO5"       # Pin du récepteur IR (optionnel)
  rs485_tx_pin: "GPIO17"         # Pin TX RS-485 (optionnel)
  rs485_rx_pin: "GPIO16"         # Pin RX RS-485 (optionnel)
```

**Modifiez uniquement si votre câblage est différent !**

### Étape 4 : Vérifier la configuration

#### Via ESPHome Dashboard

1. Ouvrez ESPHome
2. Trouvez votre appareil `balboa-ir-discovery`
3. Cliquez sur les **3 points** → **Validate**
4. Attendez la validation (doit afficher "Valid")

#### Via ligne de commande

```bash
esphome config balboa-ir-discovery.yaml
```

Si vous voyez "INFO Configuration is valid!", c'est bon !

---

## 🚀 Premier démarrage

### Étape 1 : Compiler le firmware

#### Via ESPHome Dashboard

1. Cliquez sur votre appareil `balboa-ir-discovery`
2. Cliquez sur **INSTALL**
3. Sélectionnez **Plug into this computer** (première fois)
4. Connectez l'ESP32 via USB
5. Sélectionnez le port série (COM3, /dev/ttyUSB0, etc.)
6. Attendez la compilation et le téléversement (~5-10 min)

#### Via ligne de commande

```bash
# Compilation
esphome compile balboa-ir-discovery.yaml

# Téléversement via USB
esphome upload balboa-ir-discovery.yaml

# Ou tout en une fois
esphome run balboa-ir-discovery.yaml
```

### Étape 2 : Vérifier les logs

Pendant et après le téléversement, surveillez les logs :

```
[21:45:12][I][app:102]: ESPHome version 2024.x.x
[21:45:13][I][app:104]: Compilation date: ...
[21:45:14][I][wifi:123]: Connecting to 'VotreSSID'...
[21:45:16][I][wifi:456]: WiFi connected! IP: 192.168.1.123
[21:45:17][I][api:789]: API server started
[21:45:18][I][main:100]: ==========================================
[21:45:18][I][main:101]: Balboa IR Discovery Tool - Démarrage
[21:45:18][I][main:102]: ==========================================
```

Si vous voyez ces messages, **c'est bon !** ✅

### Étape 3 : Ajouter à Home Assistant

1. Ouvrez Home Assistant
2. Allez dans **Paramètres** → **Appareils et services**
3. Cliquez sur **+ AJOUTER UNE INTÉGRATION**
4. Recherchez **ESPHome**
5. Sélectionnez votre appareil `balboa-ir-discovery` (détecté automatiquement)
6. Entrez la clé API (celle de `secrets.yaml`)
7. Cliquez sur **SOUMETTRE**

Vous devriez maintenant voir l'appareil avec tous ses contrôles !

### Étape 4 : Test de base

1. Allez dans **Aperçu** de Home Assistant
2. Trouvez la carte `Balboa IR Discovery`
3. Cliquez sur le bouton **🎯 Test Manuel**
4. Regardez les logs dans ESPHome :

```
[21:50:00][I][IR_SEND]: Envoi code 0x00000000 (protocole: 0)
```

Si vous voyez ce message, l'émetteur IR fonctionne ! ✅

---

## 🔍 Dépannage

### Problème : ESP32 ne se connecte pas au Wi-Fi

**Solution 1** : Vérifiez le SSID et mot de passe dans `secrets.yaml`

**Solution 2** : Réinitialisez le Wi-Fi
```yaml
# Ajoutez dans wifi:
wifi:
  # ... config existante
  manual_ip:
    static_ip: 192.168.1.100
    gateway: 192.168.1.1
    subnet: 255.255.255.0
```

**Solution 3** : Utilisez le point d'accès de secours
1. L'ESP32 crée un réseau `Balboa IR Discovery Fallback`
2. Mot de passe : `balboa123456`
3. Connectez-vous avec votre smartphone
4. Allez sur `http://192.168.4.1`
5. Configurez le Wi-Fi

### Problème : Home Assistant ne détecte pas l'appareil

**Solution 1** : Vérifiez que l'ESP32 est sur le même réseau que HA

**Solution 2** : Ajoutez manuellement
1. **Paramètres** → **Appareils et services**
2. **+ AJOUTER UNE INTÉGRATION** → **ESPHome**
3. Entrez l'IP de l'ESP32 manuellement
4. Entrez la clé API

### Problème : LED IR ne s'allume pas

**Solution 1** : Vérifiez avec une caméra de smartphone (LED IR = invisible à l'œil nu)

**Solution 2** : Vérifiez la polarité de la LED (patte longue = +)

**Solution 3** : Testez la LED avec une résistance directement sur 3.3V :
```
3.3V ──[100Ω]──[LED IR]── GND
```

### Problème : Portée IR trop courte

**Solution 1** : Utilisez un transistor pour amplifier le signal (voir schéma)

**Solution 2** : Utilisez plusieurs LEDs IR en parallèle

**Solution 3** : Réduisez la distance et assurez-vous qu'il n'y a pas d'obstacle

### Problème : Logs illisibles ou trop rapides

**Solution 1** : Réduisez le niveau de log
```yaml
logger:
  level: INFO  # ou WARN
```

**Solution 2** : Consultez les logs dans ESPHome :
- Cliquez sur **LOGS** dans le dashboard ESPHome

---

## 📞 Support et aide

- **Documentation ESPHome** : https://esphome.io
- **Forum Home Assistant** : https://community.home-assistant.io
- **GitHub Issues** : (lien vers votre dépôt)
- **Discord** : (si vous avez un serveur)

---

## ✅ Checklist finale

Avant de passer à l'utilisation, vérifiez que :

- [ ] ESP32 connecté au Wi-Fi
- [ ] Appareil visible dans Home Assistant
- [ ] Logs ESPHome affichent le démarrage correct
- [ ] LED IR fonctionne (visible sur caméra)
- [ ] Boutons visibles dans Home Assistant
- [ ] Test manuel fonctionne (vérifiez les logs)
- [ ] LED IR pointe vers le récepteur du spa

**Si tout est ✅, passez au [Guide d'Utilisation](USAGE.md) !**
