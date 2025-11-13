# GitHub Actions Workflows

Ce document décrit les workflows automatisés configurés pour ce projet.

## 📋 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                   Push to main/dev                      │
│                           │                             │
│                           ▼                             │
│              ┌────────────────────────┐                 │
│              │  Validate Workflow     │                 │
│              │  - Check Python        │                 │
│              │  - Validate manifest   │                 │
│              │  - Check structure     │                 │
│              └────────────────────────┘                 │
│                           │                             │
│                           ▼                             │
│              ┌────────────────────────┐                 │
│              │  Hassfest Workflow     │                 │
│              │  - HA validation       │                 │
│              └────────────────────────┘                 │
│                           │                             │
│                           ▼                             │
│              ┌────────────────────────┐                 │
│              │  HACS Validation       │                 │
│              │  - HACS compliance     │                 │
│              └────────────────────────┘                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Push tag v*.*.*                      │
│                           │                             │
│                           ▼                             │
│              ┌────────────────────────┐                 │
│              │  Release Workflow      │                 │
│              │  - Verify version      │                 │
│              │  - Create ZIP          │                 │
│              │  - Create Release      │                 │
│              │  - Publish to HACS     │                 │
│              └────────────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Workflows détaillés

### 1. `validate.yml` - Validation Continue

**Déclencheurs :**
- Push sur `main` ou `dev`
- Pull Request vers `main` ou `dev`

**Jobs :**

#### Job 1: `validate`
Valide la structure et la syntaxe de l'intégration.

**Étapes :**
1. **Checkout** - Clone le code
2. **Setup Python** - Python 3.11
3. **Install dependencies** - Home Assistant + voluptuous
4. **Validate manifest** - Vérifie les clés requises
5. **Check Python syntax** - Compile tous les .py
6. **Check file structure** - Vérifie les fichiers obligatoires
7. **Validate strings.json** - JSON valide
8. **Check for common issues** - print(), TODO, etc.

#### Job 2: `hacs-validate`
Valide la compatibilité HACS.

**Étapes :**
1. **Checkout** - Clone le code
2. **HACS validation** - Utilise l'action officielle HACS

**Badges de statut :**
```markdown
![Validate](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Validate/badge.svg)
```

---

### 2. `hassfest.yml` - Validation Home Assistant

**Déclencheurs :**
- Push sur `main` ou `dev`
- Pull Request vers `main` ou `dev`

**Jobs :**

#### Job: `hassfest`
Utilise l'outil officiel de validation Home Assistant.

**Étapes :**
1. **Checkout** - Clone le code
2. **Hassfest** - Validation officielle HA

**Ce qui est vérifié :**
- Structure du manifest.json
- Conformité avec les standards HA
- Dépendances valides
- Structure des fichiers

**Badge de statut :**
```markdown
![Hassfest](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Hassfest/badge.svg)
```

---

### 3. `release.yml` - Publication Automatique

**Déclencheurs :**
- Push d'un tag `v*.*.*` (ex: `v1.0.1`)

**Jobs :**

#### Job: `release`
Crée automatiquement une GitHub Release.

**Étapes :**

1. **Checkout code**
   - Clone le repository avec le tag

2. **Get version from tag**
   - Extrait la version du tag (ex: `v1.0.1` → `1.0.1`)

3. **Verify version in manifest**
   - Compare la version du tag avec manifest.json
   - **Échoue si les versions ne correspondent pas**

4. **Create ZIP archive**
   - Crée `balboa_gs500z-X.Y.Z.zip`
   - Contient tout le dossier `custom_components/balboa_gs500z/`

5. **Extract changelog**
   - Extrait les notes de version depuis CHANGELOG.md
   - Section correspondant à la version

6. **Create GitHub Release**
   - Crée une release sur GitHub
   - Attache le fichier ZIP
   - Ajoute les notes de version

7. **Update HACS**
   - HACS détecte automatiquement la nouvelle release

**Badge de statut :**
```markdown
![Release](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Release/badge.svg)
```

---

## 🚀 Utilisation

### Publier une nouvelle version

```bash
# Option 1: Utiliser le script de release (recommandé)
./scripts/release.sh 1.0.1

# Option 2: Manuellement
git tag -a v1.0.1 -m "Release 1.0.1"
git push origin v1.0.1
```

**Le workflow `release.yml` va :**
1. Vérifier que `manifest.json` a la version 1.0.1
2. Créer le ZIP
3. Créer la GitHub Release
4. Publier pour HACS

### Tester les workflows localement

#### Installer act (outil de test local)
```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

#### Tester le workflow validate
```bash
act -j validate
```

#### Tester le workflow release
```bash
act -j release -e event.json
```

---

## 📊 Statut des workflows

Vous pouvez voir le statut des workflows :
- **Sur GitHub** : [Actions tab](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
- **Dans le README** : Badges de statut

### Ajouter des badges au README

```markdown
## Status

![Validate](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Validate/badge.svg)
![Hassfest](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Hassfest/badge.svg)
![Release](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Release/badge.svg)
```

---

## 🔒 Secrets GitHub

Aucun secret n'est requis pour les workflows actuels. Le `GITHUB_TOKEN` est fourni automatiquement.

Si vous ajoutez des fonctionnalités nécessitant des secrets :

1. Allez dans **Settings** → **Secrets and variables** → **Actions**
2. Cliquez sur **New repository secret**
3. Ajoutez vos secrets

---

## 🐛 Dépannage

### Le workflow de release échoue

**Erreur : "version mismatch"**
```
Error: manifest.json version (1.0.0) does not match tag version (1.0.1)
```

**Solution :**
Assurez-vous que `manifest.json` contient la bonne version avant de créer le tag.

```bash
# Utiliser le script de release qui fait tout automatiquement
./scripts/release.sh 1.0.1
```

---

### Le workflow validate échoue

**Erreur : "Python syntax error"**
```
✗ Erreur de syntaxe: custom_components/balboa_gs500z/tcp_client.py
```

**Solution :**
1. Testez localement : `python3 -m py_compile custom_components/balboa_gs500z/tcp_client.py`
2. Corrigez l'erreur
3. Committez et poussez

---

### HACS ne détecte pas la nouvelle version

**Causes possibles :**
1. Le tag n'est pas au format `vX.Y.Z`
2. La GitHub Release n'a pas été créée
3. Le fichier ZIP est manquant

**Solution :**
1. Vérifiez que le workflow `release.yml` s'est exécuté sans erreur
2. Vérifiez que la release apparaît sur GitHub
3. Attendez quelques minutes (HACS met à jour toutes les heures)

---

## 📝 Personnalisation

### Ajouter un nouveau workflow

1. Créez un fichier `.github/workflows/mon_workflow.yml`
2. Définissez les déclencheurs et jobs
3. Testez localement avec `act`
4. Committez et poussez

### Exemple : Workflow de test

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: ./scripts/test.sh
```

---

## 📚 Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [HACS Integration](https://hacs.xyz/docs/publish/integration)
- [Home Assistant Hassfest](https://developers.home-assistant.io/docs/development_validation)

---

Pour toute question, ouvrez une issue sur GitHub.
