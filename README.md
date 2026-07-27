# Lenyay

**Prononciation officielle : « leny-ay »** — anciennement *Essaim* (nom de
code « Leny's life »).

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
  models/*.gguf                                    data/lenyay.db  data/accepted/*.jsonl
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
(device_id + clé API) dans `.lenyay_device.json` à la racine (ignoré par git).
Pour repartir avec un appareil neuf, supprime ce fichier. La boucle survit aux
redémarrages du coordinateur : erreurs réseau et HTTP → pause de 5 s et
nouvel essai, jamais de crash.

**Migration depuis Essaim** : au premier démarrage sous le nom Lenyay, la base
`data/essaim.db` et l'identité `.essaim_device.json` existantes sont adoptées
automatiquement (renommées) — crédits et historique conservés.

## Configuration (variables d'environnement)

Les anciennes variables `ESSAIM_*` restent lues si la variante `LENYAY_*`
n'est pas définie, avec un avertissement de dépréciation.

| Variable | Défaut | Rôle |
|---|---|---|
| `LENYAY_MOCK` | `0` | `1` = worker en mode mock (équivalent : `--mock`) |
| `LENYAY_COORDINATOR_URL` | `http://127.0.0.1:8000` | URL du coordinateur vue par le worker |
| `LENYAY_HOST` / `LENYAY_PORT` | `127.0.0.1` / `8000` | Écoute du coordinateur (`python -m coordinator.app`) |
| `LENYAY_BATCH_SIZE` | `4` | Tâches par lot demandé (borné à 1-32) |
| `LENYAY_ATTEMPTS` | `2` | Tentatives max par problème (1 = pas de retry) |
| `LENYAY_MAX_TASKS` | `0` | S'arrêter après N tâches (0 = boucle infinie) |
| `LENYAY_TEMPERATURE` | `0.8` | Température d'échantillonnage |
| `LENYAY_MAX_TOKENS` | `640` | Tokens max générés par réponse (mode réel) |
| `LENYAY_MODEL_REPO` | `Qwen/Qwen2.5-1.5B-Instruct-GGUF` | Repo Hugging Face du modèle |
| `LENYAY_MODEL_PATTERN` | `q4_k_m` | Motif du fichier GGUF à choisir |
| `LENYAY_MOCK_ACCURACY` | `0.3` | Taux de bonnes réponses du mock |
| `LENYAY_DB` | `data/lenyay.db` | Base SQLite du coordinateur |
| `LENYAY_TASKS` | `data/tasks.jsonl` | Catalogue de tâches figé |
| `LENYAY_ACCEPTED_DIR` | `data/accepted` | Archive des traces acceptées |
| `LENYAY_DEVICE_FILE` | `.lenyay_device.json` | Identité persistée du worker |
| `LENYAY_MODELS_DIR` | `models` | Dossier des GGUF téléchargés |

## Tests

```bash
.venv/Scripts/python.exe -m pytest
```

53 tests couvrent le vérificateur (format `#### N`, virgules de milliers,
virgule décimale européenne, point final, dollars, réponse noyée dans une
phrase, décimaux, négatifs), la suite d'évaluation (scoring, sorties,
anti-contamination, comparaison) et la migration Lenyay (rétrocompatibilité
`ESSAIM_*`, adoption de la base et de l'identité) — le tout sur répertoires
temporaires, sans toucher à l'essaim en marche.

## Évaluation

Le jeu d'éval `data/eval_set.jsonl` (commité, figé une fois) : 200 problèmes
tirés du split **test** de GSM8K avec un seed fixe — jamais servis à l'essaim,
avec contrôle anti-contamination affiché au figeage. L'éval est strictement
déterministe (température 0, seed fixe) et réutilise le vérificateur du
coordinateur ainsi que le prompt système de production : deux évals du même
modèle donnent le même score, et v0.1 vs v0.2 se comparent honnêtement.

Évaluer un modèle (~30-40 min sur CPU pour 200 problèmes) :

```bash
.venv/Scripts/python.exe scripts/eval.py models/qwen2.5-1.5b-instruct-q4_k_m.gguf
```

Sortie : `results/eval_<modele>_<date>.json` (score global, détail par
problème, config figée, hash du jeu et du modèle) + résumé `.md` lisible.
Un checkpoint `.partial.jsonl` est écrit au fil de l'eau (filet en cas
d'interruption) puis supprimé à la fin. Options : `--limit N` (éval rapide,
**non comparable** à une éval complète — la comparaison la refuse),
`--label`, `--eval-set`, `--out-dir`.

Comparer deux évals (delta, problèmes gagnés/perdus ; refuse deux jeux
différents) :

```bash
.venv/Scripts/python.exe scripts/compare_evals.py results/eval_v01.json results/eval_v02.json
```

Re-figer le jeu d'éval (`scripts/seed_eval.py`) refuse d'écraser l'existant
sans `--force`, car cela invaliderait toutes les évals passées.

## Régénérer le jeu de tâches (optionnel)

`data/tasks.jsonl` (7 473 problèmes — l'intégralité du split train de GSM8K —
avec la réponse attendue) est commité et fait foi. Les `task_id` sont dérivés
de la position dans le split : re-seeder n'invalide jamais les crédits ni les
rollouts déjà en base. Pour le régénérer (option `--limit N` pour un
sous-ensemble) :

```bash
.venv/Scripts/python.exe -m pip install -r requirements-seed.txt
.venv/Scripts/python.exe scripts/seed_tasks.py
```

Le coordinateur charge le catalogue au démarrage : le redémarrer après un
re-seed (le worker encaisse la coupure et reprend tout seul).

## Structure du repo

```
coordinator/          FastAPI : endpoints, vérificateur, SQLite, dashboard
worker/               boucle du client : HTTP, génération (mock ou llama.cpp)
common/               schémas Pydantic partagés + configuration LENYAY_*
data/                 tasks.jsonl et eval_set.jsonl (figés, commités) ;
                      lenyay.db et accepted/ (générés)
scripts/              seed_tasks.py, seed_eval.py, eval.py, compare_evals.py
tests/                tests pytest (vérificateur + éval + migration)
results/              résultats d'éval (générés)
models/               GGUF téléchargés (ignoré par git)
.lenyay_device.json   identité du worker, créée au 1er lancement (ignorée par git)
```

## Hors périmètre de la phase 0

Pas d'entraînement, pas de mobile, pas de blockchain, pas d'auth avancée, pas
de Docker, pas de file distribuée, pas d'optimisation de perf — voir la
feuille de route pour la suite.
