# Protocole RS-485 Balboa GS500Z/GS501Z+ — Documentation technique

> **Statut :** Confirmé par captures live (GS501Z+/VL403, 01/10/2025).
> J18 est en **lecture seule**. Les commandes d'ecriture ne sont pas implementees.

---

## 1. Architecture de communication

```
GS501Z+ (carte)
     |
     |-- J1/J2 (RJ "Phone Plug")  --> protocole proprietaire Balboa (PAS RS-485)
     |                                 VL403 (afficheur) + module IR Balboa
     |
     +-- J18 (3 pins)             --> RS-485, lecture seule, 9600 baud
                                       |
                                  EW11A (WiFi)
                                       |
                                  TCP :8899
                                       |
                                  Home Assistant
```

**Important :**
- J1/J2 utilisent le protocole proprietaire Balboa (bus clavier), pas du RS-485.
- Brancher un EW11A sur J1/J2 provoque un cyclage de la pompe (1s ON/1s OFF).
- J18 est le seul port RS-485, et il est en reception seule (RX-only).

---

## 2. Configuration RS-485 (J18 via EW11A)

| Parametre   | Valeur |
|-------------|--------|
| Baud rate   | 9600   |
| Data bits   | 8      |
| Stop bits   | 1      |
| Parity      | None   |
| Flow ctrl   | None   |
| Mode EW11A  | TCP Server, port 8899 |

---

## 3. Format des trames

### 3.1 Structure generale

Les trames sont encapsulees entre crochets, encodees en hexadecimal :

```
[643F2B xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx]
 ^^^^^^                                                                             ^
 Header (3 bytes fixes)                                                  27 bytes = 54 chars hex
```

- **Header fixe :** `64 3F 2B` (bytes 0-2)
- **Longueur :** 27 octets, soit 54 caracteres hexadecimaux entre `[` et `]`

### 3.2 Mapping des octets (confirme)

| Byte | Role | Formule / Valeurs | Statut |
|------|------|-------------------|--------|
| 0-2  | Header fixe | `64 3F 2B` | Confirme |
| 3    | Temperature eau | `valeur * 0.5` -> degC, arrondi entier | Confirme |
| 4    | Inconnu | — | Non identifie |
| 5    | Consigne temperature | `valeur * 0.5` -> degC, arrondi entier | Confirme |
| 6    | Compteur de trame | Incremente, ignore | Confirme |
| 7    | Mode (obsolete) | `0x12`=SL, `0x18`=ST — peu fiable | Non utilise (remplace par b23) |
| 8-16 | Inconnus | — | Non identifies |
| 17   | Pompe / Blower | Voir tableau 3.3 | Confirme |
| 18   | Contexte heater/mode | Combine avec b23 | Confirme |
| 19   | Etat chauffage | **bit 0 = indicateur universel** | Confirme |
| 20   | Lumiere | `0x02` ou `0x03` = ON | Confirme |
| 21   | Lumiere (variante) | Complementaire b20 | Confirme |
| 22   | Inconnu | — | Non identifie |
| 23   | Mode operatoire | Voir tableau 3.4 | Confirme |
| 24-26| Inconnus / checksum ? | — | Non identifies |

### 3.3 Byte 17 — Pompe et Blower

| Masque | Valeur | Signification |
|--------|--------|---------------|
| `b17 & 0x80` | `0x80` | Blower ON |
| `b17 & 0x80` | `0x00` | Blower OFF |
| `b17 & 0x7F` | `0x01` ou `0x08` | Pompe 1 vitesse LOW |
| `b17 & 0x7F` | `0x02` ou `0x18` | Pompe 1 vitesse HIGH |
| `b17 & 0x7F` | `0x00` | Pompe OFF |

### 3.4 Byte 19 — Etat chauffage (confirme)

Le **bit 0** est l'indicateur universel du chauffage, valable dans tous les modes :

| Valeur b19 | bit 0 | Heater | Mode | Contexte |
|------------|-------|--------|------|----------|
| `0x41`     | 1     | ON     | ST   | Chauffage actif en Standard |
| `0xC1`     | 1     | ON     | ST   | Variante ST |
| `0xC2`     | 0     | OFF    | ECO  | Idle en Economique |
| `0x44`     | 0     | OFF    | SL   | Idle en Sommeil |
| `0xC4`     | 0     | OFF    | SL   | Variante idle SL |
| `0x42`     | 0     | OFF    | —    | Transitoire ECO->SL |

Detection : `heater_on = bool(b19 & 0x01)`

### 3.5 Byte 23 — Mode operatoire (confirme)

| Valeur | Masque `b23 & 0x60` | Mode | Nom | Description |
|--------|---------------------|------|-----|-------------|
| `0x20` | `0x20` | ST  | Standard  | Mode normal, heater actif selon besoin |
| `0x00` | `0x00` | ECO | Economique | Heater uniquement pendant filtration |
| `0x40` | `0x40` | SL  | Sommeil   | 0% activation heater |
| `0x60` | `0x60` | UNK | Transitoire | Etat intermediaire, ignore |

**Attention :** En mode SL stable, b23 peut revenir a `0x00` apres stabilisation
(identique a ECO). Voir section 5 pour l'algorithme de detection avec memoire SL.

---

## 4. Exemples de trames

### Mode ST, 37.0°C eau, consigne 38.0°C, chauffage ON

```
Byte 3  = 0x4A (74) -> 74 * 0.5 = 37.0°C eau
Byte 5  = 0x4C (76) -> 76 * 0.5 = 38.0°C consigne
Byte 19 = 0x41      -> bit0=1 -> Heater ON
Byte 23 = 0x20      -> ST
```

### Mode ECO, 35.0°C eau, chauffage OFF

