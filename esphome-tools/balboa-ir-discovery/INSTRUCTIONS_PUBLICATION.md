# 🚀 Instructions de Publication v2.0.0

## ⚠️ Authentification Requise

La création de release sur GitHub nécessite une authentification que je ne peux pas fournir automatiquement.

Voici les **3 méthodes** pour publier la release v2.0.0 :

---

## 📋 Méthode 1 : Interface Web GitHub (Recommandée - 2 minutes)

### Étapes :

1. **Aller sur la page des releases** :
   ```
   https://github.com/GevaudanBeast/Balboa-GS500z/releases
   ```

2. **Cliquer sur "Draft a new release"** (bouton vert en haut à droite)

3. **Remplir le formulaire** :

   - **Choose a tag** : Taper `v2.0.0` et sélectionner "Create new tag: v2.0.0 on publish"

   - **Target** : Sélectionner la branche `claude/spa-data-node-red-015jdz6Akakd87vZ2K3s37AR` ou le commit `b49e630`

   - **Release title** :
     ```
     🎉 Balboa IR Discovery Tool v2.0.0 - Automatisation Post-Découverte
     ```

   - **Description** : Copier-coller le contenu entier de :
     ```
     esphome-tools/balboa-ir-discovery/RELEASE_NOTES.md
     ```

4. **Options** :
   - ✅ Cocher "Set as the latest release"
   - ❌ Ne PAS cocher "Set as a pre-release"

5. **Cliquer sur "Publish release"** ✅

---

## 💻 Méthode 2 : GitHub CLI (Si installé localement)

Si vous avez `gh` installé sur votre machine :

```bash
# 1. Clone le repository
git clone https://github.com/GevaudanBeast/Balboa-GS500z.git
cd Balboa-GS500z

# 2. Checkout la branche de release
git checkout claude/spa-data-node-red-015jdz6Akakd87vZ2K3s37AR

# 3. Créer le tag localement
git tag -a v2.0.0 b49e630 -m "Release v2.0.0 - Automatisation Post-Découverte

Cette version majeure transforme complètement l'expérience utilisateur en automatisant
le workflow complet de la découverte au contrôle en moins d'une heure !

Principales nouveautés :
- Export JSON automatique des codes découverts
- Script Python de génération automatique de config
- 8 exemples de dashboards Lovelace
- Guide post-découverte complet
- Fallback AP password configurable

Voir RELEASE_NOTES.md pour tous les détails."

# 4. Pousser le tag
git push origin v2.0.0

# 5. Créer la release avec gh CLI
gh release create v2.0.0 \
  --title "🎉 Balboa IR Discovery Tool v2.0.0 - Automatisation Post-Découverte" \
  --notes-file esphome-tools/balboa-ir-discovery/RELEASE_NOTES.md \
  --latest
```

---

## 🔧 Méthode 3 : API GitHub avec Token (Avancé)

Si vous avez un Personal Access Token GitHub :

```bash
# 1. Créer un token sur GitHub
# Aller sur : https://github.com/settings/tokens/new
# Permissions requises : repo (full control)

# 2. Exporter le token
export GITHUB_TOKEN="votre_token_ici"

# 3. Exécuter le script de publication
cd /chemin/vers/Balboa-GS500z/esphome-tools/balboa-ir-discovery

# Modifier publish_release.sh pour ajouter l'authentification :
# Ligne curl, ajouter : -H "Authorization: Bearer $GITHUB_TOKEN"

./publish_release.sh
```

---

## ✅ Vérification Post-Publication

Après avoir publié la release, vérifier :

1. **La release est visible** :
   ```
   https://github.com/GevaudanBeast/Balboa-GS500z/releases/tag/v2.0.0
   ```

2. **Le tag existe** :
   ```bash
   git ls-remote --tags origin | grep v2.0.0
   ```

3. **La release est marquée "Latest"** (badge vert)

4. **Les release notes sont complètes** (scroll pour tout voir)

---

## 🔗 Liens Placeholder à Mettre à Jour (AVANT de publier)

**IMPORTANT** : Avant de publier, remplacer `VotreUsername` dans les fichiers :

```bash
cd esphome-tools/balboa-ir-discovery

# Remplacer dans RELEASE_NOTES.md et docs/SETUP.md
sed -i 's|VotreUsername|GevaudanBeast|g' RELEASE_NOTES.md
sed -i 's|VotreUsername|GevaudanBeast|g' docs/SETUP.md

# Commit les changements
cd /home/user/Balboa-GS500z
git add esphome-tools/balboa-ir-discovery/RELEASE_NOTES.md
git add esphome-tools/balboa-ir-discovery/docs/SETUP.md
git commit -m "docs: Update GitHub username placeholders"
git push origin claude/spa-data-node-red-015jdz6Akakd87vZ2K3s37AR
```

---

## 📣 Après Publication

### 1. Mettre à jour la branche main (si applicable)

```bash
# Merger la branche de développement dans main
git checkout main
git merge claude/spa-data-node-red-015jdz6Akakd87vZ2K3s37AR
git push origin main
```

### 2. Annoncer la Release (Optionnel)

- **Forum Home Assistant** : Section ESPHome
- **Reddit** : r/homeassistant, r/ESPHome
- **Discord Home Assistant** : Canal #esphome

### 3. Nettoyer

```bash
# Supprimer la branche de développement (optionnel)
git branch -d claude/spa-data-node-red-015jdz6Akakd87vZ2K3s37AR
git push origin --delete claude/spa-data-node-red-015jdz6Akakd87vZ2K3s37AR
```

---

## 📊 Résumé des Fichiers Prêts

Tous les fichiers nécessaires sont prêts :

- ✅ **Tag v2.0.0** créé localement (commit `b49e630`)
- ✅ **RELEASE_NOTES.md** (306 lignes) prêt à copier
- ✅ **CHANGELOG.md** à jour avec dates
- ✅ **CONTRIBUTING.md** créé
- ✅ **docs/PUBLISHING.md** guide complet
- ✅ **PLACEHOLDER_LINKS.md** liste des liens à mettre à jour
- ✅ **Tous les commits** poussés sur la branche

---

## 🎯 Action Immédiate Recommandée

**Pour publier maintenant** :

1. Mettre à jour les placeholders (voir section ci-dessus)
2. Aller sur https://github.com/GevaudanBeast/Balboa-GS500z/releases/new
3. Remplir avec les informations de ce fichier
4. Copier RELEASE_NOTES.md dans la description
5. Publier !

**Temps estimé** : 5 minutes

---

## ❓ Questions ?

Voir le guide complet : `docs/PUBLISHING.md`

---

**Prêt à publier ! 🚀**
