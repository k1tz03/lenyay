"""Génération par vrai modèle : GGUF 1-3B via llama-cpp-python.

Le modèle est téléchargé automatiquement au premier lancement depuis
Hugging Face (repo et quantisation configurables via LENYAY_MODEL_REPO /
LENYAY_MODEL_PATTERN). Par défaut : Qwen2.5-1.5B-Instruct q4_k_m (~1 Go,
licence Apache-2.0).
"""

import logging
from pathlib import Path

from common import config
from common.schemas import Task

log = logging.getLogger("lenyay.worker")

# Public : scripts/eval.py réutilise ce prompt pour évaluer dans les mêmes
# conditions exactes que la production.
SYSTEM_PROMPT = (
    "You are a careful math tutor. Solve the problem step by step. "
    "End with the final numeric result on its own line, "
    "in the exact format: #### <number>"
)

# Quand la machine répond à un membre du réseau plutôt qu'à un exercice.
ASSISTANT_PROMPT = (
    "Tu es l'assistant de Lenyay, servi par l'ordinateur d'un membre du réseau. "
    "Tu réponds en français, clairement et utilement, sans bavardage. "
    "Si tu ne sais pas, tu le dis simplement."
)


def _ensure_model() -> Path:
    """Renvoie le chemin du GGUF local, en le téléchargeant si nécessaire.

    On liste les fichiers du repo HF et on choisit celui qui contient le motif
    de quantisation — plus robuste que de coder un nom de fichier en dur.
    """
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    pattern = config.MODEL_FILE_PATTERN.lower()

    existing = [p for p in config.MODELS_DIR.glob("*.gguf") if pattern in p.name.lower()]
    if existing:
        return existing[0]

    from huggingface_hub import hf_hub_download, list_repo_files

    files = list_repo_files(config.MODEL_REPO)
    candidates = sorted(
        f for f in files if f.lower().endswith(".gguf") and pattern in f.lower()
    )
    # Les gros modèles sont parfois découpés en "...-00001-of-00002.gguf" ;
    # on préfère un fichier entier.
    whole = [f for f in candidates if "-of-" not in f.lower()]
    if whole:
        candidates = whole
    if not candidates:
        raise RuntimeError(
            f"Aucun GGUF contenant '{pattern}' dans {config.MODEL_REPO}"
        )

    filename = candidates[0]
    log.info(
        "Téléchargement du modèle %s depuis %s (premier lancement uniquement)...",
        filename, config.MODEL_REPO,
    )
    path = hf_hub_download(
        repo_id=config.MODEL_REPO, filename=filename, local_dir=config.MODELS_DIR
    )
    return Path(path)


class LlamaGenerator:
    name = "llama"

    def __init__(self):
        model_path = _ensure_model()
        from llama_cpp import Llama

        log.info("Chargement du modèle %s ...", model_path.name)
        self._llm = Llama(model_path=str(model_path), n_ctx=2048, verbose=False)
        log.info("Modèle chargé.")

    def generate(self, task: Task) -> str:
        output = self._llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": task.prompt},
            ],
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
        return output["choices"][0]["message"]["content"] or ""

    def answer(self, question: str) -> str:
        """Répondre à la question d'un membre du réseau — pas un calcul vérifié,
        une vraie conversation. Ton posé, français, sans bavardage."""
        output = self._llm.create_chat_completion(
            messages=[
                {"role": "system", "content": ASSISTANT_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
            max_tokens=config.MAX_TOKENS,
        )
        return output["choices"][0]["message"]["content"] or ""
