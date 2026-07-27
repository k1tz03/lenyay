# Essaim — nom de code « Leny's life »

Réseau de calcul coopératif : les machines des membres génèrent la nuit des
**rollouts** (résolutions de problèmes GSM8K par un petit LLM local), un
coordinateur central **vérifie** les réponses, **crédite** les contributeurs et
**archive** les traces correctes — le futur jeu de données de fine-tuning.

Voir [ROADMAP.md](ROADMAP.md) pour la vision complète et les décisions actées.

## Architecture (phase 0 — tout tourne en local)

```
┌─────────────────┐   GET /work (prompts SEULS,     ┌─────────────────────┐
│     Worker      │    jamais la réponse)           │    Coordinateur     │
│                 │ ───────────────────────────────▶│  FastAPI + SQLite   │
│  llama.cpp      │                                 │                     │
│  (ou mock)      │ ◀─────────────────────────────── │  vérifie (#### N)  │
│                 │   POST /results → verdicts       │  crédite (+1/ok)   │
└───────┬─────────┘                                 └──────┬───────┬──────┘
        │                                                  │       │
        ▼                                                  ▼       ▼
  models/*.gguf                                    data/essaim.db  data/accepted/*.jsonl
  (téléchargé au                                   (journal +      (traces correctes =
   1er lancement)                                   crédits)        futur dataset)
```

Le worker ne reçoit **jamais** la réponse attendue : il ne peut être crédité
qu'en résolvant réellement le problème. Une tâche déjà résolue par un appareil
ne lui est pas re-servie et ne rapporte plus de crédit : catalogue épuisé →
le worker se met en pause. Dashboard sur `http://127.0.0.1:8000/`.

## Installation

Les commandes ci-dessous fonctionnent telles quelles sous PowerShell, cmd et
Git Bash (chemins avec `/`).

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
```

Pour le **mode réel** (vrai modèle, inutile en mode mock) :

```bash
.venv/Scripts/python.exe -m pip install -r requirements-llm.txt
```

## Lancer la démo (2 terminaux)

**Terminal 1 — le coordinateur :**

```bash
.venv/Scripts/python.exe -m coordinator.app
```

**Terminal 2 — le worker en mode mock** (traces simulées, ~30 % correctes,
aucun modèle chargé — idéal pour vérifier la plomberie) :

```bash
.venv/Scripts/python.exe -m worker.main --mock
```

**Terminal 2 — le worker en mode réel** (télécharge Qwen2.5-1.5B-Instruct
GGUF q4_k_m, ~1,1 Go, au premier lancement, puis résout les problèmes) :

```bash
.venv/Scripts/python.exe -m worker.main
```

Puis ouvre **http://127.0.0.1:8000/** : appareils vus, rollouts totaux, taux
d'acceptation et top contributeurs, rafraîchis toutes les 5 s. `Ctrl+C` arrête
le worker proprement avec un résumé de session. Les traces acceptées
s'accumulent dans `data/accepted/accepted-<date>.jsonl`.

Au premier lancement, le worker s'enregistre et persiste son identité
(device_id + clé API) dans `.essaim_device.json` à la racine (ignoré par git).
Pour repartir avec un appareil neuf, supprime ce fichier. La boucle survit aux
redémarrages du coordinateur : erreurs réseau et HTTP → pause de 5 s et
nouvel essai, jamais de crash.

## Configuration (variables d'environnement)

| Variable | Défaut | Rôle |
|---|---|---|
| `ESSAIM_MOCK` | `0` | `1` = worker en mode mock (équivalent : `--mock`) |
| `ESSAIM_COORDINATOR_URL` | `http://127.0.0.1:8000` | URL du coordinateur vue par le worker |
| `ESSAIM_HOST` / `ESSAIM_PORT` | `127.0.0.1` / `8000` | Écoute du coordinateur (`python -m coordinator.app`) |
| `ESSAIM_BATCH_SIZE` | `4` | Tâches par lot demandé (borné à 1-32) |
| `ESSAIM_ATTEMPTS` | `2` | Tentatives max par problème (1 = pas de retry) |
| `ESSAIM_MAX_TASKS` | `0` | S'arrêter après N tâches (0 = boucle infinie) |
| `ESSAIM_TEMPERATURE` | `0.8` | Température d'échantillonnage |
| `ESSAIM_MAX_TOKENS` | `640` | Tokens max générés par réponse (mode réel) |
| `ESSAIM_MODEL_REPO` | `Qwen/Qwen2.5-1.5B-Instruct-GGUF` | Repo Hugging Face du modèle |
| `ESSAIM_MODEL_PATTERN` | `q4_k_m` | Motif du fichier GGUF à choisir |
| `ESSAIM_MOCK_ACCURACY` | `0.3` | Taux de bonnes réponses du mock |
| `ESSAIM_DB` | `data/essaim.db` | Base SQLite du coordinateur |
| `ESSAIM_TASKS` | `data/tasks.jsonl` | Catalogue de tâches figé |
| `ESSAIM_ACCEPTED_DIR` | `data/accepted` | Archive des traces acceptées |
| `ESSAIM_DEVICE_FILE` | `.essaim_device.json` | Identité persistée du worker |
| `ESSAIM_MODELS_DIR` | `models` | Dossier des GGUF téléchargés |

## Tests

```bash
.venv/Scripts/python.exe -m pytest
```

29 tests couvrent le vérificateur (format `#### N`, virgules de milliers,
virgule décimale européenne, point final, dollars, réponse noyée dans une
phrase, décimaux, négatifs).

## Régénérer le jeu de tâches (optionnel)

`data/tasks.jsonl` (200 problèmes GSM8K + réponse attendue) est commité et fait
foi. Pour le régénérer :

```bash
.venv/Scripts/python.exe -m pip install -r requirements-seed.txt
.venv/Scripts/python.exe scripts/seed_tasks.py
```

## Structure du repo

```
coordinator/          FastAPI : endpoints, vérificateur, SQLite, dashboard
worker/               boucle du client : HTTP, génération (mock ou llama.cpp)
common/               schémas Pydantic partagés + configuration ESSAIM_*
data/                 tasks.jsonl (figé, commité) ; essaim.db et accepted/ (générés)
scripts/              seed_tasks.py
tests/                tests pytest du vérificateur
models/               GGUF téléchargés (ignoré par git)
.essaim_device.json   identité du worker, créée au 1er lancement (ignorée par git)
```

## Hors périmètre de la phase 0

Pas d'entraînement, pas de mobile, pas de blockchain, pas d'auth avancée, pas
de Docker, pas de file distribuée, pas d'optimisation de perf — voir la
feuille de route pour la suite.
