# Codes IR Découverts - Balboa GS500Z

**Utilisez ce fichier comme template pour documenter vos découvertes.**

---

## 📋 Informations sur le matériel

| Information | Valeur |
|-------------|--------|
| **Modèle de spa** | Balboa GS500Z |
| **Numéro de série** | (optionnel) |
| **Version firmware** | (si connu) |
| **Date de fabrication** | (si connu) |
| **Télécommande incluse** | VL403 / Autre |

---

## 🔧 Configuration de découverte

| Paramètre | Valeur |
|-----------|--------|
| **ESP32 utilisé** | ESP32-WROOM-32 / Autre |
| **LED IR** | 940nm / Autre |
| **Distance ESP-Spa** | X mètres |
| **Protocole(s) testé(s)** | NEC, RC5, RC6, etc. |
| **Plage de codes** | 0x00000000 à 0x0000FFFF |
| **Date de découverte** | AAAA-MM-JJ |

---

## ✅ Codes Validés

### Protocole : NEC

| Code (Hex) | Code (Décimal) | Fonction | Effet observé | Confirmé ? |
|------------|----------------|----------|---------------|------------|
| 0x00000042 | 66 | Changement de mode | ST → ECO | ✅ |
| 0x00000043 | 67 | Changement de mode | ECO → SL | ✅ |
| 0x00000044 | 68 | Changement de mode | SL → ST | ✅ |
| 0x00000050 | 80 | Température + | Augmente de 1°C | ✅ |
| 0x00000051 | 81 | Température - | Diminue de 1°C | ✅ |
| 0x00000060 | 96 | Chauffage | Toggle ON/OFF | ⚠️ |
| | | | | |
| | | | | |

**Légende** :
- ✅ = Confirmé (testé 3+ fois)
- ⚠️ = Partiel (fonctionne parfois)
- ❌ = Ne fonctionne plus

### Protocole : RC5

| Code (Hex) | Code (Décimal) | Fonction | Effet observé | Confirmé ? |
|------------|----------------|----------|---------------|------------|
| | | | | |
| | | | | |

### Protocole : Samsung

| Code (Hex) | Code (Décimal) | Fonction | Effet observé | Confirmé ? |
|------------|----------------|----------|---------------|------------|
| | | | | |

---

## 📝 Notes et observations

### Comportements particuliers

- **Code 0x00000060** : Semble activer/désactiver le chauffage, mais pas toujours. Peut dépendre de la température actuelle.
- **Codes séquentiels** : Les codes 0x50, 0x51, 0x52 semblent liés à la température.
- **Délai de réponse** : Le spa met environ 1-2 secondes pour réagir.

### Conditions de test

- **Température de l'eau** : 35°C
- **Mode initial** : Standard (ST)
- **Heure du test** : Journée (14h-16h)
- **Météo** : Ensoleillé / Couvert / Pluie

### Difficultés rencontrées

- Difficulté à distinguer certains effets subtils
- Portée IR limitée à ~2m (résolu avec transistor)
- Quelques codes semblent ne fonctionner que dans certains états

---

## 🔍 Codes suspects (à re-tester)

| Code (Hex) | Raison |
|------------|--------|
| 0x00000061 | Possible variante du code 0x60 |
| 0x00000070 | Effet non identifié (bip sonore ?) |
| 0x00000080 | Spa a réagi mais impossible de déterminer l'effet |

---

## 🎯 Plages intéressantes identifiées

| Plage (Hex) | Description |
|-------------|-------------|
| 0x00000040 - 0x0000004F | Changements de mode |
| 0x00000050 - 0x0000005F | Contrôle de température |
| 0x00000060 - 0x0000006F | Contrôle du chauffage |
| 0x00000080 - 0x0000008F | Fonction inconnue |

**Recommandation** : Ces plages méritent un test approfondi avec des variations d'état du spa.

---

## 🧪 Tests de validation

### Test 1 : Changement de mode ST → ECO

| Étape | Action | Résultat attendu | Résultat obtenu |
|-------|--------|------------------|-----------------|
| 1 | Mettre le spa en mode ST | Mode = ST | ✅ |
| 2 | Envoyer code 0x00000042 | Mode passe à ECO | ✅ |
| 3 | Répéter 3 fois | Même résultat | ✅ |

**Conclusion** : Code 0x00000042 validé pour ST → ECO

### Test 2 : Augmentation de température

| Étape | Action | Résultat attendu | Résultat obtenu |
|-------|--------|------------------|-----------------|
| 1 | Noter température actuelle (T1) | T1 = 35°C | ✅ |
| 2 | Envoyer code 0x00000050 | T2 = T1 + 1°C | ✅ (36°C) |
| 3 | Répéter 3 fois | Température augmente de 1°C à chaque fois | ✅ |

**Conclusion** : Code 0x00000050 validé pour augmentation température

---

## 📊 Statistiques de découverte

| Métrique | Valeur |
|----------|--------|
| **Total codes testés** | 256 |
| **Codes validés** | 8 |
| **Taux de réussite** | 3.1% |
| **Temps total** | 9 minutes |
| **Protocole le plus efficace** | NEC |

---

## 🚀 Intégration Home Assistant

### Configuration ESPHome pour utiliser les codes

```yaml
# Exemple d'utilisation des codes découverts
remote_transmitter:
  pin: GPIO4
  carrier_duty_percent: 50%

button:
  # Mode ECO
  - platform: template
    name: "Spa - Mode ECO"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x0042

  # Mode Standard
  - platform: template
    name: "Spa - Mode Standard"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x0044

  # Température +
  - platform: template
    name: "Spa - Température +"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x0050

  # Température -
  - platform: template
    name: "Spa - Température -"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x0051
```

---

## 🤝 Partage avec la communauté

### Format JSON des codes découverts

```json
{
  "spa_model": "Balboa GS500Z",
  "discovery_date": "2024-01-15",
  "protocol": "NEC",
  "codes": [
    {
      "code_hex": "0x00000042",
      "code_dec": 66,
      "function": "mode_eco",
      "description": "Switch to ECO mode from ST",
      "confirmed": true
    },
    {
      "code_hex": "0x00000050",
      "code_dec": 80,
      "function": "temp_increase",
      "description": "Increase temperature by 1°C",
      "confirmed": true
    }
  ]
}
```

### Où partager

- **GitHub Issues** : Créez une issue avec vos résultats
- **Home Assistant Forum** : Postez dans la section ESPHome
- **Discord** : Communauté Balboa/ESPHome

---

## 📚 Ressources utiles

- [Guide d'utilisation complet](../docs/USAGE.md)
- [Documentation ESPHome Remote Transmitter](https://esphome.io/components/remote_transmitter.html)
- [Protocoles IR supportés](https://esphome.io/components/remote_transmitter.html#remote-transmitter-protocols)

---

## ✍️ Auteur de la découverte

| Information | Valeur |
|-------------|--------|
| **Nom/Pseudo** | Votre nom |
| **GitHub** | @votrepseudo |
| **Contact** | (optionnel) |
| **Localisation** | France / Autre |

---

## 📅 Historique des modifications

### Version 1.0 - AAAA-MM-JJ

- Découverte initiale de 8 codes NEC
- Tests de validation effectués
- Configuration ESPHome créée

### Version 1.1 - AAAA-MM-JJ

- Ajout de 3 nouveaux codes
- Confirmation des codes suspects
- Amélioration de la documentation

---

**N'hésitez pas à partager vos découvertes avec la communauté ! 🎉**
