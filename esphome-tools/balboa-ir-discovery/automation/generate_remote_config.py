#!/usr/bin/env python3
"""
Générateur automatique de configuration ESPHome pour télécommande IR Balboa

Ce script lit les codes IR découverts depuis Home Assistant et génère
automatiquement un fichier de configuration ESPHome prêt à l'emploi.

Usage:
  python3 generate_remote_config.py --json codes.json --output balboa-ir-remote.yaml
  python3 generate_remote_config.py --ha-entity sensor.balboa_ir_discovery_codes_decouverts_json

Auteur: Claude AI
License: MIT
Version: 1.0.0
"""

import json
import argparse
import sys
from typing import List, Dict, Any
from pathlib import Path

# Template de configuration ESPHome de base
ESPHOME_HEADER = """###############################################################################
# Balboa GS500Z - Télécommande IR
###############################################################################
# Configuration générée automatiquement à partir des codes découverts
# Date de génération: {generation_date}
# Nombre de codes: {code_count}
###############################################################################

substitutions:
  device_name: "balboa-ir-remote"
  friendly_name: "Balboa IR Remote"
  ir_transmitter_pin: "GPIO4"
  fallback_ap_password: "balboa123456"  # Mot de passe du point d'accès de secours

esphome:
  name: ${{device_name}}
  friendly_name: ${{friendly_name}}
  comment: "Télécommande IR pour spa Balboa GS500Z"

esp32:
  board: esp32dev
  framework:
    type: arduino

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  ap:
    ssid: "${{friendly_name}} Fallback"
    password: ${{fallback_ap_password}}

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password

web_server:
  port: 80

logger:
  level: INFO

captive_portal:

###############################################################################
# Émetteur IR
###############################################################################

remote_transmitter:
  pin: ${{ir_transmitter_pin}}
  carrier_duty_percent: 50%

###############################################################################
# Boutons de commande
###############################################################################

button:
"""

# Template pour un bouton NEC
BUTTON_TEMPLATE_NEC = """  # {name}
  - platform: template
    name: "{name}"
    icon: "{icon}"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x{address:04X}
          command: 0x{command:02X}
      - logger.log:
          format: "📡 Envoi {name}: 0x{code:08X}"
          level: INFO
"""

# Template pour un bouton générique (autres protocoles)
BUTTON_TEMPLATE_GENERIC = """  # {name}
  - platform: template
    name: "{name}"
    icon: "{icon}"
    on_press:
      - lambda: |-
          auto call = id(ir_transmitter).transmit();
          // Code: 0x{code:08X} - Protocole: {protocol}
          // TODO: Implémenter l'encodage pour {protocol}
          ESP_LOGI("IR", "Code {protocol} 0x{code:08X} - À implémenter");
"""


def parse_code(code_hex: str) -> int:
    """Parse un code hexadécimal en entier."""
    if code_hex.startswith("0x"):
        return int(code_hex, 16)
    return int(code_hex)


def guess_function(code: int, protocol: str) -> Dict[str, str]:
    """
    Devine la fonction probable d'un code basé sur sa valeur.

    Retourne un dict avec 'name' et 'icon'.
    """
    # Heuristiques basées sur les plages de codes communes
    if protocol == "NEC":
        # Plages typiques (à ajuster selon les découvertes)
        if 0x40 <= code <= 0x4F:
            return {"name": f"Mode {code:02X}", "icon": "mdi:cog"}
        elif 0x50 <= code <= 0x5F:
            if code % 2 == 0:
                return {"name": "Température +", "icon": "mdi:thermometer-plus"}
            else:
                return {"name": "Température -", "icon": "mdi:thermometer-minus"}
        elif 0x60 <= code <= 0x6F:
            return {"name": "Chauffage", "icon": "mdi:radiator"}

    # Par défaut
    return {"name": f"Code 0x{code:08X}", "icon": "mdi:remote"}


def generate_button_nec(code_data: Dict[str, Any], index: int, custom_names: Dict[str, str] = None) -> str:
    """Génère le code YAML pour un bouton NEC."""
    code = parse_code(code_data["code"])

    # Nom personnalisé ou auto-généré
    if custom_names and code_data["code"] in custom_names:
        name = custom_names[code_data["code"]]
        icon = "mdi:remote"
    else:
        func = guess_function(code, "NEC")
        name = func["name"]
        icon = func["icon"]

    # Pour NEC, l'adresse est dans les 16 bits supérieurs, la commande dans les 8 bits inférieurs
    address = (code >> 16) & 0xFFFF
    command = code & 0xFF

    return BUTTON_TEMPLATE_NEC.format(
        name=name,
        icon=icon,
        address=address,
        command=command,
        code=code
    )


def generate_button_generic(code_data: Dict[str, Any], index: int, custom_names: Dict[str, str] = None) -> str:
    """Génère le code YAML pour un bouton avec protocole non-NEC."""
    code = parse_code(code_data["code"])
    protocol = code_data["protocol"]

    # Nom personnalisé ou auto-généré
    if custom_names and code_data["code"] in custom_names:
        name = custom_names[code_data["code"]]
        icon = "mdi:remote"
    else:
        func = guess_function(code, protocol)
        name = func["name"]
        icon = func["icon"]

    return BUTTON_TEMPLATE_GENERIC.format(
        name=name,
        icon=icon,
        code=code,
        protocol=protocol
    )


