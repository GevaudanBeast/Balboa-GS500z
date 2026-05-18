# Contributing — Balboa GS500Z / GS501Z+

> **FR** : Merci de votre intérêt pour ce projet ! Ce document décrit
> les conventions et les flux de contribution.
>
> **EN**: Thanks for your interest in this project! This document
> describes contribution conventions and workflows.

---

## FR — Périmètre / EN — Scope

Ce projet **n'est pas un composant HACS**. Il regroupe :

This project is **not a HACS component**. It bundles:

1. Un **firmware ESPHome** (`esphome-tools/balboa-spa-control/`) pour
   ESP8266 NodeMCU. / An **ESPHome firmware** for ESP8266 NodeMCU.
2. Un **dashboard Lovelace** (`lovelace/`). / A **Lovelace dashboard**.
3. De la **documentation matérielle et protocoles** (MD à la racine). /
   **Hardware and protocol documentation** (root MD files).

Les contributions sont les bienvenues sur ces trois axes.

Contributions are welcome on all three axes.

---

## FR — Types de contributions / EN — Contribution types

### FR — Bugs / EN — Bugs

**FR** : Ouvrir une issue avec :

**EN**: Open an issue with:

- Description / Description
- Étapes de reproduction / Steps to reproduce
- Comportement attendu vs réel / Expected vs actual behavior
- Logs ESPHome (`esphome logs ...`) / ESPHome logs
- Version firmware (ex. `v1.5.3`) / Firmware version
- Modèle spa + panneau / Spa model + panel

### FR — Nouvelles fonctionnalités firmware / EN — New firmware features

**FR** : Discuter d'abord dans une issue avant d'ouvrir une PR. Le firmware
vise à rester compact (RAM ESP8266 limitée).

**EN**: Discuss in an issue before opening a PR. The firmware aims to
stay compact (limited ESP8266 RAM).

Bonnes pratiques / Best practices :

- Pas de `std::string` dans le hot path (parsing trames). / No `std::string`
  in the hot path (frame parsing).
- Buffers statiques (`char[]`, `uint8_t[]`). / Static buffers.
- Logger `INFO` en production (pas `DEBUG`). / `INFO` logger in production.
- Pas de `web_server` (économie RAM). / No `web_server` (RAM saving).

### FR — Documentation / EN — Documentation

**FR** : Les fichiers `.md` à la racine sont **bilingues FR/EN**. Toute
modification doit conserver les deux langues, soit côte à côte, soit
par sections distinctes (`## FR — ... / EN — ...`).

**EN**: Root `.md` files are **bilingual FR/EN**. Any modification must
keep both languages, either side by side or in separate sections.

---

## FR — Conventions de commit / EN — Commit conventions

**FR** : Format `<type>: <description courte>`.

**EN**: Format `<type>: <short description>`.

Types : `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`.

Exemples / Examples :

```
feat(esphome): ajout sensor pompe / add pump sensor
fix(esphome): GPIO16 -> GPIO15 pour opto_light / for opto_light
docs: pinout VL403 mis a jour / VL403 pinout updated
```

---

## FR — Branches / EN — Branches

- `main` : branche stable / stable branch
- `dev` : branche de développement / development branch
- `feat/*`, `fix/*` : branches de feature/fix / feature/fix branches

**FR** : Les PR ciblent `main` (ou `dev` si la fonctionnalité est expérimentale).

**EN**: PRs target `main` (or `dev` if the feature is experimental).

---

## FR — Tests / EN — Testing

**FR** : Avant de soumettre une PR firmware :

**EN**: Before submitting a firmware PR:

1. **FR** : `esphome config balboa-spa-control-v1.5.3.yaml` doit passer
   sans erreur. / Must pass without errors.
2. **FR** : Flasher sur un ESP8266 réel et vérifier au moins 24 h sans
   redémarrage. / Flash on a real ESP8266 and verify at least 24 h
   without restart.
3. **FR** : Vérifier que la RAM libre reste > 8 KB après plusieurs heures
   (`text_sensor` debug heap). / Check free heap stays > 8 KB after
   several hours.

---

## FR — Hardware / EN — Hardware

**FR** : Toute modification de pinout (RJ45, GPIO) doit être validée par
mesure multimètre et documentée dans `HARDWARE.md` + `BUS_J1_PROTOCOL.md`.

**EN**: Any pinout change (RJ45, GPIO) must be validated with multimeter
measurement and documented in `HARDWARE.md` + `BUS_J1_PROTOCOL.md`.

⚠️ **FR** : Ne jamais brancher directement le bus J1 5 V sur un GPIO ESP
sans diviseur de tension (1 kΩ + 2 kΩ).

⚠️ **EN**: Never connect the 5 V J1 bus directly to an ESP GPIO without
a voltage divider (1 kΩ + 2 kΩ).

---

## FR — Licence / EN — License

**FR** : En contribuant, vous acceptez que votre code soit publié sous
licence MIT (voir `LICENSE`).

**EN**: By contributing, you agree your code will be published under the
MIT license (see `LICENSE`).
