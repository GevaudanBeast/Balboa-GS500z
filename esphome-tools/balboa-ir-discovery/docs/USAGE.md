# Guide d'Utilisation - Balboa IR Discovery Tool

Ce guide vous explique comment utiliser l'outil de découverte de commandes IR pour identifier les codes que votre spa Balboa accepte.

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Interface Home Assistant](#interface-home-assistant)
3. [Workflow de découverte](#workflow-de-découverte)
4. [Mode automatique](#mode-automatique)
5. [Mode manuel](#mode-manuel)
6. [Analyser les résultats](#analyser-les-résultats)
7. [Bonnes pratiques](#bonnes-pratiques)
8. [FAQ](#faq)

---

## 🎯 Vue d'ensemble

### Principe de fonctionnement

L'outil fonctionne en 3 étapes simples :

1. **Configuration** : Vous choisissez le protocole IR et la plage de codes à tester
2. **Envoi** : L'ESP32 envoie les codes IR un par un vers le spa
3. **Validation** : Vous observez le spa et validez les codes qui fonctionnent

### Ce dont vous avez besoin

- ✅ ESP32 configuré et connecté (voir [SETUP.md](SETUP.md))
- ✅ Home Assistant avec l'appareil ESPHome visible
- ✅ LED IR pointée vers le récepteur IR du spa
- ✅ **Accès visuel au spa** pour observer les changements
- ⚠️ **Patience** : La découverte peut prendre du temps !

---

## 🖥️ Interface Home Assistant

### Localiser l'appareil

1. Ouvrez **Home Assistant**
2. Allez dans **Paramètres** → **Appareils et services** → **ESPHome**
3. Cliquez sur **Balboa IR Discovery**
4. Vous verrez l'interface complète

### Composants de l'interface

#### 📊 Capteurs d'information

| Capteur | Description | Exemple |
|---------|-------------|---------|
| **Statut** | État actuel de la découverte | "En cours...", "Prêt", "Terminé" |
| **Code Actuel** | Code IR en cours de test | `0x00001234` |
| **Protocole Actuel** | Protocole IR utilisé | `NEC`, `RC5`, `Samsung` |
| **Progression** | Pourcentage de codes testés | `25.5%` |
| **Codes Testés** | Nombre de codes déjà testés | `1234` |
| **Codes Validés** | Nombre de codes qui fonctionnent | `5` |

#### ⚙️ Paramètres de configuration

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| **Protocole IR** | Type de protocole à tester | `NEC` |
| **Code Début** | Premier code de la plage | `0` (0x00000000) |
| **Code Fin** | Dernier code de la plage | `65535` (0x0000FFFF) |

#### 🎮 Boutons de contrôle

| Bouton | Action | Utilisation |
|--------|--------|-------------|
| **▶️ Démarrer** | Lance la découverte | Commencer une nouvelle session |
| **⏸️ Pause** | Met en pause | Faire une pause café ☕ |
| **⏹️ Arrêter** | Arrête et réinitialise | Abandonner la session actuelle |
| **✅ Ça Marche !** | Valide le code actuel | **LE PLUS IMPORTANT** - quand le spa réagit ! |
| **⏭️ Suivant** | Passe au code suivant | Si le code ne fait rien |
| **🔄 Retester** | Reteste le code actuel | Pour confirmer un effet |
| **🎯 Test Manuel** | Teste le code actuel sans avancer | Tester un code spécifique |
| **📊 Afficher Rapport** | Affiche un résumé dans les logs | Voir la progression |

---

## 🔍 Workflow de découverte

### Étape 1 : Préparation

#### Positionner l'émetteur IR

1. **Distance** : Placez la LED IR à 1-3 mètres du spa
2. **Angle** : Pointez directement vers le récepteur IR du spa
   - Le récepteur est généralement près du panneau de contrôle
   - Cherchez une petite fenêtre noire brillante
3. **Obstacles** : Assurez-vous qu'il n'y a rien entre la LED et le récepteur
4. **Lumière** : Évitez la lumière directe du soleil (peut perturber l'IR)

#### Vérifier l'état du spa

1. **Allumé** : Le spa doit être sous tension
2. **État connu** : Notez l'état actuel (température, mode, etc.)
3. **Stabilité** : Attendez que le spa soit en état stable (pas de changement en cours)

#### Préparer de quoi noter

Gardez à portée de main :
- 📱 Smartphone (pour les logs ou notes)
- 📝 Bloc-notes
- ☕ Boisson chaude (ça peut être long !)

### Étape 2 : Configuration de la découverte

#### Choisir le protocole IR

**Protocoles disponibles :**

| Protocole | Description | Utilisation typique | Recommandation |
|-----------|-------------|---------------------|----------------|
| **NEC** | Le plus courant | Télécommandes TV, climatiseurs | **Commencez par celui-ci** ⭐ |
| **RC5** | Philips, ancien standard | Vieux équipements | Si NEC ne donne rien |
| **RC6** | Philips, nouveau standard | Équipements modernes | Si NEC ne donne rien |
| **Samsung** | Spécifique Samsung | TV Samsung, clim | Si le spa est de marque Samsung |
| **LG** | Spécifique LG | TV LG, clim | Si le spa est de marque LG |
| **Sony** | Spécifique Sony | Équipements Sony | Rare pour les spas |

**Conseil** : Commencez **toujours par NEC**, c'est le plus probable !

#### Définir la plage de codes

**Stratégie recommandée** : Commencez petit, puis élargissez.

| Plage | Début (décimal) | Fin (décimal) | Début (hex) | Fin (hex) | Temps estimé* |
|-------|-----------------|---------------|-------------|-----------|--------------|
| **Mini** | 0 | 255 | 0x00000000 | 0x000000FF | ~9 minutes |
| **Petite** | 0 | 4095 | 0x00000000 | 0x00000FFF | ~2 heures |
| **Moyenne** | 0 | 65535 | 0x00000000 | 0x0000FFFF | ~36 heures |
| **Grande** | 0 | 16777215 | 0x00000000 | 0x00FFFFFF | ~1 an ! |

*\*Avec délai de 2 secondes entre chaque code*

**Exemple de configuration dans Home Assistant :**

1. Sélectionnez **Protocole IR** → `NEC`
2. **Code Début** → `0`
3. **Code Fin** → `255` (pour commencer)

### Étape 3 : Lancer la découverte

1. **Vérifiez** que tout est prêt (spa allumé, LED pointée, etc.)
2. Cliquez sur **▶️ Démarrer**
3. Observez les logs ESPHome pour confirmation :

```
[12:00:00][INFO] ==========================================
[12:00:00][INFO] 🚀 DÉMARRAGE DE LA DÉCOUVERTE
[12:00:00][INFO] Protocole: NEC
[12:00:00][INFO] Plage: 0x00000000 à 0x000000FF
[12:00:00][INFO] ==========================================
```

4. **Surveillez le spa !** 👀

### Étape 4 : Validation des codes

#### Quand cliquer sur "✅ Ça Marche !"

Cliquez dès que vous observez **n'importe quel changement** sur le spa :

- ✅ Changement de température
- ✅ Changement de mode (ECO, ST, SL)
- ✅ Chauffage qui s'allume/éteint
- ✅ Affichage qui change
- ✅ Bip sonore
- ✅ LED qui s'allume/clignote
- ✅ **Tout comportement inattendu**

**Ne soyez pas trop exigeant au début !** Même un petit bip compte.

#### Exemple de validation

**Situation** : Le spa passe de mode ST à ECO

1. Vous voyez le changement immédiatement
2. Cliquez sur **✅ Ça Marche !**
3. Les logs affichent :

```
[12:05:34][WARN] ==========================================
[12:05:34][WARN] ✅✅✅ CODE VALIDÉ ✅✅✅
[12:05:34][WARN] Protocole: NEC
[12:05:34][WARN] Code: 0x00000042
[12:05:34][WARN] ==========================================
```

4. **Notez quelque part** : "Code 0x00000042 = Changement de mode ST→ECO"

#### Si rien ne se passe

- Attendez 2 secondes (délai par défaut)
- Le code suivant sera automatiquement testé
- **Ou** cliquez sur **⏭️ Suivant** pour accélérer

### Étape 5 : Pause et reprise

Vous pouvez faire une pause à tout moment :

1. Cliquez sur **⏸️ Pause**
2. Le code actuel est sauvegardé
3. Faites votre pause ☕
4. Cliquez sur **▶️ Démarrer** pour reprendre là où vous étiez

### Étape 6 : Fin de la découverte

Quand tous les codes ont été testés :

```
[14:30:00][INFO] 🎉 Découverte terminée ! 5 codes validés
```

Le statut affiche : **"Terminé !"**

---

## ⚡ Mode automatique

> **Note** : Cette fonctionnalité nécessite un adaptateur RS-485 (optionnel)

Le mode automatique détecte automatiquement si un code a un effet en surveillant l'état du spa via RS-485.

### Configuration RS-485

1. Décommentez la section `uart:` dans `balboa-ir-discovery.yaml` :

```yaml
uart:
  id: uart_bus
  tx_pin: ${rs485_tx_pin}
  rx_pin: ${rs485_rx_pin}
  baud_rate: 9600
  data_bits: 8
  parity: NONE
  stop_bits: 1
```

2. Câblez l'adaptateur RS-485 :
   - **ESP32 GPIO17** → MAX485 DI
   - **ESP32 GPIO16** → MAX485 RO
   - **MAX485 A** → Spa RS-485 A
   - **MAX485 B** → Spa RS-485 B

3. Recompilez et téléversez

### Utilisation du mode automatique

*(Fonctionnalité à implémenter dans une future version)*

---

## 🎯 Mode manuel

Le mode manuel permet de tester un code spécifique sans lancer une découverte complète.

### Tester un code précis

1. Saisissez le code dans **Code Début** (ex: `42` pour tester 0x0000002A)
2. Cliquez sur **🎯 Test Manuel**
3. Observez le spa
4. Si ça marche, cliquez sur **✅ Ça Marche !**

### Re-tester un code suspect

1. Notez le code actuel affiché
2. Cliquez sur **🔄 Retester**
3. Observez à nouveau
4. Validez ou passez au suivant

---

## 📈 Analyser les résultats

### Consulter les logs

Les codes validés sont enregistrés dans les logs avec le niveau `WARN` pour les repérer facilement.

#### Via ESPHome Dashboard

1. Ouvrez **ESPHome**
2. Cliquez sur **LOGS** sur votre appareil
3. Recherchez les lignes avec `✅✅✅ CODE VALIDÉ`

#### Via Home Assistant

1. **Paramètres** → **Système** → **Logs**
2. Filtrez par `esphome.balboa_ir_discovery`

#### Exemple de log

```
[12:05:34][WARN] ==========================================
[12:05:34][WARN] ✅✅✅ CODE VALIDÉ ✅✅✅
[12:05:34][WARN] Protocole: NEC
[12:05:34][WARN] Code: 0x00000042
[12:05:34][WARN] ==========================================
```

### Extraire les codes

**Méthode 1** : Copier-coller depuis les logs

1. Ouvrez les logs
2. Recherchez `CODE VALIDÉ`
3. Copiez les codes dans un fichier texte

**Méthode 2** : Export automatique (future fonctionnalité)

### Documenter vos découvertes

Créez un tableau comme celui-ci :

| Code (hex) | Code (décimal) | Protocole | Effet observé | Confirmé ? |
|------------|----------------|-----------|---------------|------------|
| 0x00000042 | 66 | NEC | Change mode ST→ECO | ✅ |
| 0x00000043 | 67 | NEC | Change mode ECO→SL | ✅ |
| 0x00000050 | 80 | NEC | Monte température +1°C | ✅ |
| 0x00000051 | 81 | NEC | Baisse température -1°C | ✅ |
| 0x00000060 | 96 | NEC | Active chauffage | ✅ |

### Vérifier les codes

**Important** : Testez chaque code plusieurs fois pour confirmer !

1. Mettez le spa dans un état connu
2. Envoyez le code (via **🎯 Test Manuel**)
3. Notez l'effet
4. Répétez 3 fois pour confirmer

---

## 💡 Bonnes pratiques

### Optimisation du temps

1. **Commencez petit** : Testez d'abord 0-255, pas 0-65535
2. **Protocole NEC d'abord** : C'est le plus courant
3. **Notez immédiatement** : N'attendez pas la fin pour documenter
4. **Testez par blocs** : Faites 255 codes, analysez, puis continuez

### Sécurité

1. **Surveillez le spa** : Arrêtez si comportement anormal
2. **Ne laissez pas sans surveillance** : Des codes peuvent faire n'importe quoi
3. **Testez en journée** : Plus facile d'observer les changements
4. **Évitez les heures de pointe** : Si vous partagez le spa

### Efficacité

1. **Utilisez le bouton Pause** : Ne recommencez pas à zéro
2. **Plusieurs sessions courtes** : 30 min x 10 > 5h d'affilée
3. **Notez tout** : Même les codes qui semblent ne rien faire peuvent être utiles

### Documentation

1. **Photos/vidéos** : Filmez les réactions du spa
2. **Horodatage** : Notez l'heure pour croiser avec les logs
3. **Conditions** : Température de l'eau, heure, météo (si extérieur)

---

## ❓ FAQ

### Q1 : Combien de temps ça va prendre ?

**R** : Dépend de la plage :
- 0-255 : ~9 minutes
- 0-65535 : ~36 heures

Mais vous pouvez faire des pauses !

### Q2 : Pourquoi je ne trouve aucun code qui fonctionne ?

**R** : Plusieurs raisons possibles :
1. **Mauvais protocole** : Essayez RC5, RC6, Samsung
2. **LED IR défaillante** : Vérifiez avec une caméra
3. **Portée insuffisante** : Rapprochez la LED ou utilisez un transistor
4. **Spa ne supporte pas IR** : Vérifiez la documentation du spa

### Q3 : J'ai trouvé un code, mais il ne fonctionne pas toujours

**R** : Possible que :
1. Le code nécessite un état spécifique du spa
2. Il y a des interférences (soleil, autres IR)
3. La LED IR est mal positionnée

### Q4 : Puis-je tester plusieurs protocoles en même temps ?

**R** : Non, testez-les un par un pour éviter la confusion. Mais vous pouvez lancer plusieurs découvertes successives.

### Q5 : Les codes sont-ils portables entre différents spas Balboa ?

**R** : Probablement, mais pas garanti. Les codes peuvent varier selon :
- Le modèle exact du spa
- La version du firmware
- Les options installées

### Q6 : Que faire si je trouve 100 codes qui fonctionnent ?

**R** : Excellent ! Regroupez-les par fonction :
- Codes de température (probablement séquentiels)
- Codes de mode
- Codes de jets/pompes (si applicable)

### Q7 : Puis-je utiliser cet outil pour d'autres appareils ?

**R** : Oui ! L'outil est générique. Vous pouvez l'utiliser pour :
- Climatiseurs
- Télévisions
- Décodeurs
- Tout appareil avec récepteur IR

---

## 📞 Besoin d'aide ?

- **Logs illisibles** → Voir [SETUP.md - Dépannage](SETUP.md#dépannage)
- **LED IR ne fonctionne pas** → Voir [SETUP.md - Problème LED IR](SETUP.md#problème-led-ir-ne-sallume-pas)
- **Autre problème** → Ouvrez une issue sur GitHub

---

## 🎓 Prochaines étapes

Une fois que vous avez découvert les codes :

1. **Documentez-les** : Créez un tableau des codes
2. **Intégrez-les** : Utilisez-les dans Home Assistant
3. **Partagez-les** : Aidez la communauté en partageant vos découvertes !

**Bon courage pour la découverte ! 🚀**
