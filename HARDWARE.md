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
| Port diagnostic | J18 (3 pins) | RS-485, lecture seule (via module TTL485) |
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
| Module TTL→RS-485 | TTL485 (MAX485) | Adaptation niveaux pour lecture J18 |
| Module optocoupleur | PC817 ×4 (TLP281-4 ou HY-M154 ⚠) | Simulation des boutons côté J1 (écriture) |
| Serveur HA | Raspberry Pi 5 + HAOS | Home Assistant, broker MQTT port 1883 |
| ESP8266 #1 (IR) | NodeMCU v2 | Émetteur/récepteur IR (ESPHome) |
| ESP8266 #2 (J1) | NodeMCU 1.0 ESP-12E | Pilote du module optocoupleur (boutons VL403) |
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
  +--[J1]-- ESP8266 + module optocoupleur (PC817 ×4) — simulation boutons (écriture)
  |           \-- pin 1 (Marron) : COMMUN (+5 V référence)
  |               pin 2 (Bleu)   : Bouton LUMIÈRE
  |               pin 3 (Jaune)  : Bouton POMPE
  |               pin 7 (Orange) : Bouton BLOWER
  |               pin 8 (Gris)   : Bouton TEMP
  |
  +--[J2]-- VL403 (panneau physique — matrice courts-circuits)
  |          (même brochage et même bus que J1 ; les deux coexistent ;
  |           module IR Balboa retiré pour libérer J2)
  |
  +--[J18]- TTL485 (MAX485) → EW11A (RS-485, RX-only)
             pin A : RS-485 A
             pin B : RS-485 B
             pin GND : Masse
