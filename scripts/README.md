# Scripts d'automatisation

Ce dossier contient les scripts pour faciliter le développement et la publication de l'intégration.

## 📜 Scripts disponibles

### `release.sh` - Publication de version

Script complet pour publier une nouvelle version de l'intégration.

```bash
# Mode interactif
./scripts/release.sh

# Version spécifique
./scripts/release.sh 1.0.1
```

**Actions effectuées :**
1. ✅ Vérifie que le dépôt est propre
2. ✅ Met à jour `manifest.json`
3. ✅ Met à jour `CHANGELOG.md`
4. ✅ Crée un commit
5. ✅ Crée un tag Git
6. ✅ Push les changements et le tag
7. ✅ Déclenche le workflow GitHub Actions

### `bump_version.sh` - Mise à jour de version

Script simple pour mettre à jour la version sans publier.

```bash
# Mode interactif
./scripts/bump_version.sh

# Version spécifique
./scripts/bump_version.sh 1.0.2
```

**Utilisation :**
- Développement en cours
- Préparation d'une release
- Mise à jour rapide du numéro de version

### `test.sh` - Tests de validation

Script de test local pour valider l'intégration.

```bash
./scripts/test.sh
```

**Tests effectués :**
1. ✅ Structure des fichiers
2. ✅ Syntaxe Python
3. ✅ Validation `manifest.json`
4. ✅ Validation `strings.json`
5. ✅ Validation traductions
6. ✅ Recherche de problèmes courants

### `install_dev.sh` - Installation développement

Script pour installer l'intégration en mode développement (lien symbolique).

```bash
# Détection automatique du chemin HA
./scripts/install_dev.sh

# Chemin spécifique
./scripts/install_dev.sh /path/to/homeassistant
```

**Chemins détectés automatiquement :**
- `~/.homeassistant` (installation standard)
- `/config` (Docker/HAOS)

## 🚀 Workflow de publication

### 1. Développement

```bash
# Installer en mode dev
./scripts/install_dev.sh

# Développer et tester
# ... modifications du code ...

# Tester localement
./scripts/test.sh
```

### 2. Préparation de la release

```bash
# Mettre à jour CHANGELOG.md manuellement
vim CHANGELOG.md

# Ajouter les changements dans la section [Unreleased]

# Commiter les changements
git add .
git commit -m "feat: nouvelle fonctionnalité"
```

### 3. Publication

```bash
# Lancer le script de release
./scripts/release.sh

# Choisir le type de version:
# - Patch: corrections de bugs (1.0.0 → 1.0.1)
# - Minor: nouvelles fonctionnalités (1.0.0 → 1.1.0)
# - Major: changements majeurs (1.0.0 → 2.0.0)

# Le script va:
# 1. Mettre à jour manifest.json
# 2. Mettre à jour CHANGELOG.md
# 3. Créer un commit
# 4. Créer un tag
# 5. Pusher vers GitHub

# GitHub Actions va ensuite:
# 1. Créer une GitHub Release
# 2. Générer le ZIP
# 3. Publier sur HACS
```

## 🔧 Configuration

### Prérequis

Les scripts nécessitent :
- `bash` 4.0+
- `git`
- `jq` (pour manipulation JSON)
- `python3` (pour tests de syntaxe)

### Installation des dépendances

**Ubuntu/Debian :**
```bash
sudo apt-get install jq python3
```

**macOS :**
```bash
brew install jq python3
```

**Arch Linux :**
```bash
sudo pacman -S jq python
```

### Rendre les scripts exécutables

```bash
chmod +x scripts/*.sh
```

## 📝 Conventions de versioning

Ce projet suit [Semantic Versioning](https://semver.org/) :

- **MAJOR** (x.0.0) : Changements incompatibles
- **MINOR** (0.x.0) : Nouvelles fonctionnalités compatibles
- **PATCH** (0.0.x) : Corrections de bugs

### Exemples

```
1.0.0 → 1.0.1  (correction de bug)
1.0.1 → 1.1.0  (nouvelle fonctionnalité)
1.1.0 → 2.0.0  (changement majeur incompatible)
```

## 🤖 GitHub Actions

Les workflows automatisés se déclenchent :

### `release.yml`
- **Déclencheur :** Push d'un tag `v*.*.*`
- **Actions :**
  - Validation de la version
  - Création du ZIP
  - Création de la GitHub Release
  - Publication HACS

### `validate.yml`
- **Déclencheur :** Push ou PR sur `main`/`dev`
- **Actions :**
  - Validation manifest.json
  - Vérification syntaxe Python
  - Validation structure fichiers
  - Tests de qualité

### `hassfest.yml`
- **Déclencheur :** Push ou PR sur `main`/`dev`
- **Actions :**
  - Validation officielle Home Assistant

## 📊 Exemples d'utilisation

### Scénario 1 : Correction rapide

```bash
# Corriger un bug
vim custom_components/balboa_gs500z/tcp_client.py

# Tester
./scripts/test.sh

# Commiter
git add .
git commit -m "fix: correction reconnexion TCP"

# Publier patch
./scripts/release.sh  # Choisir option 1 (Patch)
```

### Scénario 2 : Nouvelle fonctionnalité

```bash
# Développer la fonctionnalité
vim custom_components/balboa_gs500z/climate.py

# Mettre à jour CHANGELOG
vim CHANGELOG.md

# Tester
./scripts/test.sh

# Commiter
git add .
git commit -m "feat: ajout contrôle pompe"

# Publier minor
./scripts/release.sh  # Choisir option 2 (Minor)
```

### Scénario 3 : Tests avant publication

```bash
# Tester l'intégration
./scripts/test.sh

# Mettre à jour la version (sans publier)
./scripts/bump_version.sh 1.2.0

# Continuer le développement
# ... modifications ...

# Quand prêt, publier
./scripts/release.sh 1.2.0
```

## 🐛 Dépannage

### Erreur : "jq: command not found"

Installez jq :
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

### Erreur : "Permission denied"

Rendez les scripts exécutables :
```bash
chmod +x scripts/*.sh
```

### Erreur : "Not a git repository"

Assurez-vous d'être dans un dépôt Git initialisé :
```bash
git init
git remote add origin <url>
```

## 📚 Ressources

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [HACS](https://hacs.xyz/)

---

Pour toute question, consultez [CONTRIBUTING.md](../CONTRIBUTING.md)
