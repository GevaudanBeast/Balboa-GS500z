# Balboa GS500Z/GS501Z+ — Home Assistant Integration

[![Validate](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Validate/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![Hassfest](https://github.com/GevaudanBeast/Balboa-GS500z/workflows/Hassfest/badge.svg)](https://github.com/GevaudanBeast/Balboa-GS500z/actions)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Integration Home Assistant pour la surveillance du spa Balboa GS500Z/GS501Z+ via
RS-485 (EW11A). Affiche la temperature, le mode et l'etat du chauffage en temps reel.

> **Etat du projet (avril 2026) :**
> La **lecture RS-485** via J18 est pleinement operationnelle.
> Le **controle** (consigne, mode) est en cours de developpement via le bus J1
> (protocole proprietaire Balboa + optocoupleurs EL817).
> Les commandes IR fonctionnent pour Light/Blower/Pump uniquement.

---

## Fonctionnalites actuelles

### Lecture (operationnelle)

- Temperature de l'eau en temps reel
- Consigne de temperature
- Mode de fonctionnement : Standard (ST), Economique (ECO), Sommeil (SL)
- Etat du chauffage (actif/inactif)
- Etat de la pompe (OFF/LOW/HIGH)
- Etat du blower
- Etat de la lumiere

### Controle (en developpement)

- Light / Blower / Pump : via codes IR (ESP8266)
- Temperature / Mode : en attente validation bus J1 (EL817)

---

## Prerequis

- Home Assistant 2023.1 ou superieur
- Spa Balboa GS500Z ou GS501Z+ avec panneau VL403
- Module RS-485 WiFi EW11A configure en mode TCP Server (port 8899, 9600 baud)

---

## Installation

### HACS (recommande)

1. HACS -> Integrations -> menu (...)  -> Depots personnalises
2. Ajouter : `https://github.com/GevaudanBeast/Balboa-GS500z`
3. Rechercher "Balboa GS500Z" et installer
4. Redemarrer Home Assistant

### Manuelle

Copier `custom_components/balboa_gs500z/` dans votre dossier `custom_components/`.

---

## Configuration

1. Configuration -> Integrations -> + Ajouter une integration
2. Rechercher "Balboa GS500Z Spa"
3. Renseigner l'adresse IP de l'EW11A et le port (defaut : 8899)

### Options

- **Taille fenetre glissante** (3-20) : nombre de trames pour validation (defaut : 5)
- **Garde-fou d'ordre** : valide les transitions ST->ECO->SL->ST (defaut : active)

---

## Entites creees

| Entite | Type | Description |
|--------|------|-------------|
| `climate.spa` | Climate | Temperature, consigne, mode |
| `binary_sensor.spa_heater` | Binary sensor | Etat chauffage |

---

## Configuration EW11A

| Parametre | Valeur |
|-----------|--------|
| Mode | TCP Server |
| Baud Rate | 9600 |
| Data Bits | 8 |
| Stop Bits | 1 |
| Parity | None |
| Port | 8899 |

---

## Exemples d'automatisations

```yaml
# Passer en mode ECO la nuit
automation:
  - alias: "Spa - Mode ECO la nuit"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.spa
        data:
          preset_mode: "eco"
```

---

## Architecture technique

```
custom_components/balboa_gs500z/
  __init__.py        # Setup integration
  manifest.json      # Metadonnees HACS
  const.py           # Constantes protocole
  config_flow.py     # Configuration UI
  tcp_client.py      # Client TCP EW11A — parsing trames RS-485
  coordinator.py     # Fenetre glissante + memoire SL (v5.8.4)
  climate.py         # Entite climate
  binary_sensor.py   # Entite heater
  services.yaml      # Definition services HA
  strings.json       # Traductions
  translations/      # EN + FR
```

---

## Protocole RS-485

Les trames sont au format `[643F2B...]` (27 octets, 54 chars hex).

| Byte | Role | Note |
|------|------|------|
| 3 | Temperature eau | valeur * 0.5 = degC |
| 5 | Consigne | valeur * 0.5 = degC |
| 17 | Pompe + Blower | bit7=blower, bits0-6=vitesse pompe |
| 19 | Heater | bit0 = ON/OFF (universel tous modes) |
| 20 | Lumiere | 0x02/0x03 = ON |
| 23 | Mode | 0x20=ST, 0x00=ECO, 0x40=SL, 0x60=transitoire |

Documentation complete : `PROTOCOL.md`

---

## Debogage

### Activer les logs debug

```yaml
logger:
  default: info
  logs:
    custom_components.balboa_gs500z: debug
```

### Tester la connexion

```bash
telnet <IP_EW11A> 8899
```

---

## Limitations connues

- **J18 est lecture seule** : les commandes set_temperature et set_mode ne
  sont pas implementees. Elles seront activees apres validation du bus J1.
- **WiFi ESP marginal** (~-77 dBm) : stable uniquement alimente en USB.
- **Mode SL** : peut etre confondu avec ECO apres stabilisation (b23=0x00).
  Resolu par la memoire SL de 120 secondes dans le coordinateur.

---

## Documentation

| Fichier | Contenu |
|---------|---------|
| `PROTOCOL.md` | Protocole RS-485 complet, mapping bytes, algo v5.8.4 |
| `HARDWARE.md` | Architecture materielle, cablage, composants |
| `APPROACHES_TESTED.md` | Toutes les pistes testees et leurs resultats |
| `IR_CODES.md` | Codes IR confirmes + resultats brute force |
| `BUS_J1_PROTOCOL.md` | Protocole bus J1/J2 + plan cablage EL817 |
| `INSTALL.md` | Instructions d'installation detaillees |

---

## Licence

MIT — voir `LICENSE`.

## Contribution

Issues et pull requests bienvenus.
Voir `CONTRIBUTING.md` pour les conventions.
