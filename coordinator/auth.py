"""Mots de passe et sessions — bibliothèque standard uniquement.

PBKDF2-HMAC-SHA256 avec sel aléatoire par hachage : pas de dépendance
supplémentaire, et le format stocké embarque ses paramètres pour pouvoir
augmenter le coût plus tard sans casser les comptes existants.
"""

import hashlib
import hmac
import secrets

# 600 000 itérations : la recommandation OWASP 2023 pour PBKDF2-SHA256.
_ITERATIONS = 600_000
_SCHEME = "pbkdf2-sha256"


def hash_password(password: str) -> str:
    """Renvoie « pbkdf2-sha256$itérations$sel$empreinte » (hex)."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"{_SCHEME}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Compare en temps constant ; tolère les formats invalides (→ False)."""
    try:
        scheme, iterations, salt_hex, digest_hex = stored.split("$")
        if scheme != _SCHEME:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, AttributeError):
        return False


def new_session_token() -> str:
    return secrets.token_urlsafe(32)
