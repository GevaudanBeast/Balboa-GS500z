#!/bin/bash

# Script de test de l'intégration
# Usage: ./scripts/test.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧪 Test de l'intégration Balboa GS500Z${NC}"
echo ""

# Test 1: Structure des fichiers
echo -e "${BLUE}[1/6] Vérification de la structure des fichiers...${NC}"
required_files=(
    "custom_components/balboa_gs500z/__init__.py"
    "custom_components/balboa_gs500z/manifest.json"
    "custom_components/balboa_gs500z/const.py"
    "custom_components/balboa_gs500z/config_flow.py"
    "custom_components/balboa_gs500z/coordinator.py"
    "custom_components/balboa_gs500z/tcp_client.py"
    "custom_components/balboa_gs500z/climate.py"
    "custom_components/balboa_gs500z/binary_sensor.py"
    "custom_components/balboa_gs500z/services.yaml"
    "custom_components/balboa_gs500z/strings.json"
    "custom_components/balboa_gs500z/translations/en.json"
    "custom_components/balboa_gs500z/translations/fr.json"
)

all_files_ok=true
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}  ✗ Manquant: $file${NC}"
        all_files_ok=false
    fi
done

if [ "$all_files_ok" = true ]; then
    echo -e "${GREEN}  ✓ Tous les fichiers requis sont présents${NC}"
else
    exit 1
fi

# Test 2: Syntaxe Python
echo -e "${BLUE}[2/6] Vérification de la syntaxe Python...${NC}"
if command -v python3 &> /dev/null; then
    python_errors=0
    for file in custom_components/balboa_gs500z/*.py; do
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            echo -e "${RED}  ✗ Erreur de syntaxe: $file${NC}"
            python_errors=$((python_errors + 1))
        fi
    done
    if [ $python_errors -eq 0 ]; then
        echo -e "${GREEN}  ✓ Syntaxe Python valide${NC}"
    else
        exit 1
    fi
else
    echo -e "${YELLOW}  ⚠ Python3 non trouvé, test ignoré${NC}"
fi

# Test 3: Validation manifest.json
echo -e "${BLUE}[3/6] Validation de manifest.json...${NC}"
if command -v jq &> /dev/null; then
    if jq empty custom_components/balboa_gs500z/manifest.json 2>/dev/null; then
        domain=$(jq -r '.domain' custom_components/balboa_gs500z/manifest.json)
        version=$(jq -r '.version' custom_components/balboa_gs500z/manifest.json)

        if [ "$domain" = "balboa_gs500z" ]; then
            echo -e "${GREEN}  ✓ manifest.json valide (domain: $domain, version: $version)${NC}"
        else
            echo -e "${RED}  ✗ Domain invalide: $domain${NC}"
            exit 1
        fi
    else
        echo -e "${RED}  ✗ manifest.json invalide${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  ⚠ jq non trouvé, test ignoré${NC}"
fi

# Test 4: Validation strings.json
echo -e "${BLUE}[4/6] Validation de strings.json...${NC}"
if command -v jq &> /dev/null; then
    if jq empty custom_components/balboa_gs500z/strings.json 2>/dev/null; then
        echo -e "${GREEN}  ✓ strings.json valide${NC}"
    else
        echo -e "${RED}  ✗ strings.json invalide${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  ⚠ jq non trouvé, test ignoré${NC}"
fi

# Test 5: Validation traductions
echo -e "${BLUE}[5/6] Validation des traductions...${NC}"
if command -v jq &> /dev/null; then
    translation_errors=0
    for file in custom_components/balboa_gs500z/translations/*.json; do
        if ! jq empty "$file" 2>/dev/null; then
            echo -e "${RED}  ✗ Traduction invalide: $file${NC}"
            translation_errors=$((translation_errors + 1))
        fi
    done
    if [ $translation_errors -eq 0 ]; then
        echo -e "${GREEN}  ✓ Toutes les traductions sont valides${NC}"
    else
        exit 1
    fi
else
    echo -e "${YELLOW}  ⚠ jq non trouvé, test ignoré${NC}"
fi

# Test 6: Recherche de problèmes courants
echo -e "${BLUE}[6/6] Recherche de problèmes courants...${NC}"
issues=0

# Recherche de print()
if grep -r "print(" custom_components/balboa_gs500z/*.py 2>/dev/null; then
    echo -e "${YELLOW}  ⚠ print() trouvés (utilisez logger à la place)${NC}"
    issues=$((issues + 1))
fi

# Recherche de TODO
todo_count=$(grep -r "TODO" custom_components/balboa_gs500z/*.py 2>/dev/null | wc -l || echo 0)
if [ "$todo_count" -gt 0 ]; then
    echo -e "${YELLOW}  ⚠ $todo_count TODO trouvés${NC}"
fi

if [ $issues -eq 0 ]; then
    echo -e "${GREEN}  ✓ Aucun problème majeur détecté${NC}"
fi

# Résumé
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Tous les tests sont passés avec succès !${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Version: ${BLUE}$(jq -r '.version' custom_components/balboa_gs500z/manifest.json)${NC}"
echo -e "Fichiers Python: ${BLUE}$(find custom_components/balboa_gs500z -name '*.py' | wc -l)${NC}"
echo -e "Lignes de code: ${BLUE}$(find custom_components/balboa_gs500z -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $1}')${NC}"
echo ""
