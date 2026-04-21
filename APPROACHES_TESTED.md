# Approches testées — Domotisation spa Balboa GS501Z+/VL403

> Ce document recense toutes les pistes explorées, leurs résultats et les raisons
> d'échec ou de succès. Il évite de répéter des investigations déjà concluantes.

---

## 1. RS-485 via EW11A sur J18 — FONCTIONNEL (lecture seule)

**Statut :** Opérationnel depuis septembre 2025.

### Ce qui fonctionne

- Lecture température eau (byte 3)
- Lecture consigne (byte 5)
- Lecture état heater (byte 19 bit 0)
- Lecture état pompe et blower (byte 17)
- Lecture état lumière (byte 20)
- Lecture mode opératoire (byte 23)
- Détection transitions de mode avec garde-fou d'ordre

### Limitation

J18 est RX-only. Il n'est pas possible d'envoyer des commandes via ce port.
L'EW11A connecté sur J1/J2 provoque un cyclage de la pompe (1s ON/1s OFF) —
confirmé par test.

### Scripts

- `reader_spa_state-v5_6_5.py` : ancienne version, détection mode par b7 (peu fiable)
- `reader_spa_state-v5_8_4.py` : version actuelle, b23 + mémoire SL + garde-fou

---

## 2. IR via J2 + ESP8266 — PARTIELLEMENT FONCTIONNEL

**Statut :** Light, Blower, Pump1 fonctionnent. La température NE PEUT PAS être
contrôlée par IR.

### Codes IR confirmés (protocole NEC, 38 kHz, format byte2=~byte1)

| Fonction | byte1 | Résultat |
|----------|-------|----------|
| Light    | `0x60` | Fonctionne |
| Blower   | `0xA0` | Fonctionne |
| Pump1    | `0xC0` | Fonctionne |
| Temp     | —      | N'existe pas |

### Brute force IR — 248 codes testés

- Intervalle entre codes : 2 secondes
- Durée totale : ~8 minutes
- Codes testés : tous les codes NEC possibles (256) moins les 8 déjà connus
- Codes `0x80`, `0x20`, `0x00`, `0x40`, `0xE0` : ignorés par la carte
- **Résultat : aucun code ne modifie la consigne**

**Conclusion confirmée :** Le contrôle de température ne passe PAS par IR sur
le GS501Z+. La télécommande Balboa Dolphin II (J2) contrôle uniquement Light/Blower/Pump.
Le bouton Temp est un toggle directionnel avec affichage LCD et timeout —
incompatible avec un code IR statique.

### Fichiers

- `esphome-tools/balboa-ir-vl403-complet.yaml` : YAML ESPHome codes Pronto
- `esphome-tools/balboa-ir-bruteforce.yaml` : YAML brute force
- `nodered/bruteforce-nodered.json` : flow Node-RED détection automatique

---

## 3. Projet MagnusPer/Balboa-GS510SZ — INCOMPATIBLE (architecture différente)

**Contexte :** Projet Arduino pour GS510SZ avec panneau VL700S.

### Architecture MagnusPer

- ESP8266 sur J1
- 2 optocoupleurs EL816 en porte OR sur PIN3 (Button data multiplexé)
- VL700S : bus série multiplexé, 39 bits display + 3 bits button data, 42 pulses/cycle
- Clock (PIN6) pulse 7 fois par chunk de display data

### Incompatibilités identifiées

- VL700S = bus série multiplexé sur 1 ligne (PIN3)
- **VL403 = matrice de contacts par court-circuit** (voir section 3.7)
- Architecture fondamentalement différente : pas de bus multiplexé sur le VL403
- La librairie `Balboa_GS_Interface` de MagnusPer n'est PAS applicable au VL403
- L'architecture porte OR sur PIN3 n'est pas nécessaire pour le VL403

### Sketch flashé (avant découverte)

`Balboa_GS501Z_MQTT_v2.ino` — compilé Arduino IDE, NodeMCU 1.0 ESP-12E.
WiFi connecté, MQTT connecté, publie `home/spa/status=online`.
Bug corrigé : double définition `filterReadOnly` ligne 339.
**Note :** Ne pas compiler depuis le dossier `libraries` (conflits avec `Balboa_GS_MQTT.ino`).
Ce sketch n'est plus pertinent pour le contrôle VL403.

---

## 4. Projet kgstorm/Balboa-GS100-with-VL260 — ARCHITECTURE DIFFÉRENTE

**Contexte :** GS100 avec VL260 (panneau "Standard").

