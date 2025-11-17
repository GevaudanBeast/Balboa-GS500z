# 📦 Guide de Publication - Balboa IR Discovery Tool

Ce guide explique comment publier une nouvelle version du projet sur GitHub.

---

## 📋 Prérequis

Avant de publier une release :

1. ✅ Tous les changements sont commités
2. ✅ CHANGELOG.md est à jour avec la nouvelle version
3. ✅ Les dates sont correctes dans CHANGELOG.md
4. ✅ RELEASE_NOTES.md est créé pour cette version
5. ✅ Tous les tests fonctionnels sont passés
6. ✅ La documentation est à jour
7. ✅ Le tag Git est créé localement

---

## 🚀 Processus de Publication

### Étape 1 : Vérification Finale

```bash
# Vérifier le statut Git
git status

# Vérifier que le tag existe localement
git tag -l "v*"

# Vérifier le contenu du tag
git show v2.0.0
```

### Étape 2 : Pousser le Tag vers GitHub

```bash
# Pousser le tag vers GitHub
git push origin v2.0.0

# Vérifier que le tag est bien sur GitHub
git ls-remote --tags origin
```

### Étape 3 : Créer la Release sur GitHub

#### Via l'Interface Web GitHub

1. **Aller sur la page du repository**
   - `https://github.com/VOTRE_USERNAME/Balboa-GS500z`

2. **Cliquer sur "Releases"**
   - Dans le menu de droite ou via `/releases`

3. **Cliquer sur "Draft a new release"**

4. **Remplir le formulaire** :
   - **Tag version** : Sélectionner `v2.0.0`
   - **Release title** : `🎉 Balboa IR Discovery Tool v2.0.0 - Automatisation Post-Découverte`
   - **Description** : Copier le contenu de `RELEASE_NOTES.md`

5. **Options** :
   - ✅ Cocher "Set as the latest release"
   - ❌ Ne PAS cocher "Set as a pre-release"

6. **Cliquer sur "Publish release"**

#### Via GitHub CLI (si disponible)

```bash
# Créer la release avec gh CLI
gh release create v2.0.0 \
  --title "🎉 Balboa IR Discovery Tool v2.0.0 - Automatisation Post-Découverte" \
  --notes-file RELEASE_NOTES.md \
  --latest
```

### Étape 4 : Vérifications Post-Publication

1. **Vérifier la release sur GitHub**
   - La release apparaît sur la page principale
   - Le tag est visible dans les tags
   - Les notes de release sont complètes

2. **Vérifier les liens** (mettre à jour si nécessaire)
   - Issues : `https://github.com/VOTRE_USERNAME/Balboa-GS500z/issues`
   - Discussions : `https://github.com/VOTRE_USERNAME/Balboa-GS500z/discussions`

3. **Tester le téléchargement**
   - Télécharger le ZIP source depuis la release
   - Vérifier que tous les fichiers sont présents

---

## 📝 Liens Placeholder à Mettre à Jour

Les fichiers suivants contiennent des liens génériques qui doivent être mis à jour avec votre nom d'utilisateur GitHub :

### RELEASE_NOTES.md

```markdown
# Ligne 169 (environ)
git clone https://github.com/VotreUsername/Balboa-GS500z.git

# À remplacer par :
git clone https://github.com/VOTRE_VRAI_USERNAME/Balboa-GS500z.git
```

```markdown
# Lignes 263-265
- **Issues** : [GitHub Issues](../../issues)
- **Discussions** : [GitHub Discussions](../../discussions)
- **Forum Home Assistant** : Recherchez "Balboa IR Discovery"
```

**Note** : Les liens relatifs `../../issues` et `../../discussions` fonctionneront automatiquement sur GitHub, mais vous pouvez les remplacer par des URLs absolues si nécessaire :
```markdown
- **Issues** : https://github.com/VOTRE_USERNAME/Balboa-GS500z/issues
- **Discussions** : https://github.com/VOTRE_USERNAME/Balboa-GS500z/discussions
```

