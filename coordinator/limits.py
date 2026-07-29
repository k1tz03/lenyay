"""Limiteurs de débit en mémoire (fenêtre glissante) — suffisant pour un
coordinateur mono-processus ; à revisiter si multi-workers uvicorn un jour."""

import threading
import time
from collections import deque


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window_seconds: float) -> bool:
        """True si l'appel est admis pour cette clé, False s'il dépasse le débit."""
        now = time.monotonic()
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] > window_seconds:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


device_limiter = SlidingWindowLimiter()    # requêtes par clé API
register_limiter = SlidingWindowLimiter()  # enregistrements par IP
