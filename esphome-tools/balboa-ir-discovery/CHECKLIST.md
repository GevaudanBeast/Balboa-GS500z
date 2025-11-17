# ✅ Checklist de vérification

**Utilisez cette checklist pour vous assurer que tout est prêt avant de lancer votre première découverte.**

---

## 📦 Installation du matériel

### ESP32

- [ ] ESP32 DevKit en votre possession
- [ ] Câble USB pour flasher l'ESP32
- [ ] ESP32 alimenté et allumé

### Émetteur IR

- [ ] LED IR 940nm achetée
- [ ] Résistance 100Ω (ou transistor 2N2222/BC547)
- [ ] LED IR câblée correctement :
  - [ ] Patte longue (+) connectée à GPIO4 (via résistance)
  - [ ] Patte courte (-) connectée à GND
- [ ] LED IR fonctionne (visible sur caméra smartphone)

### Récepteur IR (optionnel)

- [ ] Récepteur IR TSOP38238 ou similaire
- [ ] Récepteur câblé :
  - [ ] OUT → GPIO5
  - [ ] VCC → 3.3V (pas 5V !)
  - [ ] GND → GND

### Câblage général

- [ ] Tous les GND connectés ensemble (masse commune)
- [ ] Aucun court-circuit visible
- [ ] Câbles bien fixés (pas de faux contacts)

---

## 💻 Installation logicielle

### Prérequis

- [ ] Home Assistant installé et accessible
- [ ] ESPHome add-on installé dans Home Assistant
- [ ] Connexion Internet fonctionnelle

### Fichiers du projet

- [ ] Dossier `balboa-ir-discovery` téléchargé
- [ ] Fichier `balboa-ir-discovery.yaml` présent
- [ ] Fichier `secrets.yaml.example` présent
- [ ] Documentation présente (docs/)

### Configuration

- [ ] Fichier `secrets.yaml` créé (copie de `secrets.yaml.example`)
- [ ] `secrets.yaml` édité avec :
  - [ ] Nom WiFi (SSID)
  - [ ] Mot de passe WiFi
  - [ ] Clé API générée (avec `openssl rand -base64 32`)
  - [ ] Mot de passe OTA défini
- [ ] GPIO vérifiés dans `balboa-ir-discovery.yaml` :
  - [ ] `ir_transmitter_pin: "GPIO4"` (ou votre GPIO)
  - [ ] `ir_receiver_pin: "GPIO5"` (si utilisé)

### Flashage ESP32

