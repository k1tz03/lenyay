"""Parler au modèle, sur sa propre machine — gratuitement, hors ligne.

C'est la contrepartie immédiate de la contribution : le modèle est déjà là,
téléchargé pour travailler la nuit ; rien n'empêche de s'en servir le jour.
Aucune requête ne sort de la machine, aucun compte, aucun quota.
"""

import logging

log = logging.getLogger("lenyay.chat")

SYSTEM = (
    "Tu es l'assistant de Lenyay. Tu réponds en français, de façon claire et "
    "utile, sans bavardage inutile. Si tu ne sais pas, tu le dis."
)
MAX_TOURS = 8  # on garde les derniers échanges : le contexte du modèle est court


def trim(history: list[dict], max_tours: int = MAX_TOURS) -> list[dict]:
    """Ne conserve que les derniers échanges (hors message système)."""
    if len(history) <= 1 + 2 * max_tours:
        return history
    return history[:1] + history[-2 * max_tours:]


def run() -> None:
    from common import config
    from worker.inference import _ensure_model

    from llama_cpp import Llama

    model_path = _ensure_model()
    print(f"\n  Chargement du modèle ({model_path.name})...")
    llm = Llama(model_path=str(model_path), n_ctx=4096, verbose=False)

    print("\n  Lenyay — l'IA sur ta machine")
    print("  Hors ligne, gratuit, rien n'est envoyé nulle part.")
    print("  Écris ta question, ou « quitter » pour sortir.\n")

    history: list[dict] = [{"role": "system", "content": SYSTEM}]
    while True:
        try:
            question = input("  toi > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  À bientôt.\n")
            return
        if not question:
            continue
        if question.lower() in {"quitter", "exit", "quit", "q"}:
            print("\n  À bientôt.\n")
            return

        history.append({"role": "user", "content": question})
        history = trim(history)
        print("\n  ia  > ", end="", flush=True)
        answer = ""
        try:
            for chunk in llm.create_chat_completion(
                messages=history, temperature=0.7,
                max_tokens=config.MAX_TOKENS, stream=True,
            ):
                piece = chunk["choices"][0].get("delta", {}).get("content", "")
                if piece:
                    answer += piece
                    print(piece, end="", flush=True)
        except KeyboardInterrupt:
            print("  [interrompu]")
        print("\n")
        history.append({"role": "assistant", "content": answer})
