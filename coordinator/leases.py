"""Bails de travail signés — la preuve qu'une tâche a bien été distribuée.

Sans bail, n'importe qui pourrait deviner les task_id (ils sont séquentiels) et
poster des réponses trouvées dans le dataset public GSM8K, sans jamais faire
tourner un modèle : crédits volés et surtout dataset de fine-tuning pollué.

Le bail est un HMAC sans état : il lie (appareil, tâche, échéance) et se vérifie
sans rien stocker côté serveur. Il ne protège pas le secret d'une réponse — il
prouve seulement que le coordinateur a bien confié CETTE tâche à CET appareil.
"""

import hmac
import re
import time
from hashlib import sha256

# Le bail vient du réseau : on n'accepte que la forme exacte attendue avant
# d'en faire quoi que ce soit (int() accepte espaces, underscores et chiffres
# unicode ; compare_digest refuse les str non-ASCII en levant TypeError).
_LEASE_RE = re.compile(r"^([0-9]{1,12})\.([0-9a-f]{32})$")


def _digest(secret: str, device_id: str, task_id: str, expiry: int) -> str:
    message = f"{device_id}|{task_id}|{expiry}".encode()
    return hmac.new(secret.encode(), message, sha256).hexdigest()[:32]


def issue(secret: str, device_id: str, task_id: str, ttl_seconds: int) -> str:
    expiry = int(time.time()) + ttl_seconds
    return f"{expiry}.{_digest(secret, device_id, task_id, expiry)}"


def verify(secret: str, device_id: str, task_id: str, lease: str) -> bool:
    match = _LEASE_RE.match(lease or "")
    if match is None:
        return False
    expiry = int(match.group(1))
    if expiry < time.time():
        return False
    # Comparaison sur des octets : jamais de TypeError, temps constant.
    return hmac.compare_digest(
        match.group(2).encode(), _digest(secret, device_id, task_id, expiry).encode()
    )
