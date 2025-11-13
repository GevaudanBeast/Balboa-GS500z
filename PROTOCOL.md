# Protocole RS-485 Balboa GS500Z / VL403

Ce document détaille le protocole de communication RS-485 entre la carte de contrôle Balboa GS500Z et le clavier VL403.

## 📡 Architecture matérielle

```
┌─────────────┐         RS-485         ┌──────────┐
│  GS500Z     │◄─────────────────────►│  VL403   │
│  (Carte)    │      9600 bauds        │ (Clavier)│
└──────┬──────┘                        └──────────┘
       │
       │ RS-485
       ▼
┌─────────────┐
│   EW11A     │
│ (WiFi TCP)  │
└──────┬──────┘
       │
       │ TCP/IP
       ▼
┌─────────────┐
│Home Assistant│
└─────────────┘
```

## 🔌 Configuration RS-485

- **Baud rate** : 9600
- **Data bits** : 8
- **Stop bits** : 1
- **Parity** : None
- **Flow control** : None

## 📦 Format des trames

### Structure générale

Toutes les trames sont encapsulées entre crochets et encodées en hexadécimal :

```
[643F2B...] (54 caractères hex = 27 octets)
```

### Détail des octets

| Byte | Offset | Description | Valeur | Conversion |
|------|--------|-------------|--------|------------|
| 0-2  | 0-2    | Header fixe | `64 3F 2B` | - |
| 3    | 3      | Température eau | `0x00-0xFF` | `× 0.5°C` puis arrondi |
| 4    | 4      | ? | - | - |
| 5    | 5      | Température consigne | `0x00-0xFF` | `× 0.5°C` puis arrondi |
| 6    | 6      | Compteur | Variable | Ignoré |
| 7-18 | 7-18   | Données diverses | - | - |
| 19   | 19     | État chauffage | bit 0 | `0` = OFF, `1` = ON |
| 20-22| 20-22  | ? | - | - |
| 23   | 23     | Mode de fonctionnement | Voir tableau | - |
| 24-26| 24-26  | ? / Checksum ? | - | - |

### Modes de fonctionnement (Byte 23)

| Valeur | Code | Nom | Description |
|--------|------|-----|-------------|
| `0x20` | ST   | Standard | Mode normal |
| `0x00` | ECO  | Économique | Économie d'énergie |
| `0x40` | SL   | Sleep | Mode sommeil |
| `0x60` | UNK  | Transitoire | État intermédiaire (ignoré) |

## 📊 Exemples de trames

### Exemple 1 : Mode ST, 37°C, consigne 38°C, chauffage ON

```
[643F2B4A004C01234567890ABCDEF01020304...]
 │││││ │  │                       │
 │││││ │  └─ Consigne: 0x4C = 76 × 0.5 = 38°C
 │││││ └──── Eau: 0x4A = 74 × 0.5 = 37°C
 ││││└────── Header: 2B
 │││└─────── Header: 3F
 ││└──────── Header: 64
 │└───────── [
 └────────── Début trame

... suite de la trame ...
...│
...└─ Mode: byte[23] = 0x20 = ST
```

Byte 19 = `0x01` → bit 0 = 1 → Chauffage ON

### Exemple 2 : Mode ECO, 35°C, consigne 37°C, chauffage OFF

```
[643F2B460048... byte[19]=0x00 ... byte[23]=0x00 ...]
       │  │                          │
       │  └─ Consigne: 0x48 = 72 × 0.5 = 36°C
       └──── Eau: 0x46 = 70 × 0.5 = 35°C
                                      └─ Mode: 0x00 = ECO
```

Byte 19 = `0x00` → bit 0 = 0 → Chauffage OFF

## 🔄 Logique de validation (fenêtre glissante)

Pour éviter les lectures erronées, l'intégration utilise une fenêtre glissante :

### Principe

```
┌─────────────────────────────────────┐
│  Fenêtre glissante (taille N = 5)  │
├─────────────────────────────────────┤
│  [Trame 1] [Trame 2] [Trame 3]      │
│  [Trame 4] [Trame 5]                │
└─────────────────────────────────────┘
         │
         ▼
  ┌──────────────────┐
  │  Validation :    │
  │  3 dernières     │
  │  trames          │
  │  identiques ?    │
  └──────────────────┘
         │
         ▼
  ┌──────────────────┐
  │  Données stables │
  │  publiées dans   │
  │  Home Assistant  │
  └──────────────────┘
```

### Algorithme

1. Recevoir une nouvelle trame
2. Ajouter à la fenêtre (FIFO, taille max N)
3. Prendre les 3 dernières trames
4. Vérifier la cohérence :
   - Température eau : identique sur les 3 trames
   - Consigne : identique sur les 3 trames
   - Mode : identique sur les 3 trames (hors `UNK`)
   - Chauffage : vote majoritaire (≥2 sur 3)
5. Si cohérent → mettre à jour les données stables
6. Si incohérent → attendre la prochaine trame

### Tolérance pour les modes transitoires

Le mode `0x60` (UNK) est ignoré dans la validation. Exemple :

```
Trame 1 : Mode = SL (0x40)
Trame 2 : Mode = UNK (0x60)  ← Ignoré
Trame 3 : Mode = ECO (0x00)

→ Transition validée : SL → ECO
```

## 🛡️ Garde-fou d'ordre des modes

