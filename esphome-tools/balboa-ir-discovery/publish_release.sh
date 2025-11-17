#!/bin/bash

# Script de publication de la release v2.0.0 sur GitHub
# Utilise l'API GitHub pour créer la release

set -e

# Configuration
OWNER="GevaudanBeast"
REPO="Balboa-GS500z"
TAG="v2.0.0"
TARGET_COMMITISH="b49e630"  # Commit de la release
RELEASE_NAME="🎉 Balboa IR Discovery Tool v2.0.0 - Automatisation Post-Découverte"

# Chemin vers les release notes
RELEASE_NOTES_FILE="$(dirname "$0")/RELEASE_NOTES.md"

# Vérifier que le fichier existe
if [ ! -f "$RELEASE_NOTES_FILE" ]; then
    echo "❌ Erreur: RELEASE_NOTES.md introuvable à $RELEASE_NOTES_FILE"
    exit 1
fi

echo "📦 Publication de la release $TAG..."
echo "   Owner: $OWNER"
echo "   Repo: $REPO"
echo "   Commit: $TARGET_COMMITISH"
echo ""

# Lire le contenu des release notes
RELEASE_BODY=$(cat "$RELEASE_NOTES_FILE")

# Échapper le JSON
RELEASE_BODY_JSON=$(jq -Rs . <<< "$RELEASE_BODY")

# Créer le payload JSON
PAYLOAD=$(cat <<EOF
{
  "tag_name": "$TAG",
  "target_commitish": "$TARGET_COMMITISH",
  "name": "$RELEASE_NAME",
  "body": $RELEASE_BODY_JSON,
  "draft": false,
  "prerelease": false
}
EOF
)

# Afficher le payload pour debug (sans le body complet)
echo "📝 Payload de la release:"
echo "$PAYLOAD" | jq '{tag_name, target_commitish, name, draft, prerelease}'
echo ""

# URL de l'API GitHub
API_URL="https://api.github.com/repos/$OWNER/$REPO/releases"

echo "🚀 Création de la release sur GitHub..."
echo ""

# Créer la release via l'API
# Note: Dans l'environnement Claude Code, l'authentification est gérée par le proxy
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Séparer le code HTTP du body
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

# Vérifier le résultat
if [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ Release créée avec succès !"
    echo ""
    RELEASE_URL=$(echo "$BODY" | jq -r '.html_url')
    echo "🔗 URL de la release: $RELEASE_URL"
    echo ""
    echo "📊 Détails:"
    echo "$BODY" | jq '{id, name, tag_name, created_at, published_at, html_url}'
elif [ "$HTTP_CODE" -eq 422 ]; then
    echo "⚠️  La release ou le tag existe déjà"
    echo ""
    ERROR_MSG=$(echo "$BODY" | jq -r '.message // "Erreur inconnue"')
    echo "Message: $ERROR_MSG"
    echo ""
    echo "💡 Options:"
    echo "   1. Supprimer la release existante sur GitHub"
    echo "   2. Créer une nouvelle version (v2.0.1)"
    echo "   3. Mettre à jour la release existante manuellement"
else
    echo "❌ Erreur lors de la création de la release"
    echo "   Code HTTP: $HTTP_CODE"
    echo ""
    echo "Réponse:"
    echo "$BODY" | jq .
    exit 1
fi
