# Architecture matérielle — Balboa GS501Z+/VL403

> Dernière mise à jour : avril 2026

---

## 1. Équipement spa

| Composant | Modèle | Détails |
|-----------|--------|---------|
| Carte contrôleur | Balboa GS501Z+ | PCB P/N 22015_B, ©2007 — variante GS500Z |
| Panneau de commande | VL403 | PN 25304 R0, ©2006 — panneau "Lite Digital" |
| Interface panneau | 4 capteurs piézo | Boutons sans contact mécanique |
| Afficheur | 7 segments 3 digits + 1 LED rouge | Affichage température et mode |
| Connecteur panneau | J1 (RJ "Phone Plug") | Protocole propriétaire Balboa |
| Connecteur auxiliaire | J2 (RJ "Phone Plug") | Même protocole que J1 |
| Port diagnostic | J18 (3 pins) | RS-485, lecture seule |
| Chauffage | 5.5 kW (230V, 50Hz) | Limite 16A — heater UNIQUEMENT en pompe LOW |
| Pompe | 2 vitesses (LOW/HIGH) | |
| Blower | Installé | Indépendant, activation manuelle |
| Module IR Balboa | Récepteur 52452 | Branché sur J2, reçoit codes IR 38 kHz |

### Contraintes opérationnelles importantes

- Le chauffage ne fonctionne QU'avec la pompe en vitesse LOW (limite 16A).
- ECO : le heater s'active uniquement pendant les cycles de filtration programmés.
- SL : 0% d'activation du heater.
- La doc Balboa précise : "Panels with backlight should never be plugged into J2."
  Le VL403 n'a PAS de rétroéclairage, il peut donc utiliser J2.
- Il n'y a PAS de bouton MODE physique : le mode se change via une combinaison
  Temp + Lumière (appui simultané) sur le VL403.

---

## 2. Équipement domotique

| Composant | Modèle | Rôle |
|-----------|--------|------|
| Passerelle RS485→WiFi | Elfin EW11A | Lecture RS-485 sur J18, 9600 baud, TCP :8899 |
| Serveur HA | Raspberry Pi 5 + HAOS | Home Assistant, broker MQTT port 1883 |
| ESP8266 #1 (IR) | NodeMCU v2 | Émetteur/récepteur IR (ESPHome) |
| ESP8266 #2 (J2) | NodeMCU 1.0 ESP-12E | Sketch Arduino Balboa_GS501Z_MQTT_v2.ino |
| Prise connectée | Tuya | Coupure alimentation spa |
| Réseau WiFi | 2.4 GHz | Couverture jardin/spa via répéteur |

### Note WiFi

Le signal WiFi au niveau du spa est marginal (~-77 à -78 dBm).
L'ESP8266 est stable uniquement alimenté via le Raspberry Pi 5.

---

## 3. Schéma des connecteurs Balboa

```
GS501Z+ (carte principale)
  |
  +--[J1]-- VL403 (panneau principal — protocole Balboa, matrice courts-circuits)
  |           \-- pin 1 (Gris)   : Bouton TEMP
  |               pin 2 (Orange) : Bouton BLOWER
  |               pin 6 (Jaune)  : Bouton POMPE
  |               pin 7 (Bleu)   : Bouton LUMIÈRE
  |               pin 8 (Marron) : COMMUN (référence)
  |
  +--[J2]-- Module IR Balboa récepteur 52452
  |          (même brochage que J1)
  |
  +--[J18]- EW11A (RS-485, RX-only)
             pin A : RS-485 A
             pin B : RS-485 B
             pin GND : Masse
```

---

## 4. Fonctionnement VL403 — matrice de courts-circuits

**Confirmé par tests physiques (avril 2026).**

Le VL403 n'utilise PAS de bus série multiplexé. Chaque bouton est un simple
court-circuit entre le fil commun (Marron, pin 8) et le fil de la fonction.

| Action | Court-circuit | Pins RJ45 |
|--------|--------------|-----------|
| Blower ON/OFF | Marron + Orange | 8 + 2 |
| Pompe LOW/HIGH | Marron + Jaune | 8 + 6 |
| Lumière ON/OFF | Marron + Bleu | 8 + 7 |
| Temp +/- | Marron + Gris | 8 + 1 |
| Mode (ST→ECO→SL) | Marron + Gris + Bleu | 8 + 1 + 7 |
| Cycles filtration | Marron + Gris + Jaune | 8 + 1 + 6 |

---

## 5. Plan de câblage ESP8266 + optocoupleurs (à réaliser)

**Architecture prévue :**

```
J1 ── splitter RJ45 (mâle → 2 femelles)
           |
           ├── Femelle A → VL403 d'occasion (panneau physique)
           |
           └── Femelle B → 4 optocoupleurs + ESP8266
```

**Optocoupleurs requis :** 1 par fonction (Temp, Blower, Pompe, Lumière).
- TLP281-4 (quad, DIP-16) — solution compacte recommandée
- Ou 4× EL817 individuels (déjà en stock)

Voir `BUS_J1_PROTOCOL.md` pour le tableau de câblage complet.

---

## 6. Matériel disponible (non encore câblé)

| Composant | Quantité | Usage prévu |
|-----------|----------|-------------|
| Optocoupleurs EL817 | 10 | 4 pour les fonctions J1, reste en réserve |
| Résistances 220Ω | kit | Limitation courant LED optocoupleurs |
| Résistances 1kΩ | kit | Pull-up/down |
| Résistances 2kΩ | kit | |
| Résistances 330Ω / 47Ω / 150Ω | kit | Réserve |
| Splitter RJ45 mâle → 2 femelles | 1 | Fourni avec kit IR |
| Câble RJ45 T568B confirmé | 1 | |
| ESP8266 NodeMCU (petit) | 1 | Réserve |
| ESP8266 NodeMCU (grand) | 1 | Préférer pour étiquettes pins lisibles |

### Convention couleurs Dupont

| Couleur | Signal VL403 |
|---------|--------------|
| Blanc   | Gris clavier (TEMP, pin 1) |
| Noir    | GND |
| Bleu    | Bleu clavier (LUMIÈRE, pin 7) |
| Vert    | Jaune clavier (POMPE, pin 6) |
| Orange  | Orange clavier (BLOWER, pin 2) |
| Rouge   | Marron clavier (COMMUN, pin 8) |

---

## 7. Photos PCB VL403

- `docs/photos/vl403-front.jpeg` : Face avant — 4 capteurs piézo, afficheur 7-seg 3 digits, 1 LED rouge
- `docs/photos/vl403-back.jpeg` : Face arrière — PN 25304 R0 ©2006, connecteur RJ, CI principal

---

## 8. VL403 d'occasion (en attente)

Un VL403 d'occasion a été commandé pour les tests du bus J1.
Le VL403 original est actuellement hors service (démonté).
Dès réception : brancher sur J1 via le splitter, puis tester le câblage optocoupleurs.