```
Byte 3  = 0x46 (70) -> 70 * 0.5 = 35.0°C eau
Byte 19 = 0xC2      -> bit0=0 -> Heater OFF
Byte 23 = 0x00      -> ECO
```

### Mode SL stable (b23 retombe a 0x00)

```
Byte 19 = 0x44      -> bit0=0 -> Heater OFF
Byte 23 = 0x00      -> ECO apparent, MAIS memoire SL active -> interprete comme SL
```

---

## 5. Algorithme de detection de mode v5.8.4

### 5.1 Detection primaire par byte 23

```python
def strict_mode_from_b23(b23):
    if (b23 & 0x60) == 0x60: return "UNK"   # transitoire
    if (b23 & 0x40) == 0x40: return "SL"
    if (b23 & 0x20) == 0x20: return "ST"
    if b23 == 0x00:          return "ECO"
    return "UNK"
```

### 5.2 Memoire SL (probleme de stabilisation)

Apres plusieurs minutes en mode SL, b23 peut passer de `0x40` a `0x00`.
Sans memoire, cela serait interprete a tort comme ECO.

**Parametres :**
- Fenetre : 120 secondes
- Seuil : 2 observations minimum de b23=`0x40` dans la fenetre

**Algorithme :**
1. Chaque fois que b23=`0x40` est confirme dans la fenetre glissante -> enregistrer le timestamp
2. Si la fenetre glissante retourne "ECO" (b23=`0x00`) MAIS >= 2 timestamps SL dans les 120s -> retourner "SL"
3. La memoire expire naturellement si b23 reste a `0x00` plus de 120s

### 5.3 Garde-fou d'ordre VL403

Le panneau VL403 impose un cycle physique de transition :

```
ST --> ECO --> SL --> ST --> ...
```

Transitions valides :

| De  | Vers | Valide |
|-----|------|--------|
| ST  | ECO  | Oui    |
| ST  | SL   | Non    |
| ECO | SL   | Oui    |
| ECO | ST   | Oui    |
| SL  | ST   | Oui    |
| SL  | ECO  | Non (sauf si UNK transitoire detecte) |

Si le garde-fou est active, les transitions invalides sont bloquees avec un log warning.

### 5.4 Fenetre glissante de validation

Pour eviter les faux positifs :
- Conserver les N dernieres trames (defaut : 5)
- Valider sur les 3 dernieres trames consecutives
- Temperatures : identiques sur les 3 trames
- Mode : identique sur les 3 trames (hors UNK)
- Heater : vote majoritaire (>= 2/3)
- Pompe / Blower / Lumiere : vote majoritaire (>= 2/3)

### 5.5 Algorithme alternatif (3 regles statistiques)

Si la detection par b23 est insuffisante, cet algorithme statistique peut complementer :

1. Heater ON > 50% du temps sur la fenetre -> ST
2. Heater OFF + ecart eau/consigne > 6°C -> SL
3. Heater OFF + ecart eau/consigne < 4°C -> ECO

---

## 6. Transitions de mode (observations terrain)

Captures realisees le 01/10/2025, GS501Z+/VL403.

### ST -> ECO

```
Avant    : b19=0x41, b23=0x20 (ST, heater ON)
Transition : b19=0x41 -> 0xC1 -> 0xC2 ; b23=0x20 -> 0x00
Apres    : b19=0xC2, b23=0x00 (ECO, heater OFF)
```

### ECO -> SL

```
Avant    : b19=0xC2, b23=0x00 (ECO)
Transition : b19=0xC2 -> 0x42 -> 0x44 ; b23=0x00 -> 0x40
Apres    : b19=0x44, b23=0x40 puis 0x00 (SL stable)
```

### SL -> ST

```
Avant    : b19=0x44, b23=0x00 (SL masque)
Transition : b19=0x44 -> 0xC1 ; b23=0x00 -> 0x40 -> 0x60 -> 0x20
Apres    : b19=0xC1, b23=0x20 (ST)
```

---

## 7. Etat des commandes d'ecriture

> **J18 est en LECTURE SEULE.** Aucune commande ne peut etre envoyee via J18/EW11A.

Le seul moyen de controler le spa (consigne, mode) est via le bus J1 (protocole
proprietaire Balboa). Voir `BUS_J1_PROTOCOL.md` pour le plan d'integration.

Les methodes `build_setpoint_command()` et `build_mode_command()` dans
`tcp_client.py` sont des stubs qui levent `NotImplementedError`.

---

## 8. Debogage

### Activer les logs debug

```yaml
# configuration.yaml Home Assistant
logger:
  default: info
  logs:
    custom_components.balboa_gs500z: debug
```

### Tester la connexion TCP

```bash
telnet <IP_EW11A> 8899
# Les trames defilent :
# [643F2B...]
# [643F2B...]
```

### Format de log (frame parsee)

```
[custom_components.balboa_gs500z.tcp_client] Parsed frame: {
  'water_temp': 37, 'setpoint': 38, 'mode': 'ST', 'heater_on': True,
  'pump1_state': 'low', 'blower_on': False, 'light_on': False,
  '_b19': 65, '_b23': 32, 'raw_frame': '643f2b4a004c...'
}
```

---

## 9. References

- Manuel GS500Z (PDF) : schemas connecteurs J1/J2/J18, DIP switches
- Manuel VL403 (PDF) : documentation panneau
- [MagnusPer/Balboa-GS510SZ](https://github.com/MagnusPer/Balboa-GS510SZ) : reference architecture bus J1
- `HARDWARE.md` : architecture materielle complete
- `BUS_J1_PROTOCOL.md` : protocole bus J1/J2 et plan de cablage EL817