### README.md

Vérifier les sections :
- Support / Issues
- Contribution
- Liens vers discussions

### Autres fichiers

Rechercher tous les fichiers avec :
```bash
cd /home/user/Balboa-GS500z/esphome-tools/balboa-ir-discovery
grep -r "VotreUsername" .
grep -r "../../issues" .
grep -r "../../discussions" .
```

---

## 🔄 Workflow Complet de Release

### Pour une Release Majeure (ex: v2.0.0)

```bash
# 1. Créer une branche de release
git checkout -b release/v2.0.0

# 2. Mettre à jour CHANGELOG.md
# - Ajouter la nouvelle version
# - Mettre la date du jour

# 3. Créer RELEASE_NOTES.md
# - Rédiger les notes complètes

# 4. Commit les changements
git add CHANGELOG.md RELEASE_NOTES.md
git commit -m "chore: Prepare v2.0.0 release"

# 5. Merger dans main
git checkout main
git merge release/v2.0.0

# 6. Créer le tag
git tag -a v2.0.0 -m "Release v2.0.0 - Automatisation Post-Découverte"

# 7. Pousser vers GitHub
git push origin main
git push origin v2.0.0

# 8. Créer la release sur GitHub (interface web ou CLI)
```

### Pour une Release Mineure (ex: v2.1.0)

Même processus, mais les changements sont généralement plus petits.

### Pour un Patch (ex: v2.0.1)

```bash
# 1. Fix le bug
git checkout -b hotfix/v2.0.1

# 2. Commit le fix
git commit -am "fix: Correct typo in SETUP.md"

# 3. Mettre à jour CHANGELOG.md
# Ajouter ## [2.0.1] - YYYY-MM-DD

# 4. Créer le tag
git tag -a v2.0.1 -m "Release v2.0.1 - Bug fixes"

# 5. Pousser
git push origin hotfix/v2.0.1
git push origin v2.0.1
```

---

## 📢 Communication de la Release

Après publication, considérer :

1. **Forum Home Assistant**
   - Poster dans la section ESPHome
   - Titre : "Balboa GS500z - IR Discovery Tool v2.0.0"
   - Expliquer les nouveautés

2. **Reddit**
   - r/homeassistant
   - r/ESPHome
   - Partager le lien de la release

3. **Twitter/X** (si applicable)
   - Annoncer la release
   - Mentionner @homeassistant @esphome

4. **Discord Home Assistant**
   - Canal #esphome
   - Annoncer brièvement

---

## ✅ Checklist de Publication

Avant de publier, vérifier :

- [ ] Code compilé et testé
- [ ] Documentation à jour
- [ ] CHANGELOG.md avec date correcte
- [ ] RELEASE_NOTES.md créé
- [ ] Numéro de version cohérent partout
- [ ] Tag Git créé et annoté
- [ ] Pas de secrets ou credentials dans le code
- [ ] Fichiers .example présents
- [ ] LICENSE à jour
- [ ] README.md explique la nouvelle version
- [ ] Screenshots/GIFs à jour (si applicable)

Après publication :

- [ ] Release visible sur GitHub
- [ ] Tag présent dans la liste
- [ ] ZIP téléchargeable
- [ ] Notes de release complètes
- [ ] Lien fonctionnel
- [ ] Annonce sur les forums (optionnel)

---

## 🐛 Rollback en cas de Problème

Si un problème est découvert après publication :

```bash
# 1. Supprimer la release sur GitHub (interface web)
# 2. Supprimer le tag distant
git push --delete origin v2.0.0

# 3. Supprimer le tag local
git tag -d v2.0.0

# 4. Corriger le problème
# 5. Recréer le tag avec un patch (v2.0.1)
```

---

## 📚 Références

- [Semantic Versioning](https://semver.org/lang/fr/)
- [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

**Créé pour Balboa IR Discovery Tool**
*Version du guide : 1.0.0*
