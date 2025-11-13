#!/bin/bash

# Script pour bumper la version sans publier
# Usage: ./scripts/bump_version.sh [version]

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

if [ ! -f "custom_components/balboa_gs500z/manifest.json" ]; then
    echo -e "${RED}Erreur: Exécutez ce script depuis la racine du projet${NC}"
    exit 1
fi

CURRENT_VERSION=$(jq -r '.version' custom_components/balboa_gs500z/manifest.json)

if [ -z "$1" ]; then
    echo -e "${BLUE}Version actuelle: ${CURRENT_VERSION}${NC}"
    read -p "Nouvelle version: " NEW_VERSION
else
    NEW_VERSION=$1
fi

if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Format invalide. Utilisez: x.y.z${NC}"
    exit 1
fi

echo -e "${BLUE}Mise à jour: ${CURRENT_VERSION} → ${NEW_VERSION}${NC}"

# Mettre à jour manifest.json
jq ".version = \"${NEW_VERSION}\"" custom_components/balboa_gs500z/manifest.json > manifest.tmp
mv manifest.tmp custom_components/balboa_gs500z/manifest.json

echo -e "${GREEN}✓ Version mise à jour dans manifest.json${NC}"
echo ""
echo "N'oubliez pas de mettre à jour CHANGELOG.md !"
