# 🔗 Liens Placeholder à Mettre à Jour

Ce fichier liste tous les liens placeholder qui doivent être mis à jour avec votre vrai nom d'utilisateur GitHub avant la publication.

---

## 📋 Liste des Fichiers avec Placeholders

### 1. RELEASE_NOTES.md

**Ligne ~169** :
```markdown
# Actuel
git clone https://github.com/VotreUsername/Balboa-GS500z.git

# À remplacer par
git clone https://github.com/VOTRE_VRAI_USERNAME/Balboa-GS500z.git
```

**Lignes ~263-264** :
```markdown
# Actuel (liens relatifs - fonctionnent sur GitHub)
- **Issues** : [GitHub Issues](../../issues)
- **Discussions** : [GitHub Discussions](../../discussions)

# Option : Remplacer par des URLs absolues
- **Issues** : [GitHub Issues](https://github.com/VOTRE_USERNAME/Balboa-GS500z/issues)
- **Discussions** : [GitHub Discussions](https://github.com/VOTRE_USERNAME/Balboa-GS500z/discussions)
```

---

### 2. docs/SETUP.md

**Ligne ~27** (environ) :
```bash
# Actuel
git clone https://github.com/VotreUsername/Balboa-GS500z.git

# À remplacer par
git clone https://github.com/VOTRE_VRAI_USERNAME/Balboa-GS500z.git
```

---

### 3. README.md

**Section Support** (vers la fin du fichier) :
```markdown
# Actuel (liens relatifs - fonctionnent sur GitHub)
- **🐛 Issues** : [GitHub Issues](../../issues)
- **💬 Discussions** : [GitHub Discussions](../../discussions)

# Option : Remplacer par des URLs absolues
- **🐛 Issues** : [GitHub Issues](https://github.com/VOTRE_USERNAME/Balboa-GS500z/issues)
- **💬 Discussions** : [GitHub Discussions](https://github.com/VOTRE_USERNAME/Balboa-GS500z/discussions)
```

---

## 🔧 Remplacement Automatique

Vous pouvez remplacer tous les placeholders automatiquement avec :

```bash
# Définir votre nom d'utilisateur GitHub
GITHUB_USERNAME="VotreVraiUsername"

# Remplacer dans tous les fichiers .md
cd /chemin/vers/Balboa-GS500z/esphome-tools/balboa-ir-discovery

# Remplacer VotreUsername
find . -name "*.md" -type f -exec sed -i "s|VotreUsername|$GITHUB_USERNAME|g" {} \;

# Si vous voulez remplacer les liens relatifs par des absolus (optionnel)
find . -name "*.md" -type f -exec sed -i "s|\.\./\.\./issues|https://github.com/$GITHUB_USERNAME/Balboa-GS500z/issues|g" {} \;
find . -name "*.md" -type f -exec sed -i "s|\.\./\.\./discussions|https://github.com/$GITHUB_USERNAME/Balboa-GS500z/discussions|g" {} \;
```

**Note** : Sur macOS, utilisez `sed -i ''` au lieu de `sed -i`

---

## ✅ Vérification

Après remplacement, vérifier qu'il ne reste aucun placeholder :

```bash
# Vérifier VotreUsername
grep -r "VotreUsername" . --include="*.md"

# Vérifier les liens relatifs (si vous les avez remplacés)
grep -r "\.\./\.\./issues\|\.\./\.\./discussions" . --include="*.md"
```

Si aucune sortie, tous les placeholders sont remplacés ! ✅

---

## 📝 Recommandations

### Liens Relatifs vs Absolus

**Liens relatifs** (`../../issues`) :
- ✅ Fonctionnent automatiquement sur GitHub
- ✅ Fonctionnent même si vous forkez le projet
- ✅ Plus courts et plus propres
- ❌ Ne fonctionnent pas localement

**Liens absolus** (`https://github.com/user/repo/issues`) :
- ✅ Fonctionnent partout (local + GitHub)
- ✅ Plus explicites
- ❌ Spécifiques à votre repository
- ❌ Cassés si le projet est forké

**Recommandation** : Garder les liens relatifs pour les Issues et Discussions, mais remplacer `VotreUsername` dans les commandes git clone.

---

## 🎯 Action Requise Avant Publication

**Minimum requis** :
```bash
# Remplacer uniquement VotreUsername dans les git clone
sed -i 's|VotreUsername|VOTRE_VRAI_USERNAME|g' RELEASE_NOTES.md docs/SETUP.md
```

**Optionnel** :
- Remplacer les liens relatifs par des absolus si vous préférez

---

## 📊 Résumé

| Fichier | Placeholder | Action Requise |
|---------|-------------|----------------|
| **RELEASE_NOTES.md** | `VotreUsername` | ✅ Obligatoire |
| **RELEASE_NOTES.md** | `../../issues` | ⚪ Optionnel |
| **RELEASE_NOTES.md** | `../../discussions` | ⚪ Optionnel |
| **docs/SETUP.md** | `VotreUsername` | ✅ Obligatoire |
| **README.md** | `../../issues` | ⚪ Optionnel |
| **README.md** | `../../discussions` | ⚪ Optionnel |

**Total de remplacements obligatoires** : 2 fichiers (git clone URLs)

---

**Note** : Ce fichier (`PLACEHOLDER_LINKS.md`) peut être supprimé après la mise à jour des placeholders.
