"""Bails de travail signés — la preuve qu'une tâche a bien été distribuée.

Sans bail, n'importe qui pourrait deviner les task_id (ils sont séquentiels) et
poster des réponses trouvées dans le dataset public GSM8K, sans jamais faire
tourner un modèle : crédits volés et surtout dataset de fine-tuning pollué.

Le bail est un HMAC sans état : il lie (appareil, tâche, échéance) et se vérifie
sans rien stocker côté serveur. Il ne protège pas le secret d'une réponse — il
prouve seulement que le coordinateur a bien confié CETTE tâche à CET appareil.
"""

import hmac
import time
from hashlib import sha256


def _digest(secret: str, device_id: str, task_id: str, expiry: int) -> str:
    message = f"{device_id}|{task_id}|{expiry}".encode()
    return hmac.new(secret.encode(), message, sha256).hexdigest()[:32]


def issue(secret: str, device_id: str, task_id: str, ttl_seconds: int) -> str:
    expiry = int(time.time()) + ttl_seconds
    return f"{expiry}.{_digest(secret, device_id, task_id, expiry)}"


def verify(secret: str, device_id: str, task_id: str, lease: str) -> bool:
    if not lease or "." not in lease:
        return False
    raw_expiry, _, signature = lease.partition(".")
    try:
        expiry = int(raw_expiry)
    except ValueError:
        return False
    if expiry < time.time():
        return False
    return hmac.compare_digest(signature, _digest(secret, device_id, task_id, expiry))
