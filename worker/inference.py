"""Génération par vrai modèle : GGUF 1-3B via llama-cpp-python.

Le modèle est téléchargé automatiquement au premier lancement depuis
Hugging Face (repo et quantisation configurables via LENYAY_MODEL_REPO /
LENYAY_MODEL_PATTERN). Par défaut : Qwen2.5-1.5B-Instruct q4_k_m (~1 Go,
licence Apache-2.0).
"""

import logging
import os
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


def _tier_model() -> tuple[str, str]:
    """Le modèle correspondant au palier servi par cette machine.

    LENYAY_MODEL_REPO reste prioritaire : on peut toujours imposer un modèle
    précis, quel que soit le palier déclaré.
    """
    if "LENYAY_MODEL_REPO" in os.environ or "ESSAIM_MODEL_REPO" in os.environ:
        return config.MODEL_REPO, config.MODEL_FILE_PATTERN
    return config.TIER_MODELS.get(
        config.WORKER_TIER, (config.MODEL_REPO, config.MODEL_FILE_PATTERN))


def _ensure_model() -> Path:
    """Renvoie le chemin du GGUF local, en le téléchargeant si nécessaire.

    On liste les fichiers du repo HF et on choisit celui qui contient le motif
    de quantisation — plus robuste que de coder un nom de fichier en dur.
    """
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    repo, pattern = _tier_model()
    pattern = pattern.lower()
    # La famille du modèle fait partie de la reconnaissance : sans elle, une
    # machine « costaud » réutiliserait le 1.5B déjà présent sur le disque.
    family = repo.split("/")[-1].lower().replace("-gguf", "")

    existing = sorted(p for p in config.MODELS_DIR.glob("*.gguf")
                      if pattern in p.name.lower() and family in p.name.lower())
    if existing:
        # Modèle découpé : il faut toutes les parties avant de s'en servir.
        head = existing[0]
        if "-of-" in head.name.lower():
            expected = int(head.name.lower().split("-of-")[1].split(".")[0])
            if len(existing) < expected:
                log.info("Modèle incomplet (%d/%d parties) — reprise du téléchargement",
                         len(existing), expected)
            else:
                return head
        else:
            return head

    from huggingface_hub import hf_hub_download, list_repo_files

    files = list_repo_files(repo)
    candidates = sorted(
        f for f in files if f.lower().endswith(".gguf") and pattern in f.lower()
    )
    if not candidates:
        raise RuntimeError(f"Aucun GGUF contenant '{pattern}' dans {repo}")

    # Les gros modèles sont découpés en "...-00001-of-00002.gguf". Un fichier
    # entier suffit ; sinon il faut TOUTES les parties, llama.cpp les recolle
    # à partir de la première.
    whole = [f for f in candidates if "-of-" not in f.lower()]
    wanted = [whole[0]] if whole else sorted(f for f in candidates if "-of-" in f.lower())

    log.info("Téléchargement du modèle depuis %s — %d fichier(s), premier lancement "
             "uniquement...", repo, len(wanted))
    first = None
    for name in wanted:
        path = Path(hf_hub_download(repo_id=repo, filename=name,
                                    local_dir=config.MODELS_DIR))
        first = first or path
        log.info("  %s (%.1f Go)", path.name, path.stat().st_size / 1024**3)
    return first


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

    def answer(self, question: str, context: list[dict] | None = None) -> str:
        """Répondre à un membre du réseau — pas un calcul vérifié, une vraie
        conversation. Le contexte est la mémoire du fil : sans lui, l'assistant
        oublierait ce qui vient d'être dit."""
        messages = [{"role": "system", "content": ASSISTANT_PROMPT}]
        for entry in (context or []):
            if entry.get("role") in {"user", "assistant"} and entry.get("content"):
                messages.append({"role": entry["role"], "content": entry["content"]})
        messages.append({"role": "user", "content": question})
        output = self._llm.create_chat_completion(
            messages=messages, temperature=0.7, max_tokens=config.MAX_TOKENS,
        )
        return output["choices"][0]["message"]["content"] or ""