- [ ] Fichier `balboa-ir-discovery.yaml` ajouté dans ESPHome
- [ ] Configuration validée (pas d'erreurs)
- [ ] ESP32 flashé avec succès via USB
- [ ] Logs affichent le démarrage :
  ```
  [INFO] Balboa IR Discovery Tool - Démarrage
  ```
- [ ] ESP32 connecté au WiFi (IP visible dans les logs)

### Intégration Home Assistant

- [ ] Appareil détecté automatiquement dans HA
- [ ] Appareil ajouté avec la clé API
- [ ] Appareil visible dans **Paramètres** → **Appareils et services** → **ESPHome**
- [ ] Toutes les entités disponibles :
  - [ ] Boutons (▶️ Démarrer, ⏸️ Pause, etc.)
  - [ ] Capteurs (Progression, Codes Testés, etc.)
  - [ ] Sélecteurs (Protocole IR, Code Début/Fin)

---

## 🎯 Configuration de la découverte

### Positionnement

- [ ] Spa allumé et fonctionnel
- [ ] Récepteur IR du spa localisé (près du panneau de contrôle)
- [ ] LED IR pointée directement vers le récepteur
- [ ] Distance LED-Spa : 1-3 mètres maximum
- [ ] Pas d'obstacle entre LED et récepteur
- [ ] Pas de lumière directe du soleil sur le récepteur

### Paramètres de découverte

- [ ] **Protocole IR** sélectionné : `NEC` (recommandé pour démarrer)
- [ ] **Code Début** : `0` (ou autre si test spécifique)
- [ ] **Code Fin** : `255` (pour un test rapide) ou plus
- [ ] Délai compris : 2 secondes entre chaque code par défaut

### État du spa

- [ ] Spa dans un état connu (noter température, mode, etc.)
- [ ] Spa stable (pas de changement en cours)
- [ ] Possibilité d'observer le spa pendant 5-30 minutes

---

## 🚀 Préparation au lancement

### Environnement

- [ ] Vous avez du temps devant vous (au moins 10-15 minutes)
- [ ] Vous pouvez observer le spa sans interruption
- [ ] De quoi noter les résultats (smartphone, bloc-notes)

### Tests préliminaires

- [ ] Bouton **🎯 Test Manuel** testé (vérifiez les logs)
- [ ] LED IR émet bien (visible sur caméra)
- [ ] Logs ESPHome accessibles et lisibles
- [ ] Interface HA réactive (boutons cliquables)

### Documentation

- [ ] Guide **USAGE.md** lu (au moins en diagonale)
- [ ] Vous savez quand cliquer sur **✅ Ça Marche !**
- [ ] Vous savez où trouver les codes validés (logs)

---

## 📊 Pendant la découverte

### Surveillance

- [ ] Vous observez **activement** le spa
- [ ] Vous êtes prêt à cliquer sur **✅ Ça Marche !** rapidement

### Comportements à surveiller

Cochez si vous savez reconnaître ces changements :

- [ ] Changement de température affichée
- [ ] Changement de mode (ECO, ST, SL)
- [ ] Chauffage qui s'allume/s'éteint
- [ ] Affichage qui change
- [ ] Bip sonore
- [ ] LED du spa qui s'allume/clignote
- [ ] Tout comportement inhabituel

### Actions à connaître

- [ ] **✅ Ça Marche !** : Valider un code qui fonctionne
- [ ] **⏭️ Suivant** : Passer au code suivant
- [ ] **⏸️ Pause** : Mettre en pause
- [ ] **🔄 Retester** : Re-tester un code suspect
- [ ] **📊 Afficher Rapport** : Voir la progression

---

## 📝 Documentation des résultats

### Préparation

- [ ] Fichier `examples/discovered_codes_template.md` ouvert
- [ ] Prêt à noter :
  - [ ] Code (hex et décimal)
  - [ ] Effet observé
  - [ ] Protocole utilisé
  - [ ] Conditions (température, mode initial, etc.)

### Logs

- [ ] Vous savez accéder aux logs ESPHome
- [ ] Vous savez filtrer les logs pour trouver `CODE VALIDÉ`
- [ ] Vous pouvez copier-coller les codes depuis les logs

---

## 🔧 Dépannage

### En cas de problème, je sais où chercher

- [ ] **SETUP.md** → Section Dépannage
- [ ] **USAGE.md** → FAQ
- [ ] Logs ESPHome pour les erreurs
- [ ] GitHub Issues pour signaler un bug

---

## ✅ Checklist finale (avant de démarrer)

**Si tous ces points sont cochés, vous êtes PRÊT ! 🎉**

- [ ] ESP32 câblé et flashé
- [ ] LED IR fonctionne et est pointée vers le spa
- [ ] Appareil dans Home Assistant avec toutes les entités
- [ ] Protocole NEC sélectionné
- [ ] Plage 0-255 configurée
- [ ] Spa allumé et observable
- [ ] Temps disponible pour surveiller (10-30 min)
- [ ] De quoi noter les résultats
- [ ] Guide USAGE.md lu

---

## 🚀 C'est parti !

Si toute la checklist est validée, vous pouvez :

1. Ouvrir l'appareil **Balboa IR Discovery** dans Home Assistant
2. Cliquer sur **▶️ Démarrer**
3. **Observer attentivement le spa** 👀
4. Cliquer sur **✅ Ça Marche !** dès qu'un changement survient

**Bonne découverte ! 🎯**

---

## 📞 Besoin d'aide ?

Si un élément de cette checklist n'est pas clair :

- Consultez **[SETUP.md](docs/SETUP.md)** pour l'installation
- Consultez **[USAGE.md](docs/USAGE.md)** pour l'utilisation
- Consultez **[QUICKSTART.md](docs/QUICKSTART.md)** pour un démarrage rapide
- Ouvrez une issue sur GitHub

---

**Cette checklist garantit une découverte réussie ! Ne sautez aucune étape ! ✅**
