"""Vérification des rollouts GSM8K : extraction du nombre final et comparaison.

Deux régimes d'extraction :
- la trace contient "####" (format GSM8K) → premier nombre après le DERNIER "####",
  avec tolérance sur les séparateurs de milliers (virgules et espaces) ;
- sinon → dernier nombre du texte (le modèle conclut généralement par sa réponse).
"""

import re

# Nombre à groupes de milliers, ou nombre simple, avec décimales optionnelles.
# Après "####" on tolère aussi l'espace comme séparateur de milliers ("1 000") ;
# en texte libre ce serait trop risqué (ça fusionnerait des nombres distincts).
_NUM_AFTER_HASH = re.compile(r"-?\$?(?:\d{1,3}(?:[ ,]\d{3})+|\d+)(?:\.\d+)?")
_NUM_FREE_TEXT = re.compile(r"-?\$?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")


def _normalize(candidate: str) -> str | None:
    s = (
        candidate.replace("$", "")
        .replace("%", "")
        .replace(",", "")
        .replace(" ", "")
        .strip()
        .rstrip(".")
    )
    return s or None


def extract_final_answer(trace: str) -> str | None:
    """Extrait la réponse numérique finale d'une trace, normalisée ("1,000" → "1000")."""
    if "####" in trace:
        tail = trace.rsplit("####", 1)[1]
        match = _NUM_AFTER_HASH.search(tail)
        return _normalize(match.group()) if match else None
    matches = _NUM_FREE_TEXT.findall(trace)
    return _normalize(matches[-1]) if matches else None


def verify(trace: str, expected: str) -> tuple[bool, str | None]:
    """Renvoie (accepté, nombre_extrait). Comparaison numérique : "3.50" == "3.5"."""
    extracted = extract_final_answer(trace)
    if extracted is None:
        return False, None
    expected_norm = _normalize(expected)
    if expected_norm is None:
        return False, extracted
    try:
        accepted = float(extracted) == float(expected_norm)
    except ValueError:
        accepted = extracted == expected_norm
    return accepted, extracted
