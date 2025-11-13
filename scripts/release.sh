#!/bin/bash

# Script de publication d'une nouvelle version de l'intégration Balboa GS500Z
# Usage: ./scripts/release.sh [version]
# Example: ./scripts/release.sh 1.0.1

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Vérifier que nous sommes à la racine du projet
if [ ! -f "custom_components/balboa_gs500z/manifest.json" ]; then
    log_error "Erreur: Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

# Récupérer la version actuelle
CURRENT_VERSION=$(jq -r '.version' custom_components/balboa_gs500z/manifest.json)
log_info "Version actuelle: ${CURRENT_VERSION}"

# Déterminer la nouvelle version
if [ -z "$1" ]; then
    log_warning "Aucune version spécifiée"
    echo ""
    echo "Quelle version voulez-vous publier ?"
    echo "  1) Patch (${CURRENT_VERSION} → $(echo $CURRENT_VERSION | awk -F. '{print $1"."$2"."$3+1}'))"
    echo "  2) Minor (${CURRENT_VERSION} → $(echo $CURRENT_VERSION | awk -F. '{print $1"."$2+1".0"}'))"
    echo "  3) Major (${CURRENT_VERSION} → $(echo $CURRENT_VERSION | awk -F. '{print $1+1".0.0"}'))"
    echo "  4) Personnalisée"
    echo ""
    read -p "Choix [1-4]: " choice

    case $choice in
        1)
            NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."$2"."$3+1}')
            ;;
        2)
            NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1"."$2+1".0"}')
            ;;
        3)
            NEW_VERSION=$(echo $CURRENT_VERSION | awk -F. '{print $1+1".0.0"}')
            ;;
        4)
            read -p "Entrez la nouvelle version (format: x.y.z): " NEW_VERSION
            ;;
        *)
            log_error "Choix invalide"
            exit 1
            ;;
    esac
else
    NEW_VERSION=$1
fi

# Valider le format de version
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log_error "Format de version invalide: ${NEW_VERSION}"
    log_error "Le format doit être: x.y.z (ex: 1.0.1)"
    exit 1
fi

log_info "Nouvelle version: ${NEW_VERSION}"

# Vérifier que la branche est propre
if [ -n "$(git status --porcelain)" ]; then
    log_error "Le dépôt a des changements non commités"
    git status --short
    exit 1
fi

# Vérifier qu'on est sur main ou dev
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "dev" ]]; then
    log_warning "Vous n'êtes pas sur main ou dev (branche actuelle: ${CURRENT_BRANCH})"
    read -p "Continuer quand même ? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Confirmation
echo ""
log_warning "Vous allez créer la version ${NEW_VERSION}"
read -p "Continuer ? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Annulé"
    exit 0
fi

# 1. Mettre à jour manifest.json
log_info "Mise à jour de manifest.json..."
jq ".version = \"${NEW_VERSION}\"" custom_components/balboa_gs500z/manifest.json > manifest.tmp
mv manifest.tmp custom_components/balboa_gs500z/manifest.json
log_success "manifest.json mis à jour"

# 2. Mettre à jour CHANGELOG.md
log_info "Mise à jour de CHANGELOG.md..."
TODAY=$(date +%Y-%m-%d)
sed -i "s/## \[Unreleased\]/## [Unreleased]\n\n## [${NEW_VERSION}] - ${TODAY}/" CHANGELOG.md 2>/dev/null || \
sed -i '' "s/## \[Unreleased\]/## [Unreleased]\n\n## [${NEW_VERSION}] - ${TODAY}/" CHANGELOG.md 2>/dev/null || \
log_warning "Impossible de mettre à jour CHANGELOG.md automatiquement. Mettez-le à jour manuellement."
log_success "CHANGELOG.md mis à jour"

# 3. Commiter les changements
log_info "Commit des changements..."
git add custom_components/balboa_gs500z/manifest.json CHANGELOG.md
git commit -m "Bump version to ${NEW_VERSION}"
log_success "Changements commités"

# 4. Créer le tag
log_info "Création du tag v${NEW_VERSION}..."
git tag -a "v${NEW_VERSION}" -m "Release version ${NEW_VERSION}"
log_success "Tag créé"

# 5. Push
echo ""
log_warning "Prêt à pusher les changements et le tag"
read -p "Pusher maintenant ? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Push des commits..."
    git push origin "${CURRENT_BRANCH}"
    log_success "Commits pushés"

    log_info "Push du tag..."
    git push origin "v${NEW_VERSION}"
    log_success "Tag pushé"

    echo ""
    log_success "✨ Release ${NEW_VERSION} publiée avec succès !"
    echo ""
    log_info "Le workflow GitHub Actions va maintenant:"
    log_info "  1. Créer une GitHub Release"
    log_info "  2. Générer le fichier ZIP"
    log_info "  3. Publier sur HACS"
    echo ""
    log_info "Suivez le workflow sur: https://github.com/GevaudanBeast/Balboa-GS500z/actions"
else
    log_info "Push annulé. Vous pouvez pusher manuellement avec:"
    echo "  git push origin ${CURRENT_BRANCH}"
    echo "  git push origin v${NEW_VERSION}"
fi

echo ""
log_success "Terminé !"