def load_codes_from_json(json_file: Path) -> List[Dict[str, Any]]:
    """Charge les codes depuis un fichier JSON."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_codes_from_ha(entity_id: str, ha_url: str, ha_token: str) -> List[Dict[str, Any]]:
    """
    Charge les codes depuis Home Assistant via l'API.

    Args:
        entity_id: ID de l'entité sensor (ex: sensor.balboa_ir_discovery_codes_decouverts_json)
        ha_url: URL de Home Assistant (ex: http://homeassistant.local:8123)
        ha_token: Token d'accès longue durée
    """
    try:
        import requests
    except ImportError:
        print("❌ Module 'requests' non installé. Installez-le avec: pip install requests")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {ha_token}",
        "Content-Type": "application/json",
    }

    url = f"{ha_url}/api/states/{entity_id}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        state = data.get("state", "[]")

        # Le state est une chaîne JSON, il faut la parser
        codes = json.loads(state)
        return codes

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la connexion à Home Assistant: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur lors du parsing du JSON: {e}")
        sys.exit(1)


def load_custom_names(names_file: Path) -> Dict[str, str]:
    """
    Charge les noms personnalisés depuis un fichier JSON.

    Format: {"0x00000042": "Mode ECO", "0x00000050": "Température +"}
    """
    if not names_file.exists():
        return {}

    with open(names_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_config(codes: List[Dict[str, Any]], custom_names: Dict[str, str] = None) -> str:
    """Génère la configuration ESPHome complète."""
    from datetime import datetime

    # En-tête
    config = ESPHOME_HEADER.format(
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        code_count=len(codes)
    )

    # Générer les boutons
    for i, code_data in enumerate(codes):
        protocol = code_data.get("protocol", "NEC")

        if protocol == "NEC":
            config += generate_button_nec(code_data, i, custom_names)
        else:
            config += generate_button_generic(code_data, i, custom_names)

    # Section climate (si codes de température trouvés)
    temp_codes = [c for c in codes if 0x50 <= parse_code(c["code"]) <= 0x5F]
    if temp_codes:
        config += "\n###############################################################################\n"
        config += "# Climate Entity (optionnel - nécessite plus de configuration)\n"
        config += "###############################################################################\n\n"
        config += "# TODO: Implémenter une entité climate pour un contrôle plus intégré\n"

    return config


def main():
    parser = argparse.ArgumentParser(
        description="Génère automatiquement une configuration ESPHome pour télécommande IR Balboa"
    )

    # Sources de données
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--json",
        type=Path,
        help="Fichier JSON contenant les codes découverts"
    )
    source_group.add_argument(
        "--ha-entity",
        type=str,
        help="Entity ID du sensor Home Assistant (ex: sensor.balboa_ir_discovery_codes_decouverts_json)"
    )

    # Options Home Assistant
    parser.add_argument(
        "--ha-url",
        type=str,
        default="http://homeassistant.local:8123",
        help="URL de Home Assistant (défaut: http://homeassistant.local:8123)"
    )
    parser.add_argument(
        "--ha-token",
        type=str,
        help="Token d'accès longue durée Home Assistant"
    )

    # Options de sortie
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("balboa-ir-remote.yaml"),
        help="Fichier de sortie (défaut: balboa-ir-remote.yaml)"
    )

    # Noms personnalisés
    parser.add_argument(
        "--names",
        type=Path,
        help="Fichier JSON avec les noms personnalisés (optionnel)"
    )

    # Autres options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Afficher plus d'informations"
    )

    args = parser.parse_args()

    # Charger les codes
    print("📥 Chargement des codes découverts...")

    if args.json:
        if not args.json.exists():
            print(f"❌ Fichier {args.json} introuvable")
            sys.exit(1)
        codes = load_codes_from_json(args.json)
    else:
        if not args.ha_token:
            print("❌ --ha-token requis pour utiliser --ha-entity")
            sys.exit(1)
        codes = load_codes_from_ha(args.ha_entity, args.ha_url, args.ha_token)

    if not codes:
        print("⚠️  Aucun code découvert. Lancez d'abord la découverte !")
        sys.exit(1)

    print(f"✅ {len(codes)} code(s) chargé(s)")

    # Charger les noms personnalisés
    custom_names = {}
    if args.names:
        print(f"📥 Chargement des noms personnalisés depuis {args.names}...")
        custom_names = load_custom_names(args.names)
        print(f"✅ {len(custom_names)} nom(s) personnalisé(s) chargé(s)")

    # Générer la configuration
    print("⚙️  Génération de la configuration ESPHome...")
    config = generate_config(codes, custom_names)

    # Écrire le fichier
    print(f"💾 Écriture dans {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(config)

    print(f"✅ Configuration générée avec succès !")
    print(f"\n📄 Fichier: {args.output.absolute()}")
    print(f"📊 {len(codes)} bouton(s) créé(s)")

    # Instructions suivantes
    print("\n🚀 Prochaines étapes:")
    print("   1. Vérifiez le fichier généré")
    print("   2. Personnalisez les noms de boutons si nécessaire")
    print("   3. Flashez un nouvel ESP32 avec cette configuration")
    print("   4. Ajoutez l'appareil à Home Assistant")
    print("   5. Profitez de votre télécommande IR ! 🎉")

    if args.verbose:
        print(f"\n📋 Codes découverts:")
        for code_data in codes:
            print(f"   - {code_data['protocol']}: {code_data['code']} (décimal: {code_data.get('code_dec', 'N/A')})")


if __name__ == "__main__":
    main()