### Architecture kgstorm

4 lignes boutons SÉPARÉES (PIN 2/3/7/8), chacune avec son optocoupleur.

### Note

Le VL403 est en réalité plus proche de cette architecture (lignes séparées par
fonction) que de MagnusPer. La différence : VL403 utilise un fil commun unique
(pin 8, Marron) au lieu de 4 lignes indépendantes. Voir section 3.7.

---

## 5. Projet ccutrer/balboa_worldwide_app — PROTOCOLE DIFFÉRENT

**Contexte :** Série BP (BP2100, etc.) avec module WiFi intégré.

### Incompatibilité protocolaire

| Paramètre | BP series | GS500Z/GS501Z+ |
|-----------|-----------|----------------|
| Format trame | `7E [length] [channel] [type] [args] [CRC] 7E` | `64 3F 2B [27 bytes]` |
| Baud rate | 115200 | 9600 |
| Interface | WiFi intégré | RS-485 externe |

Totalement incompatible — familles de produits différentes.

---

## 6. Bus J1 avec 2 EL817 en porte OR — ABANDONNÉ

**Statut : ABANDONNÉ** suite à la découverte du fonctionnement réel du VL403 (section 3.7).

### Plan initial (inspiré de MagnusPer)

```
J1 GS501Z+ <-- splitter RJ45 (mâle→2 femelles)
                   |-- femelle A -> VL403 d'occasion
                   `-- femelle B -> ESP8266 via 2 EL817 en porte OR sur PIN3
```

### Pourquoi abandonné

La porte OR sur PIN3 supposait que le VL403 utilise un bus série multiplexé
(comme le VL700S de MagnusPer). La découverte physique du VL403 (section 3.7)
montre qu'il n'y a pas de bus multiplexé — chaque bouton est un simple
court-circuit entre le fil commun (Marron, pin8) et le fil de la fonction.
L'architecture porte OR n'est donc ni nécessaire ni adaptée.

**Plan retenu à la place :** 4 optocoupleurs individuels, un par fonction.
Voir `BUS_J1_PROTOCOL.md`.

---

## 7. DÉCOUVERTE MAJEURE : VL403 = matrice de contacts par court-circuit

**[Confirmé par tests physiques sur le clavier VL403 démonté]**

### Principe de fonctionnement

Le VL403 n'est PAS un bus série multiplexé. Chaque bouton est un **simple
court-circuit** entre le fil MARRON (commun, pin 8) et le fil de la fonction.

Il suffit de fermer ce circuit électriquement (via un optocoupleur ou
transistor) pour simuler un appui bouton.

### Pinout RJ45 VL403 (confirmé)

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

| Action | Court-circuit | Pins |
|--------|--------------|------|
| Blower ON/OFF | Marron + Orange | 8 + 2 |
| Pompe LOW/HIGH | Marron + Jaune | 8 + 6 |
| Lumière ON/OFF | Marron + Bleu | 8 + 7 |
| Temp +/- | Marron + Gris | 8 + 1 |
| **Mode (ST→ECO→SL)** | Marron + Gris + Bleu | 8 + 1 + 7 |
| **Cycles filtration** | Marron + Gris + Jaune | 8 + 1 + 6 |

### Conséquence pour le câblage ESP

- Pas de bus multiplexé à décoder
- Pas de porte OR nécessaire
- 1 optocoupleur par fonction (TLP281-4 ou 4× EL817)
- Combinaisons = activation simultanée de 2 optocoupleurs
- Circuit ouvert = aucune interférence avec le VL403 physique

Voir `BUS_J1_PROTOCOL.md` pour le schéma de câblage complet.

---

## 8. Projets de référence

| Projet | Série | Panneau | Pertinence |
|--------|-------|---------|------------|
| MagnusPer/Balboa-GS510SZ | GS510SZ | VL700S | Architecture bus multiplexé — incompatible VL403 |
| kgstorm/Balboa-GS100-with-VL260 | GS100 | VL260 | Lignes séparées — plus proche VL403 mais pas identique |
| Shuraxxx/Balboa-GS523DZ | GS523DZ | VL801D | Même architecture que MagnusPer |
| ccutrer/balboa_worldwide_app | BP series | TP600+ | Protocole totalement différent |
| netmindz/balboa_GL_ML_spa_control | GL/EL | ML | Autre famille, doc de référence |
| cribskip/esp8266_spa | BP2100 | — | ESP8266+MQTT, protocole incompatible |
