# Approches testees — Domotisation spa Balboa GS501Z+/VL403

> Ce document recense toutes les pistes explorees, leurs resultats et les raisons
> d'echec ou de succes. Il evite de repeter des investigations deja concluantes.

---

## 1. RS-485 via EW11A sur J18 — FONCTIONNEL (lecture seule)

**Statut :** Operationnel depuis septembre 2025.

### Ce qui fonctionne

- Lecture temperature eau (byte 3)
- Lecture consigne (byte 5)
- Lecture etat heater (byte 19 bit 0)
- Lecture etat pompe et blower (byte 17)
- Lecture etat lumiere (byte 20)
- Lecture mode operatoire (byte 23)
- Detection transitions de mode avec garde-fou d'ordre

### Limitation

J18 est RX-only. Il n'est pas possible d'envoyer des commandes via ce port.
L'EW11A connecte sur J1/J2 provoque un cyclage de la pompe (1s ON/1s OFF) —
confirme par test.

### Scripts

- `reader_spa_state-v5_6_5.py` : ancienne version, detection mode par b7 (peu fiable)
- `reader_spa_state-v5_8_4.py` : version actuelle, b23 + memoire SL + garde-fou

---

## 2. IR via J2 + ESP8266 — PARTIELLEMENT FONCTIONNEL

**Statut :** Light, Blower, Pump1 fonctionnent. La temperature NE PEUT PAS etre
controlee par IR.

### Codes IR confirmes (protocole NEC, 38 kHz, format byte2=~byte1)

| Fonction | byte1 | Resultat |
|----------|-------|----------|
| Light    | `0x60` | Fonctionne |
| Blower   | `0xA0` | Fonctionne |
| Pump1    | `0xC0` | Fonctionne |
| Temp     | —      | N'existe pas |

### Brute force IR — 248 codes testes

- Intervalle entre codes : 2 secondes
- Duree totale : ~8 minutes
- Codes testes : tous les codes NEC possibles (256) moins les 8 deja connus
- Codes `0x80`, `0x20`, `0x00`, `0x40`, `0xE0` : ignores par la carte
- **Resultat : aucun code ne modifie la consigne**

**Conclusion confirmee :** Le controle de temperature ne passe PAS par IR sur
le GS501Z+. La telecommande Dolphin II (J2) controle uniquement Light/Blower/Pump.
Le bouton Temp est un toggle directionnel avec affichage LCD et timeout —
incompatible avec un simple code IR statique.

### Fichiers

- `esphome-tools/balboa-ir-vl403-complet.yaml` : YAML ESPHome codes Pronto
- `esphome-tools/balboa-ir-bruteforce.yaml` : YAML brute force
- `nodered/bruteforce-nodered.json` : flow Node-RED detection automatique

---

## 3. Projet MagnusPer/Balboa-GS510SZ — INCOMPATIBLE TEL QUEL

**Contexte :** Projet Arduino pour GS510SZ avec panneau VL700S.

### Architecture MagnusPer

- ESP8266 sur J1
- 2 optocoupleurs EL816 en porte OR sur PIN3 (Button data)
- VL700S a un retro-eclairage (interdit sur J2 selon doc Balboa)
- Protocole bus J1 : clock (PIN6) pulse 7 fois par chunk, 39 bits total + 3 pour
  button data, cycle complet = 42 pulses, BCD -> 7-segments LCD

### Incompatibilites identifiees

- VL700S (MagnusPer) = panneau "Standard" avec boutons mecaniques
- VL403 (notre spa) = panneau "Lite Digital" avec capteurs piezo
- Le protocole de multiplexage des boutons peut differer entre VL700S et VL403
- La librairie `Balboa_GS_Interface` de MagnusPer n'a pas ete validee sur GS501Z+/VL403

### Architecture retenue (similaire MagnusPer)

2 EL817 en porte OR sur PIN3 — meme concept que MagnusPer mais adapte VL403.
Voir `BUS_J1_PROTOCOL.md` pour le plan complet.

### Sketch flash

`Balboa_GS501Z_MQTT_v2.ino` compile via Arduino IDE (COM5, NodeMCU 1.0 ESP-12E).
- WiFi connecte, MQTT connecte
- Publie `home/spa/status=online`
- Bug corrige : double definition `filterReadOnly` ligne 339
- **Important :** ne pas compiler depuis le dossier `libraries` (conflits avec
  `Balboa_GS_MQTT.ino` original)

---

## 4. Projet kgstorm/Balboa-GS100-with-VL260 — ARCHITECTURE DIFFERENTE

**Contexte :** GS100 avec VL260.

### Architecture kgstorm

4 lignes boutons SEPAREES (PIN 2/3/7/8), chacune avec son optocoupleur.

### Incompatibilite

VL403 utilise 1 ligne multiplexee (PIN3) pour tous les boutons, pas 4 lignes
separees. Architecture fondamentalement differente, inutilisable tel quel.

---

## 5. Projet ccutrer/balboa_worldwide_app — PROTOCOLE DIFFERENT

**Contexte :** Serie BP (BP2100, etc.) avec module WiFi integre.

### Incompatibilite protocolaire

| Parametre | BP series | GS500Z/GS501Z+ |
|-----------|-----------|----------------|
| Format trame | `7E [length] [channel] [type] [args] [CRC] 7E` | `64 3F 2B [27 bytes]` |
| Baud rate | 115200 | 9600 |
| Interface | WiFi integre | RS-485 externe |

Totalement incompatible — familles de produits differentes.

---

## 6. Bus J1 avec ESP + 2 EL817 — EN ATTENTE (plan retenu)

**Statut :** En attente de reception du VL403 d'occasion.

### Plan

```
J1 carte GS501Z+ <-- splitter RJ45 (male->2 femelles)
                       |-- femelle A -> VL403 d'occasion
                       `-- femelle B -> ESP8266 avec 2 EL817 en porte OR
```

La porte OR sur PIN3 permet :
- Au VL403 d'envoyer normalement ses signaux boutons
- A l'ESP8266 d'injecter des "appuis" virtuels

Voir `BUS_J1_PROTOCOL.md` pour le schema de cablage complet.

### Bloqueur actuel

VL403 original demonte (hors service). VL403 d'occasion commande, livraison attendue.
Apres reception : test lecture J1 en premier (sans EL817), puis test commande.

---

## 7. Projets de reference

| Projet | Serie | Panneau | Pertinence |
|--------|-------|---------|------------|
| MagnusPer/Balboa-GS510SZ | GS510SZ | VL700S | Le plus proche — architecture porte OR |
| kgstorm/Balboa-GS100-with-VL260 | GS100 | VL260 | Architecture 4 lignes — incompatible |
| Shuraxxx/Balboa-GS523DZ | GS523DZ | VL801D | Meme architecture que MagnusPer |
| ccutrer/balboa_worldwide_app | BP series | TP600+ | Protocole totalement different |
| netmindz/balboa_GL_ML_spa_control | GL/EL | ML | Autre famille, doc de reference |
| cribskip/esp8266_spa | BP2100 | — | ESP8266+MQTT, protocole incompatible |
