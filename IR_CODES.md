# Codes IR — Balboa GS501Z+/VL403

> Protocole NEC, 38 kHz. Format : byte1 + ~byte1 (complement bit a bit).
> Module IR Balboa recepteur 52452 branche sur J2.

---

## 1. Codes confirmes

| Fonction | byte1 | Code NEC complet | Statut |
|----------|-------|------------------|--------|
| Light    | `0x60` | NEC 0x60 | Fonctionne |
| Blower   | `0xA0` | NEC 0xA0 | Fonctionne |
| Pump1    | `0xC0` | NEC 0xC0 | Fonctionne |
| Temp     | —      | N/A | N'existe PAS |

---

## 2. Brute force — resultats complets

**Date :** septembre/octobre 2025
**Methode :** envoi de tous les codes NEC possibles, intervalle 2 secondes
**Duree :** ~8 minutes (248 codes x 2s)

### Codes inexistants / ignores par la carte

Codes qui ne declenchent aucune reaction :
`0x00`, `0x20`, `0x40`, `0x80`, `0xE0`

### Conclusion

**Aucun code IR ne controle la consigne de temperature.**

La telecommande Balboa Dolphin II (concue pour J2) gere uniquement :
- Light (eclairage)
- Blower (soufflerie)
- Pump (pompe)

Le bouton Temp sur le VL403 est un toggle directionnel avec :
- Affichage LCD interactif
- Timeout (~5 secondes sans action)
- Logique d'incrementation/decrementation

Ce mecanisme est fondamentalement incompatible avec un code IR statique.

---

## 3. Configuration ESPHome

Les codes Pronto pour les 3 fonctions confirmees sont documentes dans :
- `esphome-tools/balboa-ir-vl403-complet.yaml`

Le YAML inclut :
- Scripts centralises pour chaque fonction
- Sequences de filtration (combinaisons Light + Pump)
- Detection de l'etat courant via RS-485

---

## 4. Implication pour le projet

Puisque la temperature ne peut pas etre controlee par IR :

- **Light / Blower / Pump1** : controlables via IR (ESP8266 #1)
- **Temperature / Mode** : uniquement via bus J1 (plan EL817) ou manuellement

Voir `BUS_J1_PROTOCOL.md` et `APPROACHES_TESTED.md` pour les alternatives.
