# Guide de Contribution

Merci de votre intérêt pour contribuer au **Balboa IR Discovery Tool** ! 🎉

Ce document explique comment contribuer efficacement à ce projet.

---

## 📋 Table des matières

1. [Code de Conduite](#code-de-conduite)
2. [Comment Contribuer](#comment-contribuer)
3. [Signaler un Bug](#signaler-un-bug)
4. [Proposer une Fonctionnalité](#proposer-une-fonctionnalité)
5. [Soumettre des Codes Découverts](#soumettre-des-codes-découverts)
6. [Développement](#développement)
7. [Style de Code](#style-de-code)
8. [Processus de Pull Request](#processus-de-pull-request)

---

## 🤝 Code de Conduite

Ce projet adopte un code de conduite basé sur le respect mutuel :

- ✅ Soyez respectueux et constructif
- ✅ Acceptez les critiques constructives
- ✅ Concentrez-vous sur ce qui est meilleur pour la communauté
- ✅ Faites preuve d'empathie envers les autres membres

---

## 💡 Comment Contribuer

Il existe plusieurs façons de contribuer :

### 1. 🐛 Signaler des bugs
Trouvé un problème ? Ouvrez une issue !

### 2. ✨ Proposer des fonctionnalités
Vous avez une idée ? Partagez-la !

### 3. 📊 Partager vos codes découverts
Aidez la communauté en partageant vos résultats

### 4. 📚 Améliorer la documentation
Corrections, clarifications, traductions

### 5. 🔧 Contribuer du code
Corrections de bugs, nouvelles fonctionnalités

### 6. 🎨 Créer des dashboards
Partagez vos configurations Lovelace

---

## 🐛 Signaler un Bug

### Avant de signaler

1. **Vérifiez** que le bug n'a pas déjà été signalé
2. **Testez** avec la dernière version
3. **Lisez** la documentation (SETUP.md, USAGE.md, FAQ)

### Comment signaler

Créez une issue avec :

**Template** :

```markdown
### Description du bug
Description claire et concise du problème.

### Étapes pour reproduire
1. Aller dans '...'
2. Cliquer sur '...'
3. Observer l'erreur

### Comportement attendu
Ce qui devrait se passer.

### Comportement actuel
Ce qui se passe réellement.

### Environnement
- Version du projet : [ex: v2.0.0]
- Version ESPHome : [ex: 2024.6.0]
- Version Home Assistant : [ex: 2024.6.0]
- Modèle ESP32 : [ex: ESP32-DevKitC]
- Modèle de spa : [ex: Balboa GS500Z]

### Logs
```yaml
[Coller les logs pertinents ici]
```

### Captures d'écran
Si applicable, ajoutez des captures d'écran.
```

---

## ✨ Proposer une Fonctionnalité

### Avant de proposer

1. **Vérifiez** que la fonctionnalité n'existe pas déjà
2. **Vérifiez** qu'elle n'est pas dans la roadmap (CHANGELOG.md)
3. **Réfléchissez** à l'utilité pour la communauté

### Comment proposer

Créez une issue avec :

**Template** :

```markdown
### Fonctionnalité proposée
Description claire de la fonctionnalité.

### Problème résolu
Quel problème cette fonctionnalité résout-elle ?

### Solution proposée
Comment devrait-elle fonctionner ?

### Alternatives considérées
Avez-vous pensé à d'autres solutions ?

### Informations supplémentaires
Tout autre contexte utile.
```

---

## 📊 Soumettre des Codes Découverts

### Format

Créez une issue avec le titre : `[CODES] Modèle de spa - Protocole`

**Template** :

```markdown
### Informations sur le spa
- Modèle : Balboa GS500Z
- Version firmware : [si connu]
- Télécommande : VL403 / Autre
- Date de découverte : AAAA-MM-JJ

### Protocole IR
- Protocole : NEC / RC5 / RC6 / Samsung / LG / Sony
- Plage testée : 0x00000000 à 0x0000FFFF

### Codes découverts

| Code (Hex) | Code (Déc) | Fonction | Confirmé |
|------------|------------|----------|----------|
| 0x00000042 | 66 | Mode ECO | ✅ |
| 0x00000050 | 80 | Température + | ✅ |
| ... | ... | ... | ... |

### Configuration ESPHome

```yaml
# Si vous le souhaitez, partagez votre config générée
button:
  - platform: template
    name: "Mode ECO"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x0000
          command: 0x42
```

### Notes
Observations particulières, conditions de test, etc.
```

Ces codes seront ajoutés à une base de données communautaire (future fonctionnalité).

---

## 🔧 Développement

### Prérequis

- Git
- Python 3.8+
- ESPHome
- Home Assistant (pour tester)
- ESP32 + LED IR (pour tester le matériel)

### Setup du projet

```bash
# 1. Fork le projet sur GitHub

# 2. Clone votre fork
git clone https://github.com/VOTRE_USERNAME/Balboa-GS500z.git
cd Balboa-GS500z/esphome-tools/balboa-ir-discovery

# 3. Créer une branche
git checkout -b feature/ma-fonctionnalite

# 4. Installer les dépendances (pour le script Python)
pip install requests  # si nécessaire
```

### Structure du projet

```
balboa-ir-discovery/
├── balboa-ir-discovery.yaml    # Config ESPHome principale
├── automation/                 # Scripts d'automatisation
│   └── generate_remote_config.py
├── docs/                       # Documentation
├── examples/                   # Exemples et templates
└── README.md
```

### Tests

#### YAML (ESPHome)

```bash
# Valider la syntaxe
esphome config balboa-ir-discovery.yaml

# Compiler (sans uploader)
esphome compile balboa-ir-discovery.yaml
```

#### Python

```bash
# Tester le script
python3 automation/generate_remote_config.py --help

# Test avec fichier exemple
python3 automation/generate_remote_config.py \
  --json automation/discovered_codes.json.example \
  --output /tmp/test-remote.yaml

# Vérifier la sortie
esphome config /tmp/test-remote.yaml
```

#### Documentation

```bash
# Vérifier les liens markdown (si markdownlint installé)
markdownlint docs/*.md README.md

# Vérifier l'orthographe
# (utilisez votre éditeur ou un outil en ligne)
```

---

## 📝 Style de Code

### YAML (ESPHome)

- **Indentation** : 2 espaces (pas de tabs)
- **Nommage** : snake_case pour les IDs
- **Commentaires** : En français, clairs et concis
- **Organisation** : Sections séparées par des commentaires

**Exemple** :

```yaml
###############################################################################
# Section bien commentée
###############################################################################

button:
  # Commentaire explicatif
  - platform: template
    name: "Nom du Bouton"
    id: mon_bouton_id
    on_press:
      - logger.log: "Message clair"
```

### Python

- **Standard** : PEP 8
- **Type hints** : Utilisez-les partout
- **Docstrings** : Pour toutes les fonctions publiques
- **Imports** : Groupés (stdlib, externe, local)

**Exemple** :

```python
def ma_fonction(param: str) -> bool:
    """
    Description claire de la fonction.

    Args:
        param: Description du paramètre

    Returns:
        Description du retour
    """
    return True
```

### Markdown

- **Titres** : Hiérarchie cohérente (#, ##, ###)
- **Listes** : Utilisez - pour les listes à puces
- **Code** : Toujours entre triple backticks avec le langage
- **Liens** : Vérifiez qu'ils fonctionnent

### Commits

- **Format** : `type: description courte`
- **Types** :
  - `feat:` Nouvelle fonctionnalité
  - `fix:` Correction de bug
  - `docs:` Documentation
  - `style:` Formatage
  - `refactor:` Refactoring
  - `test:` Tests
  - `chore:` Maintenance

**Exemples** :

```bash
git commit -m "feat: Add smart scan mode"
git commit -m "fix: Correct NEC protocol encoding"
git commit -m "docs: Update SETUP.md wiring diagram"
```

---

## 🔄 Processus de Pull Request

### 1. Avant de soumettre

- [ ] Code testé localement
- [ ] Documentation mise à jour
- [ ] CHANGELOG.md mis à jour (section [Non publié])
- [ ] Pas de conflits avec main
- [ ] Commits clairs et atomiques

### 2. Créer la PR

**Titre** : `type: Description courte`

**Description** :

```markdown
## Description
Explication claire des changements.

## Type de changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Tests effectués
- [ ] Testé sur ESP32
- [ ] Compilation ESPHome réussie
- [ ] Documentation vérifiée
- [ ] Exemples testés

## Checklist
- [ ] Code suit le style du projet
- [ ] Self-review effectué
- [ ] Documentation mise à jour
- [ ] CHANGELOG.md mis à jour
- [ ] Pas de warnings/errors

## Captures d'écran
Si applicable.

## Informations supplémentaires
Tout autre contexte.
```

### 3. Après soumission

- Répondez aux commentaires de review
- Apportez les modifications demandées
- Soyez patient et respectueux

### 4. Merge

Une fois approuvée, votre PR sera mergée ! 🎉

Merci pour votre contribution !

---

## 🎁 Reconnaissance des Contributeurs

Tous les contributeurs seront mentionnés dans :
- README.md (section Contributors)
- Notes de release
- CHANGELOG.md

---

## 📞 Questions ?

- **Issues** : Pour les questions liées au code
- **Discussions** : Pour les questions générales
- **Discord** : (si disponible)

---

## 🙏 Merci !

Merci de contribuer à rendre cet outil encore meilleur pour toute la communauté !

**Chaque contribution compte, qu'elle soit grande ou petite.** ❤️

---

*Ce guide de contribution peut être mis à jour. Consultez toujours la version la plus récente sur GitHub.*