Le clavier VL403 impose un ordre de transition des modes :

```
    ST (0x20)
     │     ▲
     ▼     │
   ECO (0x00)
     │     ▲
     ▼     │
    SL (0x40)
     └─────┘
```

### Transitions valides

| De  | Vers | Valide |
|-----|------|--------|
| ST  | ECO  | ✅ Oui |
| ST  | SL   | ❌ Non |
| ECO | SL   | ✅ Oui |
| ECO | ST   | ✅ Oui |
| SL  | ST   | ✅ Oui |
| SL  | ECO  | ⚠️ Oui si mode transitoire (0x60) détecté |

### Implémentation

Si le garde-fou est activé, l'intégration bloque les transitions invalides :

```python
# Exemple : demande de passage ST → SL
Current mode: ST
Target mode: SL

→ Transition invalide (bloquée)
→ Log warning
→ Commande non envoyée
```

Pour passer de ST à SL, il faut passer par ECO :
1. `ST → ECO`
2. Attendre validation
3. `ECO → SL`

## 🔧 Commandes d'écriture (injection RS-485)

⚠️ **Cette section décrit la logique théorique. L'implémentation exacte doit être validée sur votre installation.**

### Principe général

Le clavier VL403 envoie des commandes à la carte GS500Z pour :
- Changer la consigne de température
- Changer le mode (bouton mode)

L'intégration doit reproduire ces commandes.

### Commande : Changer la consigne

**Hypothèse** : La trame de commande ressemble à la trame de lecture, mais avec un code spécifique.

```
Structure supposée :
[643F2B??00XX...] où XX = nouvelle consigne

Exemple : Changer la consigne à 39°C
39°C ÷ 0.5 = 78 = 0x4E

Trame : [643F2B00004E...]
              │   │
              │   └─ Consigne (byte 5)
              └───── Indicateur de commande ?
```

**Implémentation actuelle** (`tcp_client.py:build_setpoint_command`) :
```python
def build_setpoint_command(self, setpoint: int) -> bytes:
    setpoint_raw = int(setpoint / TEMP_MULTIPLIER)
    command = bytearray(FRAME_HEADER)
    command.extend([0x00] * (FRAME_LENGTH - 3))
    command[5] = setpoint_raw
    # TODO: Ajouter checksum si nécessaire
    return bytes(command)
```

### Commande : Changer le mode

**Hypothèse** : Le mode est changé par un "appui bouton" virtuel qui cycle à travers les modes.

```
Cycle des modes :
ST → ECO → SL → ST → ...

Pour aller de ST à SL :
- 2 appuis : ST → ECO → SL

Pour aller de ECO à ST :
- 1 appui : ECO → SL → ST
ou
- 2 appuis : ECO → SL → ST
```

**Implémentation actuelle** (`tcp_client.py:build_mode_command`) :
```python
def build_mode_command(self, current_mode: str, target_mode: str) -> Optional[bytes]:
    mode_sequence = ["ST", "ECO", "SL"]
    current_idx = mode_sequence.index(current_mode)
    target_idx = mode_sequence.index(target_mode)
    presses = (target_idx - current_idx) % len(mode_sequence)

    # TODO: Implémenter la commande de "presse bouton"
    command = bytearray(FRAME_HEADER)
    command.extend([0x00] * (FRAME_LENGTH - 3))
    command[23] = 0x01  # Indicateur bouton mode ?
    return bytes(command)
```

### À faire pour finaliser les commandes

1. **Capturer les trames réelles du VL403** :
   - Utiliser un analyseur RS-485
   - Observer les trames envoyées quand on change la consigne
   - Observer les trames envoyées quand on change le mode

2. **Implémenter le checksum** (si nécessaire) :
   - Analyser si les trames ont un checksum
   - Implémenter le calcul (CRC, XOR, somme ?)

3. **Tester et ajuster** :
   - Envoyer les commandes au GS500Z
   - Observer la réponse
   - Ajuster le format si nécessaire

## 🧪 Débogage

### Activer les logs détaillés

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.balboa_gs500z: debug
```

### Observer les trames brutes

Les logs debug affichent :
- Toutes les trames reçues (hex)
- Les trames parsées (valeurs décodées)
- Les validations de la fenêtre glissante
- Les commandes envoyées

Exemple de log :
```
[custom_components.balboa_gs500z.tcp_client] Parsed frame: {
  'water_temp': 37,
  'setpoint': 38,
  'mode': 'ST',
  'heater_on': True,
  'raw_mode_byte': 32,
  'raw_frame': '643f2b4a004c...'
}
```

### Tester la connexion TCP

```bash
# Depuis la ligne de commande
telnet <IP_EW11A> 8899

# Vous devriez voir les trames arriver :
[643F2B...]
[643F2B...]
...
```

## 📚 Références

- [EIA-485 (Wikipedia)](https://fr.wikipedia.org/wiki/EIA-485)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Balboa Documentation](https://www.balboawatergroup.com/)

## 🤝 Contribuer

Si vous découvrez des détails supplémentaires sur le protocole, n'hésitez pas à :
1. Ouvrir une issue
2. Partager vos captures de trames
3. Proposer une pull request

---

**Note importante** : Ce document est basé sur l'analyse empirique du protocole. Certains détails peuvent nécessiter des ajustements selon votre configuration matérielle.
