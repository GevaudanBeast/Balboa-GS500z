# Protocole bus J1/J2 et plan de cablage EL817

> Ce document decrit le protocole proprietaire Balboa sur J1/J2 et le plan
> d'integration via 2 optocoupleurs EL817 en porte OR.

---

## 1. Protocole bus J1/J2

J1 et J2 utilisent le meme protocole proprietaire Balboa (PAS du RS-485).

### Brochage RJ (T568B confirme)

| PIN | Signal | Description |
|-----|--------|-------------|
| 1   | —      | Ne jamais connecter |
| 2   | —      | Ne jamais connecter |
| 3   | Button data | Ligne multiplexee — TOUS les boutons (1 seule ligne) |
| 4   | GND    | Masse |
| 5   | Display data | Donnees afficheur 7 segments |
| 6   | Clock  | Horloge synchronisation |
| 7   | 5V     | Alimentation |

### Protocole (reference MagnusPer/VL700S, a valider sur VL403)

- Horloge (PIN6) : pulse 7 fois par chunk de display data
- Total : 39 bits display data + 3 bits button data = 42 pulses par cycle
- Format affichage : BCD -> segments 7-segments LCD

**Important :** Ces timings sont ceux du VL700S (MagnusPer). Le VL403 utilise
des capteurs piezo au lieu de boutons mecaniques — les timings ou le multiplexage
peuvent differer. A valider experimentalement.

### Principe Button data (PIN3)

Tous les boutons du VL403 sont multiplexes sur 1 seule ligne (PIN3).
Les appuis sont encodes en position dans le cycle de 42 pulses.

---

## 2. Plan de cablage — Porte OR avec 2 EL817

### Architecture

```
J1 GS501Z+ <-- splitter RJ45 (male -> 2 femelles)
                  |
                  +-- femelle A --> VL403 d'occasion (panneau physique)
                  |
                  +-- femelle B --> ESP8266 via 2 EL817 en porte OR
```

La porte OR sur PIN3 permet :
- Au VL403 de fonctionner normalement (ses signaux passent via EL817-A)
- A l'ESP8266 d'injecter des signaux virtuels (via EL817-B)
- L'isolation optique protege l'ESP et le bus

### Schema porte OR EL817

```
PIN7 (5V) ----+---- EL817-A collecteur (broche 4)
              |
              +---- EL817-B collecteur (broche 4)
              |
              +---- PIN3 (Button data) du splitter

VL403 PIN3 --> EL817-A anode (broche 1)
EL817-A cathode (broche 2) --> GND
EL817-A emetteur (broche 3) --> GND

ESP D8/GPIO15 --> [220R] --> EL817-B anode (broche 1)
EL817-B cathode (broche 2) --> GND
EL817-B emetteur (broche 3) --> GND
```

### Tableau de cablage complet

| # | De | Via | A | Dupont |
|---|-----|-----|---|--------|
| 1 | Splitter PIN7 (5V) | direct | EL817-A broche 4 (collecteur) | — |
| 2 | EL817-A broche 4 | direct | EL817-B broche 4 (collecteur) | — |
| 3 | EL817-A+B broche 4 | direct | Splitter PIN3 (Button data) | Blanc |
| 4 | VL403 PIN3 | direct | EL817-A broche 1 (anode) | — |
| 5 | EL817-A broche 2 (cathode) | direct | GND | Noir |
| 6 | EL817-A broche 3 (emetteur) | direct | GND | Noir |
| 7 | ESP D8/GPIO15 | 220R | EL817-B broche 1 (anode) | Blanc |
| 8 | EL817-B broche 2 (cathode) | direct | GND | Noir |
| 9 | EL817-B broche 3 (emetteur) | direct | GND | Noir |
| 10 | Splitter PIN4 (GND) | direct | ESP GND | Noir |
| 11 | Splitter PIN5 (Display data) | 2kR | ESP D2/GPIO4 | Bleu |
| 12 | Splitter PIN6 (Clock) | 1kR | ESP D1/GPIO5 | Vert |
| 13 | Splitter PIN7 (5V) | direct | ESP VIN | Rouge |

### Points de vigilance

- **PIN1 et PIN2 du splitter : ne jamais connecter.**
- Le collecteur EL817 est alimente en 5V (PIN7 RJ), PAS en 3.3V ESP.
  (meme choix que MagnusPer — le bus fonctionne en logique 5V)
- PIN3 du splitter doit etre coupee et recablee via les 2 EL817 pour isoler
  correctement VL403 et ESP.
- PIN5 (Display data, 5V) passe par un diviseur 2kR avant l'ESP (3.3V max).
- PIN6 (Clock, 5V) passe par une resistance 1kR avant l'ESP.

---

## 3. Plan d'integration progressif

### Etape 1 — Reception VL403 d'occasion

Brancher le VL403 d'occasion sur J1 via le splitter RJ45 (femelle A).
Verifier que le panneau principal (VL403 original, si disponible) continue de
fonctionner normalemen. Si le VL403 original est hors service, utiliser
uniquement le VL403 d'occasion.

### Etape 2 — Lecture J1 (sans EL817)

Monter l'ESP8266 en lecture seule :
- PIN4 (GND) -> ESP GND
- PIN5 (Display data) -> [2kR] -> ESP D2/GPIO4
- PIN6 (Clock) -> [1kR] -> ESP D1/GPIO5
- PIN7 (5V) -> ESP VIN

Objectif : verifier que les donnees display remontent et que les appuis VL403
physiques sont visibles dans le moniteur serie. Valider les timings par rapport
a la reference MagnusPer (VL700S).

### Etape 3 — Commande J1 avec EL817

Ajouter les 2 EL817 selon le schema section 2.
Tester l'injection d'un appui virtuel Temp.

### Etape 4 — Integration Home Assistant

Si la commande J1 fonctionne :
- RS-485 (J18/EW11A) : lecture temperature, mode, heater, pompe
- Bus J1 (ESP8266 + EL817) : commandes Temp et mode
- Finaliser l'entite `climate` HA avec controle bidirectionnel

### Plan B — Si bus J1 ne fonctionne pas avec VL403

Garder le monitoring RS-485 + IR pour Light/Blower/Pump1.
La consigne reste modifiable manuellement via le VL403 physique
(cas acceptable, la consigne est rarement modifiee).

---

## 4. References

- [MagnusPer/Balboa-GS510SZ](https://github.com/MagnusPer/Balboa-GS510SZ) :
  reference implementation bus J1 (VL700S, architecture similaire)
- `APPROACHES_TESTED.md` section 3 : details incompatibilites VL700S/VL403
- `HARDWARE.md` : materiel disponible (EL817, resistances, splitter, ESP8266)
- `PROTOCOL.md` : protocole RS-485 J18 (lecture)
