# Protocole bus J1/J2 et plan de câblage ESP + optocoupleurs

> **Découverte confirmée (avril 2026) :** Le VL403 fonctionne en matrice de
> contacts par court-circuit. L'architecture porte OR (plan MagnusPer) est
> incompatible et a été abandonnée. Voir `APPROACHES_TESTED.md` section 3.6.

---

## 1. Fonctionnement réel du VL403

### Principe : matrice de courts-circuits

Chaque bouton du VL403 est un **simple court-circuit** entre :
- Le fil **COMMUN** (Marron, pin 8) — référence commune à tous les boutons
- Le fil de la **fonction** (pin 1, 2, 6 ou 7)

Il n'y a pas de bus série multiplexé, pas de timing complexe, pas de protocole.
Un appui = un contact électrique fermé entre deux fils.

### Pinout RJ45 VL403 (confirmé)

Orientation : connecteur face à soi, ergot de verrouillage en bas.

| Pin RJ45 | Couleur fil clavier | Signal | Câble T568B |
|----------|--------------------|---------|--------------------|
| 1 | Gris | Bouton **TEMP** | Blanc/Orange |
| 2 | Orange | Bouton **BLOWER** | Orange |
| 3 | Noir | Non utilisé (boutons) | Blanc/Vert |
| 4 | Rouge | Non utilisé (boutons) | Bleu |
| 5 | Vert | Non utilisé (boutons) | Blanc/Bleu |
| 6 | Jaune | Bouton **POMPE** | Vert |
| 7 | Bleu | Bouton **LUMIÈRE** | Blanc/Marron |
| 8 | Marron | **COMMUN** (référence) | Marron |

### Combinaisons de boutons

| Action | Court-circuit requis | Pins |
|--------|---------------------|------|
| Blower ON/OFF | Marron + Orange | 8 + 2 |
| Pompe LOW/HIGH | Marron + Jaune | 8 + 6 |
| Lumière ON/OFF | Marron + Bleu | 8 + 7 |
| Temp +/- | Marron + Gris | 8 + 1 |
| **Mode (ST→ECO→SL)** | Marron + Gris + Bleu | 8 + 1 + 7 |
| **Cycles filtration** | Marron + Gris + Jaune | 8 + 1 + 6 |

Pour les combinaisons (Mode, Cycles), deux optocoupleurs sont activés simultanément.

---

## 2. Architecture d'intégration ESP8266 + optocoupleurs

### Principe

Un optocoupleur par fonction. Le collecteur/émetteur court-circuite le fil commun
avec le fil de la fonction. L'ESP commande le côté LED de l'optocoupleur.

```
ESP8266                    Optocoupleur              RJ45 → J1
───────                    ────────────              ─────────
GPIO → [220Ω] → Anode ─┐
                        ├─ LED ─┤
                GND ────┘       │
                                │
                    Collecteur ─┤──── Pin fonction (1/2/6/7)
                    Émetteur   ─┤──── Pin 8 (Marron, COMMUN)
```

### Câblage complet (4 fonctions)

| # | De | Via | À |
|---|-----|-----|---|
| 1 | ESP GPIO_TEMP | 220Ω | Opto-A anode |
| 2 | Opto-A cathode | direct | GND |
| 3 | Opto-A collecteur | direct | RJ45 pin 1 (Gris, TEMP) |
| 4 | Opto-A émetteur | direct | RJ45 pin 8 (Marron, COMMUN) |
| 5 | ESP GPIO_BLOWER | 220Ω | Opto-B anode |
| 6 | Opto-B cathode | direct | GND |
| 7 | Opto-B collecteur | direct | RJ45 pin 2 (Orange, BLOWER) |
| 8 | Opto-B émetteur | direct | RJ45 pin 8 (Marron, COMMUN) |
| 9 | ESP GPIO_PUMP | 220Ω | Opto-C anode |
| 10 | Opto-C cathode | direct | GND |
| 11 | Opto-C collecteur | direct | RJ45 pin 6 (Jaune, POMPE) |
| 12 | Opto-C émetteur | direct | RJ45 pin 8 (Marron, COMMUN) |
| 13 | ESP GPIO_LIGHT | 220Ω | Opto-D anode |
| 14 | Opto-D cathode | direct | GND |
| 15 | Opto-D collecteur | direct | RJ45 pin 7 (Bleu, LUMIÈRE) |
| 16 | Opto-D émetteur | direct | RJ45 pin 8 (Marron, COMMUN) |
| 17 | RJ45 pin 8 (Marron) | direct | Émetteurs tous optos (commun) |

