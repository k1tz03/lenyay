"""Vérification des rollouts GSM8K : extraction du nombre final et comparaison.

Deux régimes d'extraction :
- la trace contient "####" (format GSM8K) → premier nombre après le DERNIER "####",
  avec tolérance sur les séparateurs de milliers (virgules et espaces) ;
- sinon → dernier nombre du texte (le modèle conclut généralement par sa réponse).
"""

import re

# Après "####" : on capture le jeton numérique complet (espaces de milliers en
# groupes de 3 stricts, virgules libres pour désambiguïser ensuite, décimales).
# En texte libre : seuls les groupements stricts sont tolérés — plus permissif,
# on fusionnerait des nombres voisins ("12 pommes 5" → 125).
_NUM_AFTER_HASH = re.compile(r"-?\$?(?:\d{1,3}(?: \d{3})+|\d[\d,]*)(?:\.\d+)?")
_NUM_FREE_TEXT = re.compile(r"-?\$?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")

_THOUSANDS = re.compile(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?")
_DECIMAL_COMMA = re.compile(r"-?\d+,\d{1,2}")


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


def _disambiguate_commas(token: str) -> str:
    """"1,000" → milliers ; "12,50" → virgule décimale ; "1,0000" → séparateurs retirés."""
    if _THOUSANDS.fullmatch(token):
        return token.replace(",", "")
    if _DECIMAL_COMMA.fullmatch(token):
        return token.replace(",", ".")
    return token.replace(",", "")


def extract_final_answer(trace: str) -> str | None:
    """Extrait la réponse numérique finale d'une trace, normalisée ("1,000" → "1000")."""
    if "####" in trace:
        tail = trace.rsplit("####", 1)[1]
        match = _NUM_AFTER_HASH.search(tail)
        if match is None:
            return None
        token = match.group().replace("$", "").replace("%", "").replace(" ", "")
        return _disambiguate_commas(token) or None
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
