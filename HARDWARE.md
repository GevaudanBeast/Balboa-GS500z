# Architecture materielle — Balboa GS501Z+/VL403

> Derniere mise a jour : avril 2026

---

## 1. Equipement spa

| Composant | Modele | Details |
|-----------|--------|---------|
| Carte controleur | Balboa GS501Z+ | PCB P/N 22015_B, (c)2007 — variante GS500Z |
| Panneau de commande | VL403 | PN 25304 R0, (c)2006 — panneau "Lite Digital" |
| Interface panneau | 4 capteurs piezo | Boutons sans contact mecanique |
| Afficheur | 7 segments 3 digits + 1 LED rouge | Affichage temperature et mode |
| Connecteur panneau | J1 (RJ "Phone Plug") | Protocole proprietaire Balboa |
| Connecteur auxiliaire | J2 (RJ "Phone Plug") | Meme protocole que J1 |
| Port diagnostic | J18 (3 pins) | RS-485, lecture seule |
| Chauffage | 5.5 kW (230V, 50Hz) | Limite 16A — heater UNIQUEMENT en pompe LOW |
| Pompe | 2 vitesses (LOW/HIGH) | |
| Blower | Installe | Independant, activation manuelle |
| Module IR Balboa | Recepteur 52452 | Branche sur J2, recoit codes IR 38 kHz |

### Contraintes operationnelles importantes

- Le chauffage ne fonctionne QU'avec la pompe en vitesse LOW (limite 16A).
- ECO : le heater s'active uniquement pendant les cycles de filtration programmes.
- SL : 0% d'activation du heater.
- La doc Balboa precise : "Panels with backlight should never be plugged into J2."
  Le VL403 n'a PAS de retro-eclairage, il peut donc utiliser J2.
- Il n'y a PAS de bouton MODE physique : le mode se change via une sequence
  Temp puis Light sur le VL403.

---

## 2. Equipement domotique

| Composant | Modele | Role |
|-----------|--------|------|
| Passerelle RS485->WiFi | Elfin EW11A | Lecture RS-485 sur J18, 9600 baud, TCP :8899 |
| Serveur HA | Raspberry Pi 5 + HAOS | Home Assistant, broker MQTT port 1883 |
| ESP8266 #1 (IR) | NodeMCU v2 | Emetteur/recepteur IR (ESPHome) |
| ESP8266 #2 (J2) | NodeMCU 1.0 ESP-12E | Sketch Arduino Balboa_GS501Z_MQTT_v2.ino |
| Prise connectee | Tuya | Coupure alimentation spa |
| Reseau WiFi | 2.4 GHz | Couverture jardin/spa via repeteur |

### Note WiFi

Le signal WiFi au niveau du spa est marginal (~-77 a -78 dBm).
L'ESP8266 est stable uniquement alimente via le Raspberry Pi 5.

---

## 3. Schema des connecteurs Balboa

```
GS501Z+ (carte principale)
  |
  +--[J1]-- VL403 (panneau principal, protocole Balboa)
  |           \-- PIN3 : Button data (multiplex, 1 ligne pour tous les boutons)
  |               PIN4 : GND
  |               PIN5 : Display data
  |               PIN6 : Clock
  |               PIN7 : 5V
  |
  +--[J2]-- Module IR Balboa recepteur 52452
  |          (meme brochage que J1)
  |
  +--[J18]- EW11A (RS-485, RX-only)
             PIN1 : RS-485 A
             PIN2 : RS-485 B
             PIN3 : GND
```

---

## 4. Materiel disponible (non encore cable)

| Composant | Quantite | Usage prevu |
|-----------|----------|-------------|
| Optocoupleurs EL817 | 10 | Porte OR sur PIN3 (bus J1) |
| Resistances 1K | kit | Pull-up/down |
| Resistances 2K | kit | Diviseur pour PIN5 (Display data, 5V -> 3.3V) |
| Resistances 220R | kit | Limitation courant LED EL817 |
| Resistances 330R | kit | |
| Resistances 47R / 150R | kit | |
| Splitter RJ45 male -> 2 femelles | 1 | Fourni avec kit IR |
| Cable RJ45 T568B confirme | 1 | |
| ESP8266 NodeMCU (petit) | 1 | Reserve |
| ESP8266 NodeMCU (grand) | 1 | Preferer pour etiquettes pins lisibles |

### Convention couleurs Dupont

| Couleur | Signal |
|---------|--------|
| Blanc   | Button data (PIN3) |
| Noir    | GND (PIN4) |
| Bleu    | Display data (PIN5) |
| Vert    | Clock (PIN6) |
| Rouge   | 5V (PIN7) |

---

## 5. Photos PCB VL403

- `docs/photos/vl403-front.jpeg` : Face avant — 4 capteurs piezo, afficheur 7-seg 3 digits, 1 LED rouge
- `docs/photos/vl403-back.jpeg` : Face arriere — PN 25304 R0 (c)2006, connecteur RJ, CI principal

---

## 6. VL403 d'occasion (en attente)

Un VL403 d'occasion a ete commande pour les tests du bus J1.
Il sera branche via le splitter RJ45 (J1 -> splitter -> VL403 d'occasion + ESP8266).
Voir `BUS_J1_PROTOCOL.md` pour le plan de cablage complet.