**Composants recommandés :**
- TLP281-4 (quad optocoupleur, 4 canaux en 1 boîtier DIP-16) — solution compacte
- Ou 4× EL817 individuels (disponibles, déjà en stock)
- Résistances 220Ω (déjà en stock)

### Combinaisons par activation simultanée

Pour simuler Mode (TEMP + LUMIÈRE) :
→ Activer GPIO_TEMP ET GPIO_LIGHT en même temps (< 100ms de décalage).

Pour simuler Cycles filtration (TEMP + POMPE) :
→ Activer GPIO_TEMP ET GPIO_PUMP en même temps.

### Connexion au J1 via splitter RJ45

```
J1 carte GS501Z+ ─── splitter RJ45 (mâle → 2 femelles)
                           │
                           ├── Femelle A → VL403 d'occasion (panneau physique)
                           │
                           └── Femelle B → Câble vers optocoupleurs + ESP8266
```

Le VL403 et l'ESP sont en parallèle sur le même bus J1. Les optocoupleurs
n'interfèrent pas avec le VL403 quand ils ne sont pas activés (circuit ouvert).

---

## 3. Plan d'intégration progressif

### Étape 1 — Réception VL403 d'occasion

Brancher le VL403 d'occasion sur J1 via le splitter (femelle A).
Vérifier que le spa répond normalement aux appuis physiques.

### Étape 2 — Test lecture passive

Avant de câbler les optocoupleurs, connecter l'ESP en lecture seule :
- RJ45 pin 8 (Marron) → ESP GND
- RJ45 pin 1 (Gris) → ESP GPIO (lecture, avec résistance pull-up)

Vérifier dans le moniteur série que les appuis VL403 physiques sont
détectables (changement d'état sur le fil TEMP).

### Étape 3 — Câblage complet optocoupleurs

Monter les 4 optocoupleurs selon le tableau de câblage section 2.
Tester chaque fonction individuellement depuis l'ESP.

### Étape 4 — Intégration Home Assistant

Finaliser l'entité `climate` HA :
- Lecture : RS-485 via EW11A/J18 (température, mode, heater)
- Écriture : ESP + optocoupleurs via J1 (consigne Temp, changement Mode)

---

## 4. Durée des impulsions (à calibrer)

Les durées d'impulsion pour un appui VL403 reconnu sont à déterminer
expérimentalement. Point de départ :

| Type d'action | Durée impulsion estimée |
|---------------|-------------------------|
| Appui court (toggle) | 100–300 ms |
| Maintien Temp (incrément) | 500 ms par degré |
| Combinaison (Mode/Cycle) | 100–300 ms, simultané |

Ces valeurs seront affinées lors des tests avec le VL403 d'occasion.

---

## 5. Ce qui a été abandonné

L'architecture porte OR sur PIN3 (plan initial inspiré de MagnusPer/VL700S)
a été abandonnée car le VL403 n'utilise pas de bus série multiplexé.
Voir `APPROACHES_TESTED.md` section 3.6 pour les détails.

---

## 6. Références

- `APPROACHES_TESTED.md` section 3.7 : découverte du fonctionnement VL403
- `HARDWARE.md` : matériel disponible (EL817, résistances, splitter, ESP8266)
- `PROTOCOL.md` : protocole RS-485 J18 (lecture)
- `IR_CODES.md` : codes IR pour Light/Blower/Pump (alternative IR)
