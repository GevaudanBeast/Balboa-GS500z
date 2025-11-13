#!/bin/bash

# Script d'installation pour le développement
# Ce script crée un lien symbolique vers Home Assistant pour le développement
# Usage: ./scripts/install_dev.sh [chemin_vers_home_assistant]

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 Installation en mode développement${NC}"
echo ""

# Déterminer le chemin Home Assistant
if [ -n "$1" ]; then
    HA_PATH="$1"
elif [ -d "$HOME/.homeassistant" ]; then
    HA_PATH="$HOME/.homeassistant"
elif [ -d "/config" ]; then
    HA_PATH="/config"
else
    echo -e "${YELLOW}Chemin Home Assistant non trouvé${NC}"
    read -p "Entrez le chemin vers votre installation HA: " HA_PATH
fi

# Vérifier que le chemin existe
if [ ! -d "$HA_PATH" ]; then
    echo -e "${RED}✗ Le chemin n'existe pas: $HA_PATH${NC}"
    exit 1
fi

echo -e "${BLUE}Chemin Home Assistant: ${HA_PATH}${NC}"

# Créer le dossier custom_components si nécessaire
CUSTOM_COMPONENTS_PATH="${HA_PATH}/custom_components"
if [ ! -d "$CUSTOM_COMPONENTS_PATH" ]; then
    echo -e "${BLUE}Création du dossier custom_components...${NC}"
    mkdir -p "$CUSTOM_COMPONENTS_PATH"
fi

# Chemin de l'intégration
INTEGRATION_PATH="${CUSTOM_COMPONENTS_PATH}/balboa_gs500z"

# Vérifier si l'intégration existe déjà
if [ -e "$INTEGRATION_PATH" ]; then
    echo -e "${YELLOW}⚠ L'intégration existe déjà${NC}"
    read -p "Voulez-vous la remplacer ? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INTEGRATION_PATH"
        echo -e "${GREEN}✓ Ancienne installation supprimée${NC}"
    else
        echo -e "${BLUE}Installation annulée${NC}"
        exit 0
    fi
fi

# Créer le lien symbolique
SOURCE_PATH="$(pwd)/custom_components/balboa_gs500z"
ln -s "$SOURCE_PATH" "$INTEGRATION_PATH"

echo -e "${GREEN}✓ Lien symbolique créé${NC}"
echo -e "  Source: ${BLUE}${SOURCE_PATH}${NC}"
echo -e "  Cible:  ${BLUE}${INTEGRATION_PATH}${NC}"
echo ""

# Vérifier la configuration
echo -e "${BLUE}Vérification...${NC}"
if [ -L "$INTEGRATION_PATH" ]; then
    echo -e "${GREEN}✓ Installation réussie${NC}"
else
    echo -e "${RED}✗ Erreur lors de la création du lien${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Installation terminée !${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo -e "  1. Redémarrer Home Assistant"
echo -e "  2. Aller dans Paramètres → Appareils et services"
echo -e "  3. Ajouter l'intégration 'Balboa GS500Z Spa'"
echo ""
echo -e "${BLUE}Pour activer les logs debug, ajoutez dans configuration.yaml:${NC}"
echo ""
echo -e "logger:"
echo -e "  default: info"
echo -e "  logs:"
echo -e "    custom_components.balboa_gs500z: debug"
echo ""
