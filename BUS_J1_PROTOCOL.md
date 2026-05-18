# Protocole bus J1/J2 et plan de câblage ESP + optocoupleurs

> **Découverte confirmée (avril 2026) :** Le VL403 fonctionne en matrice de
> contacts par court-circuit. L'architecture porte OR (plan MagnusPer) est
> incompatible et a été abandonnée. Voir `APPROACHES_TESTED.md` section 3.6.

---

## 1. Fonctionnement réel du VL403

### Principe : matrice de courts-circuits

Chaque bouton du VL403 est un **simple court-circuit** entre :
- Le fil **COMMUN** (Marron, pin 1, +5 V) — référence commune à tous les boutons
- Le fil de la **fonction** (pin 2, 3, 7 ou 8)

Il n'y a pas de bus série multiplexé, pas de timing complexe, pas de protocole.
Un appui = un contact électrique fermé entre deux fils.

### Pinout RJ45 VL403 (confirmé)

Orientation : connecteur **face contacts visibles**, loquet vers le bas,
pins comptés de **gauche (pin 1)** à **droite (pin 8)**.

| Pin RJ45 | Couleur fil clavier | Signal | Câble T568B |
|----------|--------------------|---------|--------------------|
| 1 | Marron | **COMMUN** (+5 V, référence) | Blanc/Orange |
| 2 | Bleu | Bouton **LUMIÈRE** | Orange |
| 3 | Jaune | Bouton **POMPE** | Blanc/Vert |
| 4 | Vert | GND (probable) | Bleu |
| 5 | Rouge | Data (probable, bus 24-bit) | Blanc/Bleu |
| 6 | Noir | Clock (probable, bus 24-bit) | Vert |
| 7 | Orange | Bouton **BLOWER** | Blanc/Marron |
| 8 | Gris | Bouton **TEMP** | Marron |

Les pins 4/5/6 ne participent pas à la matrice des boutons mais portent
le bus d'affichage 24-bit (cf. `BUS_J1_PROTOCOL.md` §3 / approche kgstorm).

### Combinaisons de boutons

| Action | Court-circuit requis | Pins |
|--------|---------------------|------|
| Lumière ON/OFF | Marron + Bleu | 1 + 2 |
| Pompe LOW/HIGH | Marron + Jaune | 1 + 3 |
| Blower ON/OFF | Marron + Orange | 1 + 7 |
| Temp +/- | Marron + Gris | 1 + 8 |
| **Mode (ST→ECO→SL)** | Marron + Gris + Bleu | 1 + 8 + 2 |
| **Cycles filtration** | Marron + Gris + Jaune | 1 + 8 + 3 |

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
                    Collecteur ─┤──── Pin fonction (2/3/7/8)
                    Émetteur   ─┤──── Pin 1 (Marron, COMMUN +5 V)
