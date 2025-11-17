# ⚡ Démarrage Rapide - 5 Minutes Chrono !

**Lancez votre première découverte de codes IR en moins de 5 minutes.**

---

## 🎯 Ce dont vous avez besoin

### Matériel (minimum absolu)

- [x] **ESP32** (n'importe quel modèle)
- [x] **LED IR 940nm** (1€ sur Amazon/AliExpress)
- [x] **Résistance 100Ω** (optionnel mais recommandé)
- [x] **3 câbles Dupont**
- [x] **Câble USB** pour flasher l'ESP32

### Logiciel

- [x] **Home Assistant** installé et accessible
- [x] **ESPHome** add-on installé dans HA

---

## ⚡ Installation en 5 étapes

### Étape 1 : Câblage (2 minutes)

**Version ultra-simple (sans résistance)** :

```
ESP32              LED IR
GPIO4 ────────────(+) Anode (patte longue)
GND ──────────────(-) Cathode (patte courte)
```

**Version recommandée (avec résistance)** :

```
ESP32              Résistance    LED IR
GPIO4 ───────────[100Ω]─────────(+) Anode
GND ────────────────────────────(-) Cathode
```

**⚠️ ATTENTION** : Patte **longue** = Anode (+), patte **courte** = Cathode (-)

### Étape 2 : Télécharger les fichiers (30 secondes)

1. Téléchargez **[balboa-ir-discovery.yaml](../balboa-ir-discovery.yaml)**
2. Téléchargez **[secrets.yaml.example](../secrets.yaml.example)**

### Étape 3 : Configuration (1 minute)

1. **Renommez** `secrets.yaml.example` en `secrets.yaml`
2. **Éditez** `secrets.yaml` :

```yaml
wifi_ssid: "VotreNomWiFi"
wifi_password: "VotreMotDePasseWiFi"
api_encryption_key: "laissez-vide-pour-le-moment"
ota_password: "123456"
```

3. **Générez une clé API** :
   - Linux/Mac : `openssl rand -base64 32`
   - Windows : Laissez vide pour le moment (HA générera une clé automatiquement)

### Étape 4 : Flasher l'ESP32 (2 minutes)

1. Ouvrez **ESPHome** dans Home Assistant
2. Cliquez sur **+ NEW DEVICE**
3. Cliquez sur **CONTINUE** → **SKIP**
4. Cliquez sur **⋮** (trois points) → **Upload**
5. Sélectionnez `balboa-ir-discovery.yaml`
6. Cliquez sur **INSTALL** → **Plug into this computer**
7. Branchez l'ESP32 via USB
8. Sélectionnez le port (COM3, /dev/ttyUSB0, etc.)
9. **Attendez ~2-3 minutes**

### Étape 5 : Ajouter à Home Assistant (30 secondes)

1. Home Assistant détecte automatiquement le nouvel appareil
2. Notification : **"Nouvel appareil ESPHome découvert"**
3. Cliquez sur **CONFIGURER**
4. Entrez la clé API (si demandé)
5. Cliquez sur **SOUMETTRE**

**✅ C'EST TERMINÉ !**

---

## 🚀 Première découverte en 3 clics

### 1. Ouvrir l'appareil

1. **Paramètres** → **Appareils et services** → **ESPHome**
2. Cliquez sur **Balboa IR Discovery**

### 2. Configurer

| Paramètre | Valeur |
|-----------|--------|
| **Protocole IR** | `NEC` |
| **Code Début** | `0` |
| **Code Fin** | `255` |

### 3. Lancer !

1. **Pointez** la LED IR vers le spa (1-3 mètres)
2. Cliquez sur **▶️ Démarrer**
3. **Observez le spa** 👀
4. Dès qu'il réagit, cliquez sur **✅ Ça Marche !**

---

## 📋 Checklist de vérification

Avant de cliquer sur "Démarrer", vérifiez :

- [ ] LED IR câblée (GPIO4 → Anode, GND → Cathode)
- [ ] ESP32 connecté au Wi-Fi (vérifiez dans ESPHome)
- [ ] Appareil visible dans Home Assistant
- [ ] Spa **allumé** et accessible
- [ ] LED IR **pointée vers le récepteur IR du spa**
- [ ] Vous êtes prêt à **observer le spa** pendant 5-10 minutes

---

## 🎯 À quoi s'attendre

### Pendant la découverte

Vous verrez dans l'interface :

```
Statut : "Test: 0x00000042"
Code Actuel : "0x00000042"
Protocole Actuel : "NEC"
Progression : "25.5%"
Codes Testés : "65"
Codes Validés : "0"
```

### Quand un code fonctionne

Le spa peut :
- Changer de température
- Changer de mode (ECO/ST/SL)
- Afficher un message
- Émettre un bip
- Allumer/éteindre le chauffage

➡️ **Cliquez immédiatement sur "✅ Ça Marche !"**

### Dans les logs

```
[12:05:34][WARN] ==========================================
[12:05:34][WARN] ✅✅✅ CODE VALIDÉ ✅✅✅
[12:05:34][WARN] Protocole: NEC
[12:05:34][WARN] Code: 0x00000042
[12:05:34][WARN] ==========================================
```

---

## ❓ FAQ Ultra-Rapide

### Q : La LED IR fonctionne-t-elle ?

**R** : Utilisez votre caméra de smartphone. La LED doit apparaître **violet/blanc** sur l'écran.

### Q : Combien de temps pour tester 0-255 ?

**R** : Environ **9 minutes** (2 secondes par code).

### Q : Je ne trouve aucun code qui fonctionne

**R** : Essayez un autre protocole (RC5, RC6, Samsung) ou rapprochez la LED.

### Q : Puis-je mettre en pause ?

**R** : Oui ! Cliquez sur **⏸️ Pause**. La progression est sauvegardée.

---

## 🎓 Prochaines étapes

Une fois que vous avez découvert quelques codes :

1. **[USAGE.md](USAGE.md)** : Apprenez toutes les fonctionnalités
2. **[SETUP.md](SETUP.md)** : Améliorez votre installation (transistor, RS-485, etc.)
3. **Partagez vos découvertes** : Aidez la communauté !

---

## 🆘 Problèmes ?

| Problème | Solution rapide |
|----------|----------------|
| ESP32 ne se connecte pas | Vérifiez le SSID/mot de passe dans `secrets.yaml` |
| LED IR ne s'allume pas | Inversez les pattes (+/-) ou vérifiez la résistance |
| HA ne détecte pas l'appareil | Ajoutez manuellement avec l'IP de l'ESP32 |
| Codes ne fonctionnent pas | Essayez d'autres protocoles ou rapprochez la LED |

**Plus de détails** : Voir [SETUP.md - Dépannage](SETUP.md#dépannage)

---

**C'est parti ! Bonne découverte ! 🚀**

*Temps total : ~5 minutes de configuration + 10 minutes de première découverte*
