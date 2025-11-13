# 🚀 Démarrage rapide - 5 minutes

Guide simple pour connecter votre spa Balboa GS500Z à Home Assistant.

---

## 📦 Ce dont vous avez besoin

✅ Un spa Balboa GS500Z
✅ Un module WiFi **EW11A** (RS-485 vers WiFi)
✅ Home Assistant installé
✅ HACS installé (optionnel mais recommandé)

---

## Étape 1️⃣ : Brancher le module EW11A

### Matériel nécessaire
- Module EW11A
- Alimentation 5V pour l'EW11A
- 2 fils pour le branchement RS-485 (A et B)

### Branchement

```
Spa GS500Z                    EW11A
┌──────────┐                 ┌──────────┐
│          │                 │          │
│  RS485-A │────────────────►│ A (RS+)  │
│  RS485-B │────────────────►│ B (RS-)  │
│          │                 │          │
│  GND     │────────────────►│ GND      │
└──────────┘                 └──────────┘
                                  │
                                  └─► Alimentation 5V
```

**⚠️ Important** : Branchez l'EW11A sur les **connecteurs RS-485** du spa, **PAS sur les connecteurs du clavier VL403** (risque de panne).

---

## Étape 2️⃣ : Configurer l'EW11A

### Connectez-vous au module

1. **Cherchez le WiFi** : Réseau `EW11A_XXXXX`
2. **Mot de passe par défaut** : `12345678`
3. **Ouvrez votre navigateur** : http://192.168.4.1

### Paramètres à configurer

| Paramètre | Valeur |
|-----------|--------|
| **Mode** | TCP Server |
| **Baud Rate** | 9600 |
| **Data Bits** | 8 |
| **Stop Bits** | 1 |
| **Parity** | None |
| **Port** | 8899 |

### Connecter au WiFi de votre maison

1. Dans l'interface EW11A, allez dans **WiFi Settings**
2. Sélectionnez votre réseau WiFi
3. Entrez le mot de passe
4. **Notez l'adresse IP** attribuée (ex: `192.168.1.50`)

---

## Étape 3️⃣ : Installer l'intégration dans Home Assistant

### Via HACS (recommandé)

1. Ouvrez **HACS** dans Home Assistant
2. Allez dans **Intégrations**
3. Cliquez sur **⋮** (menu) → **Dépôts personnalisés**
4. Ajoutez : `https://github.com/GevaudanBeast/Balboa-GS500z`
5. Recherchez **"Balboa GS500Z"**
6. Cliquez sur **Télécharger**
7. **Redémarrez** Home Assistant

### Installation manuelle

1. Téléchargez le dossier `custom_components/balboa_gs500z`
2. Copiez-le dans `config/custom_components/`
3. **Redémarrez** Home Assistant

---

## Étape 4️⃣ : Ajouter le spa dans Home Assistant

1. Allez dans **Paramètres** → **Appareils et services**
2. Cliquez sur **+ Ajouter une intégration**
3. Recherchez **"Balboa GS500Z Spa"**
4. Entrez :
   - **Adresse IP** : celle de l'EW11A (ex: `192.168.1.50`)
   - **Port** : `8899`
5. Cliquez sur **Soumettre**

✅ **C'est fait !** Vous verrez apparaître :
- `climate.spa` - Température et mode du spa
- `binary_sensor.spa_heater` - État du chauffage

---

## Étape 5️⃣ : Créer votre première carte

Copiez-collez cette configuration dans une nouvelle carte Lovelace :

```yaml
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.spa
    name: Mon Spa

  - type: entities
    entities:
      - entity: binary_sensor.spa_heater
        name: Chauffage
      - type: attribute
        entity: climate.spa
        attribute: current_temperature
        name: Température actuelle
      - type: attribute
        entity: climate.spa
        attribute: temperature
        name: Consigne
      - type: attribute
        entity: climate.spa
        attribute: preset_mode
        name: Mode
```

Vous verrez :

```
┌─────────────────────────┐
│      Mon Spa            │
│                         │
│        37°C             │
│   [━━━━━━━●━━━━━━━]    │
│                         │
│  Chauffage: ● Actif     │
│  Température: 37°C      │
│  Consigne: 38°C         │
│  Mode: Standard         │
└─────────────────────────┘
```

---

## 🎯 Que peut faire l'intégration ?

### ✅ Ce qui fonctionne (lecture)

- 🌡️ **Température de l'eau** en temps réel
- 🎯 **Consigne** actuelle
- 🔥 **État du chauffage** (actif/inactif)
- 🔄 **Mode** du spa (Standard / Économique / Sommeil)
- 📊 **Historiques** et graphiques
- 🔔 **Notifications** et automations

### ❌ Ce qui ne fonctionne PAS (écriture)

- ❌ Changer la température depuis Home Assistant
- ❌ Changer le mode depuis Home Assistant

**Pourquoi ?** Le clavier VL403 utilise un protocole propriétaire. Vous devez utiliser :
- Le clavier physique VL403, OU
- Un module IR + ESP32 (voir [IR_CONTROL.md](IR_CONTROL.md) pour le guide complet)

---

## 💡 Exemple d'automatisation : Notification quand le spa est prêt

```yaml
automation:
  - alias: "Spa prêt"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('climate.spa', 'current_temperature') >=
             state_attr('climate.spa', 'temperature') }}
    action:
      - service: notify.mobile_app
        data:
          title: "🔥 Spa prêt !"
          message: "Le spa a atteint {{ state_attr('climate.spa', 'temperature') }}°C"
```

Vous recevrez une notification sur votre téléphone dès que le spa atteint la température souhaitée !

---

## 🆘 Problèmes courants

### ❌ "Impossible de se connecter"

**Solutions** :
1. Vérifiez l'adresse IP de l'EW11A (elle peut changer au redémarrage)
2. Testez la connexion : `telnet 192.168.1.50 8899`
3. Vérifiez que l'EW11A est bien allumé

### ❌ "Le mode change tout le temps entre Standard/Eco/Sommeil"

**C'est normal !** Quand le mode ECO est sélectionné sur le clavier, le spa alterne automatiquement entre les 3 modes pour économiser l'énergie. Ce n'est **pas un bug**, c'est le fonctionnement du spa.

### ❌ "Les valeurs ne se mettent pas à jour"

**Solutions** :
1. Allez dans les **options** de l'intégration
2. Augmentez "Fiabilité des données" à **7** ou **10**
3. Vérifiez les **logs** dans Home Assistant

---

## 📚 Pour aller plus loin

- **[README.md](README.md)** - Documentation complète
- **[IR_CONTROL.md](IR_CONTROL.md)** - Contrôler le spa avec un ESP32
- **[PROTOCOL.md](PROTOCOL.md)** - Détails techniques du protocole RS-485
- **[GitHub Issues](https://github.com/GevaudanBeast/Balboa-GS500z/issues)** - Poser une question

---

## ✅ Checklist

- [ ] Module EW11A branché sur les connecteurs RS-485 du spa
- [ ] EW11A configuré (mode TCP Server, baud 9600, port 8899)
- [ ] EW11A connecté au WiFi de la maison
- [ ] Adresse IP de l'EW11A notée
- [ ] Intégration installée via HACS
- [ ] Home Assistant redémarré
- [ ] Intégration ajoutée avec l'IP de l'EW11A
- [ ] Entités `climate.spa` et `binary_sensor.spa_heater` visibles
- [ ] Carte Lovelace créée

**Tout est coché ?** Profitez de votre spa connecté ! 🎉