```

### Câblage complet (4 fonctions) — pinout briefing

| # | De | Via | À |
|---|-----|-----|---|
| 1 | ESP GPIO_TEMP | 220Ω | Opto-A anode |
| 2 | Opto-A cathode | direct | GND |
| 3 | Opto-A collecteur | direct | RJ45 **pin 8** (Gris, TEMP) |
| 4 | Opto-A émetteur | direct | RJ45 **pin 1** (Marron, COMMUN) |
| 5 | ESP GPIO_BLOWER | 220Ω | Opto-B anode |
| 6 | Opto-B cathode | direct | GND |
| 7 | Opto-B collecteur | direct | RJ45 **pin 7** (Orange, BLOWER) |
| 8 | Opto-B émetteur | direct | RJ45 **pin 1** (Marron, COMMUN) |
| 9 | ESP GPIO_PUMP | 220Ω | Opto-C anode |
| 10 | Opto-C cathode | direct | GND |
| 11 | Opto-C collecteur | direct | RJ45 **pin 3** (Jaune, POMPE) |
| 12 | Opto-C émetteur | direct | RJ45 **pin 1** (Marron, COMMUN) |
| 13 | ESP GPIO_LIGHT | 220Ω | Opto-D anode |
| 14 | Opto-D cathode | direct | GND |
| 15 | Opto-D collecteur | direct | RJ45 **pin 2** (Bleu, LUMIÈRE) |
| 16 | Opto-D émetteur | direct | RJ45 **pin 1** (Marron, COMMUN) |
| 17 | RJ45 pin 1 (Marron) | direct | Émetteurs tous optos (commun) |

**Composants candidats :**
- TLP281-4 (quad optocoupleur DIP-16) — solution compacte recommandée,
  câblage direct anode/cathode + collecteur/émetteur.
- 4× EL817 individuels (disponibles, déjà en stock) — équivalent fonctionnel.
- **HY-M154** : module prêt-à-l'emploi à base de 4× PC817. ⚠ **À valider**
  (cf. encart ci-dessous) avant intégration.
- Résistances 220Ω (déjà en stock) — pour TLP281-4 / EL817 nus ; pas
  nécessaires si on utilise un module avec résistances intégrées.

> ⚠️ **HY-M154 — vérifications préalables au câblage (TODO)**
>
> 1. **Alimentation 5 V côté IN** : le module nécessite **VCC = 5 V** pour
>    déclencher correctement. Un GPIO ESP en 3,3 V ne suffit pas. Sur
>    NodeMCU, alimenter via VIN à 5 V et relier VCC HY-M154 = VIN NodeMCU,
>    GND HY-M154 = GND NodeMCU.
> 2. **Polarité côté sortie (à mesurer)** : certains modules PC817 du
>    commerce sont **cathode-commun côté sortie**, alors que le bus J1
>    VL403 est **anode-commun (+5 V)**. À vérifier au multimètre sur
>    l'exemplaire physique. Si cathode-commun confirmé, soit inverser
>    la logique de commande, soit remplacer par un module anode-commun
>    (ou utiliser TLP281-4 / EL817 nus).
>
> Tant que le point 2 n'est pas mesuré, traiter le HY-M154 comme un
> candidat et garder TLP281-4 ou 4× EL817 comme solution de repli sûre.

### Combinaisons par activation simultanée

Pour simuler Mode (TEMP + LUMIÈRE) :
→ Activer GPIO_TEMP ET GPIO_LIGHT en même temps (< 100ms de décalage).

Pour simuler Cycles filtration (TEMP + POMPE) :
→ Activer GPIO_TEMP ET GPIO_PUMP en même temps.

### Connexion : deux options possibles

**Option A — Splitter sur J1 :**

```
J1 carte GS501Z+ ─── splitter RJ45 (mâle → 2 femelles)
                           │
                           ├── Femelle A → VL403 (panneau physique)
                           │
                           └── Femelle B → Câble vers module opto + ESP8266
```

**Option B — Bus partagé J1/J2 (recommandé, plus simple) :**

```
J1 carte GS501Z+ ── Câble RJ → Module opto (PC817 ×4) ← ESP8266
J2 carte GS501Z+ ── Câble RJ → VL403 (panneau physique)
```

J1 et J2 partageant le même bus interne, il n'est pas nécessaire d'utiliser
un splitter : on dédie un port à l'ESP et l'autre au panneau. Les
optocoupleurs n'interfèrent pas avec le VL403 quand ils ne sont pas
activés (circuit ouvert).

---

## 3. Plan d'intégration progressif

### Étape 1 — Réception VL403 d'occasion

Brancher le VL403 d'occasion sur **J2** (ou sur J1 via splitter).
Vérifier que le spa répond normalement aux appuis physiques.

### Étape 2 — Test lecture passive

Avant de câbler les optocoupleurs, connecter l'ESP en lecture seule :
- RJ45 pin 1 (Marron, COMMUN +5 V) → diviseur 1k/2k → ESP GPIO ref
- RJ45 pin 8 (Gris, TEMP) → diviseur 1k/2k → ESP GPIO (lecture, pull-up)

Vérifier dans le moniteur série que les appuis VL403 physiques sont
détectables (chute sur le fil TEMP quand le bouton est pressé).

> Le bus J1 est en **5 V** : impératif de placer un diviseur de tension
> (1 kΩ + 2 kΩ → ~3,3 V) avant l'entrée GPIO d'un ESP8266/ESP32. Brancher
> directement le +5 V sur un GPIO endommage le MCU.

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
