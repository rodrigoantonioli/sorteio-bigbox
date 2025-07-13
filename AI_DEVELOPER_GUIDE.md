# AI Developer Guide

This guide provides an overview of the **Sistema de Sorteios** project for developers building automation tools or integrations.

## Overview

The project is a Flask based web application used to manage prize drawings for the *Grupo Big Box Ultrabox*. It includes a cinematic Instagram drawing interface and management for stores, employees and prizes. Most features are tested with `unittest`.

## Repository Layout

```
app/                 Flask application package
  forms/             WTForms definitions
  models.py          SQLAlchemy models
  routes/            Blueprints (`main`, `auth`, `admin`, `manager`)
  static/            Front‑end assets (CSS/JS)
  templates/         Jinja2 templates
tests/               Test suite (`python tests/run_all_tests.py`)
run.py               Application factory and CLI commands
config.py            Configuration classes
```

## Key Models

- **Usuario** – user accounts with type `admin` or `assistente`.
- **Loja** – stores for the drawings.
- **Colaborador** – store employees.
- **Premio** – prizes with optional store association and image handling.
- **SorteioSemanal** – weekly store drawings.
- **SorteioColaborador** – drawings linking employees to prizes.
- **SorteioInstagram** – Instagram giveaways processed from comments.

All relationships are defined in `app/models.py`.

## Utilities

`app/utils.py` includes helpers such as:

- Date helpers (`get_brazil_datetime`, `format_brazil_date`)
- `parse_instagram_comments` – converts raw Instagram comment text into a dictionary of participants and tickets.
- `validar_arquivo_instagram` – simple validation for uploaded `.txt` comment files.

## Front-end

The Instagram giveaway screen is generated dynamically via JavaScript. The class `SorteioAnimado` in `app/static/js/script.js` constructs the modal layout, controls animations and updates the winners list.
Important methods include:

- `criarModal` – builds the three‑column layout used during the drawing.
- `popularFichaSorteio` and `atualizarFichaComResultados` – fill the information column.
- `adicionarGanhadorNaLista` and `atualizarListaGanhadoresFinais` – populate the winners column.
- `mostrarAlertaSucessoTopo` – visual feedback after saving results.

CSS rules for these elements live in `app/static/css/style.css`.

## Running and Testing

Create the app with `python run.py`. A database initialization command is included:

```bash
flask init-db
```

Tests are executed with:

```bash
python tests/run_all_tests.py
```

The current suite covers models, authentication flows and drawing logic, though some tests may fail depending on the environment.

## Further Reading

Additional documentation is available in:

- `README.md` – project introduction and instructions
- `API_DOCUMENTATION.md` – detailed API and model usage
- `INSTAGRAM_FEATURE.md` – description of the Instagram drawing feature