```

> **Note J1/J2 :** J1 et J2 partagent le même bus. La documentation Balboa
> déconseille uniquement les panneaux **rétroéclairés** branchés sur J2 seul.
> Dans cette configuration "fractionnée" (ESP sur J1 + VL403 non rétroéclairé
> sur J2), les deux cohabitent sans conflit.

---

## 4. Fonctionnement VL403 — matrice de courts-circuits

**Confirmé par tests physiques (avril 2026).**

> **Convention de numérotation RJ45** : connecteur face contacts visibles,
> loquet vers le bas, pins comptés **de gauche (pin 1) à droite (pin 8)**.
> Le COMMUN (+5 V) est sur **pin 1 (Marron)**. Les fonctions sortent sur
> pin 2 / 3 / 7 / 8.

Le VL403 n'utilise PAS de bus série multiplexé. Chaque bouton est un simple
court-circuit entre le fil commun (Marron, pin 1) et le fil de la fonction.

| Action | Court-circuit | Pins RJ45 |
|--------|--------------|-----------|
| Lumière ON/OFF | Marron + Bleu | 1 + 2 |
| Pompe LOW/HIGH | Marron + Jaune | 1 + 3 |
| Blower ON/OFF | Marron + Orange | 1 + 7 |
| Temp +/- | Marron + Gris | 1 + 8 |
| Mode (ST→ECO→SL) | Marron + Gris + Bleu | 1 + 8 + 2 |
| Cycles filtration | Marron + Gris + Jaune | 1 + 8 + 3 |

---

## 5. Plan de câblage ESP8266 + optocoupleurs

> Firmware ESPHome valide : `esphome-tools/balboa-spa-control/balboa-spa-control-v1.5.3.yaml`.
> Voir le README associé pour le câblage TTL485 + TLP281-4 détaillé et la liste des entités exposées.

### Affectation GPIO (firmware v1.5.3)

| Fonction | GPIO ESP | Carte NodeMCU | Pin RJ45 VL403 |
|---|---|---|---|
| BLOWER | GPIO14 | D5 | pin 7 (Orange) |
| POMPE  | GPIO12 | D6 | pin 3 (Jaune) |
| TEMP   | GPIO13 | D7 | pin 8 (Gris) |
| LIGHT  | **GPIO15** | **D8** | pin 2 (Bleu) |
| RS-485 RX (TTL485 TXD) | GPIO4 | D2 | — (cote J18) |

> ⚠️ **Ne pas utiliser GPIO16 (D0)** pour les sorties optocoupleur :
> domaine RTC, transitoire HIGH au boot → déclenche le bouton à chaque
> redémarrage (cf. FIX-1 v1.5.3).



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

| Couleur Dupont | Signal VL403 |
|----------------|--------------|
| Blanc   | Gris clavier (TEMP, pin 8) |
| Noir    | GND |
| Bleu    | Bleu clavier (LUMIÈRE, pin 2) |
| Vert    | Jaune clavier (POMPE, pin 3) |
| Orange  | Orange clavier (BLOWER, pin 7) |
| Rouge   | Marron clavier (COMMUN, pin 1) |

---

## 7. Photos PCB VL403

- `docs/photos/vl403-front.jpeg` : Face avant — 4 capteurs piézo, afficheur 7-seg 3 digits, 1 LED rouge
- `docs/photos/vl403-back.jpeg` : Face arrière — PN 25304 R0 ©2006, connecteur RJ, CI principal

---

## 8. VL403 d'occasion (en attente)

Un VL403 d'occasion a été commandé pour les tests du bus J1.
Le VL403 original est actuellement hors service (démonté).
Dès réception : brancher sur J2 (port libéré par le retrait du module IR),
garder l'ESP + module optocoupleur sur J1, et tester.

---

## 9. Points critiques d'alimentation

### Module HY-M154 (PC817) — 5 V obligatoires côté IN

Le module HY-M154 nécessite **5 V** côté entrée (IN) pour déclencher de
manière fiable l'optocoupleur PC817. Une sortie GPIO ESP en 3,3 V est
**insuffisante** pour activer la LED interne de manière propre.

**Montage recommandé sur NodeMCU :**

- Alimenter le NodeMCU via la broche **VIN à 5 V** (USB ou alimentation
  externe régulée 5 V).
- La broche **VIN** du NodeMCU expose alors le 5 V vers le module HY-M154.
- Câbler les GPIO ESP sur les entrées IN1..IN4 du module (le module utilise
  un niveau logique compatible TTL avec son propre transistor de
  commutation côté LED, alimenté par VCC=5 V).
- VCC module = 5 V (VIN), GND module = GND NodeMCU (référence commune).

Sans 5 V, les commandes peuvent fonctionner partiellement mais de façon
non fiable (déclenchements manqués, doubles appuis, etc.).

> ⚠️ **TODO câblage HY-M154 — vérification multimètre à faire avant
> intégration définitive.** Certains modules PC817 du commerce sont
> **cathode-commun côté sortie**, alors que le bus J1 VL403 est
> **anode-commun (+5 V)**. Si c'est le cas, la logique de commande doit
> être inversée ou le module remplacé par une variante anode-commun.
> À mesurer sur l'exemplaire physique avant câblage et à documenter ici.
> Tant que cette mesure n'est pas faite, traiter le HY-M154 comme un
> candidat et non comme la solution validée — TLP281-4 ou 4× EL817
> individuels restent l'option de repli sûre.

---

## 10. Choix de l'ESP

| MCU | Statut | Notes |
|-----|--------|-------|
| **ESP8266 NodeMCU v2** | Validé | Configuration de référence, poll RS-485 à 500 ms stable |
| **ESP32-WROOM-32 (dual-core)** | Recommandé si upgrade | Cœur dédié au parsing RS-485 temps réel, WiFi sur l'autre cœur |
| **ESP32-C6 (mono-core)** | À éviter pour ce cas | Mono-cœur : risque de problèmes de timing en combinant parsing RS-485 + WiFi |

Pour la lecture RS-485 seule (J18), un ESP32 quelconque convient.
Pour combiner lecture temps réel + WiFi + commande J1, préférer un
ESP32 dual-core.

---

## 11. FAQ — choix matériels

### TTL485 + module optocoupleur — les deux sont nécessaires ?

Oui, ils répondent à deux besoins complémentaires :

- **TTL485 sur J18** → télémétrie RS-485 en **lecture seule** (température,
  mode, pompe, chauffage, cycle de filtration…).
- **Module optocoupleur (PC817 ×4) sur J1** → **simulation de boutons**,
  c'est-à-dire le **contrôle en écriture** (consigne, mode, etc.).

J18 ne permet pas d'écrire ; J1 ne fournit pas la télémétrie. Les deux
modules sont donc complémentaires, pas redondants.

### Peut-on mettre l'optocoupleur sur J2 ?

Oui — J1 et J2 partagent le même bus. Une configuration éprouvée :

- **J1** : ESP + module optocoupleur (écriture / simulation boutons)
- **J2** : panneau VL403 physique (lecture / contrôle manuel)

Les deux cohabitent sans conflit. L'avertissement Balboa ("Panels with
backlight should never be plugged into J2") ne s'applique qu'aux
panneaux **rétroéclairés** — le VL403 n'a pas de rétroéclairage.

### Carte personnalisée kgstorm — compatible ?

Le projet kgstorm utilise une approche matérielle différente : panneau
**VL260** (côté haut de gamme) et lignes de boutons séparées sur une
carte personnalisée. Sa carte Lovelace est conçue autour de cette
intégration.

Cette intégration-ci expose des entités **ESPHome / HA standard**
(`climate`, `binary_sensor`, etc.) : n'importe quelle carte Lovelace
supportant capteurs et boutons fonctionne. Adapter la carte kgstorm
demande quelques retouches, mais reste possible.
