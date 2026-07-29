"""Retrait des données personnelles avant conservation pour l'apprentissage.

Rien de ce qui vient d'une conversation n'est stocké pour l'entraînement sans
passer par ici. Le parti pris : effacer large. Un faux positif (un nombre
banal masqué) ne coûte qu'un peu de contenu ; un faux négatif (un numéro de
carte qui fuite dans un modèle) est inacceptable.

Ce n'est pas une anonymisation certifiée — c'est une première barrière. Le
consentement et le tri humain restent les garanties principales.
"""

import re

# E-mails.
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# Numéros de téléphone français (avec ou sans espaces / points / tirets).
_PHONE = re.compile(r"\b(?:\+33|0)\s*[1-9](?:[\s.-]*\d{2}){4}\b")
# Suites de 13 à 19 chiffres (cartes, IBAN partiels), séparateurs tolérés.
_LONG_DIGITS = re.compile(r"\b(?:\d[\s-]?){13,19}\b")
# IBAN.
_IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?:[\s]?[A-Z0-9]{4}){2,7}\b")


def scrub(text: str) -> str:
    """Renvoie le texte débarrassé des identifiants directs les plus courants."""
    if not text:
        return text
    out = _EMAIL.sub("[courriel]", text)
    out = _IBAN.sub("[iban]", out)
    out = _LONG_DIGITS.sub("[numéro]", out)
    out = _PHONE.sub("[numéro]", out)
    return out
