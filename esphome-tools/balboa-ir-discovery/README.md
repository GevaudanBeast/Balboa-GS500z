# 🔍 Balboa IR Discovery Tool

**Outil de découverte de commandes IR pour spa Balboa GS500Z**

Découvrez automatiquement les codes infrarouges acceptés par votre spa Balboa en testant systématiquement différents protocoles IR avec validation humaine simple.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![ESPHome](https://img.shields.io/badge/ESPHome-compatible-orange)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-compatible-blue)

---

## 📖 Vue d'ensemble

### Qu'est-ce que c'est ?

Cet outil utilise un **ESP32 avec un émetteur IR** pour tester systématiquement des codes infrarouges et identifier lesquels sont acceptés par votre spa Balboa GS500Z.

### Pourquoi c'est utile ?

- 🎯 **Découvrir les commandes IR** que le spa accepte
- 🔓 **Contrôler le spa sans télécommande officielle**
- 🏠 **Intégrer le contrôle IR dans Home Assistant**
- 🧪 **Reverse-engineering du protocole IR** du spa
- 💡 **Créer une télécommande universelle** personnalisée

### Comment ça marche ?

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ ESP32 +     │   IR    │ Spa Balboa   │  État   │ Vous        │
│ Émetteur IR ├────────>│ GS500Z       ├────────>│ (validation)│
│             │         │              │         │             │
└─────┬───────┘         └──────────────┘         └──────┬──────┘
      │                                                  │
      │                 ┌──────────────┐                │
      └────────────────>│ Home         │<───────────────┘
        Contrôle        │ Assistant    │   ✅ Ça marche!
                        └──────────────┘
```

1. **Configuration** : Vous choisissez le protocole IR et la plage de codes
2. **Envoi automatique** : L'ESP32 envoie les codes un par un
3. **Observation** : Vous observez si le spa réagit
4. **Validation** : Vous cliquez sur "✅ Ça marche !" quand vous voyez un effet
5. **Enregistrement** : Les codes validés sont enregistrés dans les logs

---

## ✨ Fonctionnalités

### Protocoles IR supportés

- ✅ **NEC** (le plus courant - recommandé pour commencer)
- ✅ **RC5** (Philips)
- ✅ **RC6** (Philips moderne)
- ✅ **Samsung**
- ✅ **LG**
- ✅ **Sony**

### Modes de découverte

- 🔄 **Mode automatique** : Teste les codes séquentiellement
- 🎯 **Mode manuel** : Teste un code spécifique
- ⏸️ **Pause/Reprise** : Mettez en pause et reprenez plus tard
- 📊 **Suivi de progression** : Visualisez l'avancement en temps réel

### Interface utilisateur

- 🖥️ **Interface Home Assistant** complète et intuitive
- 📱 **Interface Web ESPHome** locale
- 📊 **Capteurs de progression** en temps réel
- 🔘 **Boutons de contrôle** simples
- 📝 **Logs détaillés** pour analyse

### Validation

- ✅ **Validation humaine** : Vous confirmez manuellement les codes qui fonctionnent
- 🔄 **Re-test facile** : Re-testez un code pour confirmer
- 📋 **Enregistrement automatique** : Les codes validés sont sauvegardés dans les logs

---

## 🚀 Démarrage rapide

### Prérequis

- **Matériel** :
  - ESP32 DevKit (~5-10€)
  - LED IR 940nm (~1€)
  - Résistance 100Ω (~0.10€)
  - Quelques câbles Dupont (~2€)

- **Logiciel** :
  - Home Assistant installé
  - ESPHome add-on installé
  - Éditeur de texte

### Installation en 5 étapes

#### 1️⃣ Câbler le matériel

```
ESP32                    LED IR
┌─────────────┐         ┌──────┐
│   GPIO4 ────┼─[100Ω]─┤+ Anode
│             │         └──────┘
│   GND ──────┼────────────┘
└─────────────┘
```

#### 2️⃣ Copier les fichiers

```bash
cd /config/esphome
git clone <ce-repo>
cd balboa-ir-discovery
cp secrets.yaml.example secrets.yaml
```

#### 3️⃣ Configurer les secrets

Éditez `secrets.yaml` :

```yaml
wifi_ssid: "VotreSSID"
wifi_password: "VotreMotDePasse"
api_encryption_key: "générez-avec-openssl-rand-base64-32"
ota_password: "votre_mot_de_passe"
```

#### 4️⃣ Flasher l'ESP32

Dans ESPHome Dashboard :
1. Cliquez sur **INSTALL**
2. Sélectionnez **Plug into this computer**
3. Choisissez le port USB
4. Attendez le téléversement

#### 5️⃣ Ajouter à Home Assistant

1. **Paramètres** → **Appareils et services** → **+ AJOUTER**
2. Sélectionnez **ESPHome**
3. L'appareil est détecté automatiquement
4. Entrez la clé API et validez

**C'est tout ! 🎉**

---

## 📚 Documentation complète

| Document | Description |
|----------|-------------|
| **[SETUP.md](docs/SETUP.md)** | Guide d'installation détaillé avec schémas de câblage |
| **[USAGE.md](docs/USAGE.md)** | Guide d'utilisation complet avec bonnes pratiques |
| **[QUICKSTART.md](docs/QUICKSTART.md)** | Guide de démarrage ultra-rapide (5 minutes) |

---

## 🎮 Utilisation

### Configuration de base

1. Ouvrez l'appareil dans Home Assistant
2. Sélectionnez le **Protocole IR** : `NEC` (recommandé)
3. Définissez la **plage de codes** :
   - Début : `0`
   - Fin : `255` (pour commencer petit)

### Lancer la découverte

1. Pointez la LED IR vers le récepteur IR du spa
2. Cliquez sur **▶️ Démarrer**
3. **Observez attentivement le spa** 👀
4. Dès qu'un changement se produit, cliquez sur **✅ Ça Marche !**
5. Continuez jusqu'à la fin de la plage

### Récupérer les résultats

Les codes validés apparaissent dans les logs :

```
[12:05:34][WARN] ==========================================
[12:05:34][WARN] ✅✅✅ CODE VALIDÉ ✅✅✅
[12:05:34][WARN] Protocole: NEC
[12:05:34][WARN] Code: 0x00000042
[12:05:34][WARN] ==========================================
```

Consultez les logs dans **ESPHome** → **LOGS** ou dans Home Assistant.

---

## 📊 Interface Home Assistant

### Capteurs disponibles

| Capteur | Description |
|---------|-------------|
| **Statut** | État actuel de la découverte |
| **Code Actuel** | Code IR en cours de test |
| **Protocole Actuel** | Protocole utilisé |
| **Progression** | Pourcentage complété |
| **Codes Testés** | Nombre de codes testés |
| **Codes Validés** | Nombre de codes confirmés |

### Boutons de contrôle

| Bouton | Action |
|--------|--------|
| **▶️ Démarrer** | Lance la découverte |
| **⏸️ Pause** | Met en pause |
| **⏹️ Arrêter** | Arrête et réinitialise |
| **✅ Ça Marche !** | Valide le code actuel ⭐ |
| **⏭️ Suivant** | Passe au code suivant |
| **🔄 Retester** | Re-teste le code actuel |
| **🎯 Test Manuel** | Teste un code spécifique |
| **📊 Afficher Rapport** | Affiche un résumé |

---

## 💡 Conseils et astuces

### Optimiser la découverte

1. **Commencez petit** : Testez 0-255 avant 0-65535
2. **Protocole NEC d'abord** : C'est le plus courant pour les équipements domestiques
3. **Testez par sessions** : 30 minutes × 10 sessions > 5 heures d'affilée
4. **Documentez immédiatement** : Notez chaque code validé tout de suite

### Améliorer la portée IR

1. **Utilisez un transistor** : Amplifie le signal (voir schéma dans SETUP.md)
2. **Plusieurs LEDs IR** : Montez-les en parallèle
3. **Rapprochez la LED** : 1-3 mètres du récepteur
4. **Évitez les obstacles** : Ligne de vue directe

### Résolution de problèmes

| Problème | Solution |
|----------|----------|
| Aucun code ne fonctionne | Essayez d'autres protocoles (RC5, RC6, Samsung) |
| LED IR ne s'allume pas | Vérifiez avec une caméra de smartphone |
| Portée trop courte | Utilisez un transistor ou rapprochez la LED |
| Logs trop rapides | Augmentez `discovery_delay` dans le YAML |

---

## 🔧 Configuration avancée

### Personnaliser le délai entre codes

Dans `balboa-ir-discovery.yaml` :

```yaml
substitutions:
  discovery_delay: "3s"  # Changez de 2s à 3s par exemple
```

### Changer les GPIO

```yaml
substitutions:
  ir_transmitter_pin: "GPIO4"  # Changez selon votre câblage
  ir_receiver_pin: "GPIO5"
```

### Activer la validation automatique (avancé)

Décommentez la section `uart:` pour activer la lecture RS-485 :

```yaml
uart:
  id: uart_bus
  tx_pin: ${rs485_tx_pin}
  rx_pin: ${rs485_rx_pin}
  baud_rate: 9600
```

---

## 📈 Exemple de résultats

Voici ce que vous pourriez découvrir :

| Code (hex) | Protocole | Effet observé |
|------------|-----------|---------------|
| `0x00000042` | NEC | Change mode ST → ECO |
| `0x00000043` | NEC | Change mode ECO → SL |
| `0x00000050` | NEC | Monte température +1°C |
| `0x00000051` | NEC | Baisse température -1°C |
| `0x00000060` | NEC | Active/désactive chauffage |

---

## 🤝 Contribution

Les contributions sont les bienvenues !

### Partager vos découvertes

Si vous découvrez des codes fonctionnels :

1. Créez une **issue** avec vos résultats
2. Documentez le modèle exact de votre spa
3. Listez tous les codes découverts avec leurs effets
4. Précisez le protocole IR utilisé

### Améliorer l'outil

- 🐛 **Signaler des bugs** : Ouvrez une issue
- 💡 **Proposer des fonctionnalités** : Ouvrez une issue avec le tag "enhancement"
- 🔧 **Pull requests** : Les PRs sont appréciées !

---

## 📋 Roadmap

### Fonctionnalités futures

- [ ] **Validation automatique** via RS-485 (détection automatique des changements)
- [ ] **Export JSON** des codes découverts
- [ ] **Import de codes connus** pour tests rapides
- [ ] **Graphiques de progression** dans Home Assistant
- [ ] **Base de données communautaire** des codes découverts
- [ ] **Apprentissage de télécommande existante** (capture IR)

---

## ⚖️ License

Ce projet est sous licence **MIT**.

Vous êtes libre de :
- ✅ Utiliser commercialement
- ✅ Modifier
- ✅ Distribuer
- ✅ Utiliser en privé

Avec les conditions :
- ℹ️ Inclure la license et le copyright

---

## 🙏 Remerciements

- **ESPHome Team** : Pour l'excellent framework
- **Home Assistant Community** : Pour l'inspiration et le support
- **Balboa Water Group** : Pour les spas GS500Z

---

## 📞 Support

- **📖 Documentation** : Voir [docs/](docs/)
- **🐛 Issues** : [GitHub Issues](../../issues)
- **💬 Discussions** : [GitHub Discussions](../../discussions)
- **📧 Email** : (votre email si vous voulez)

---

## ⚠️ Avertissement

Cet outil envoie des commandes IR aléatoires à votre spa. Bien que généralement sans danger, il est **recommandé de** :

- ✅ Surveiller le spa pendant la découverte
- ✅ Arrêter immédiatement en cas de comportement anormal
- ✅ Tester d'abord sur une plage réduite (0-255)
- ⚠️ Ne pas laisser sans surveillance

**L'auteur n'est pas responsable des dommages causés à votre équipement.**

---

## 🌟 Vous aimez ce projet ?

Si cet outil vous a été utile :

- ⭐ **Star** ce dépôt sur GitHub
- 🐦 **Partagez** avec la communauté
- 💬 **Partagez vos résultats** dans les discussions
- ☕ **Offrez-moi un café** (lien PayPal/Ko-fi si vous voulez)

---

**Bonne découverte ! 🚀**

*Fait avec ❤️ pour la communauté Home Assistant et Balboa*
