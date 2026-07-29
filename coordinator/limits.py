"""Limiteurs de débit en mémoire (fenêtre glissante) — suffisant pour un
coordinateur mono-processus ; à revisiter si multi-workers uvicorn un jour."""

import threading
import time
from collections import deque


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque] = {}
        self._lock = threading.Lock()

    # Au-delà de cette taille, on balaye et on purge les clés éteintes à
    # chaque appel : borne la mémoire face à une rotation d'IP/clés hostile.
    _PURGE_THRESHOLD = 10_000

    def allow(self, key: str, limit: int, window_seconds: float) -> bool:
        """True si l'appel est admis pour cette clé, False s'il dépasse le débit."""
        now = time.monotonic()
        with self._lock:
            if len(self._hits) > self._PURGE_THRESHOLD:
                self._purge(now, window_seconds)
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] > window_seconds:
                hits.popleft()
            if len(hits) >= limit:
                if not hits:  # clé rejetée sans historique vivant : ne pas la garder
                    self._hits.pop(key, None)
                return False
            hits.append(now)
            return True

    def _purge(self, now: float, window_seconds: float) -> None:
        dead = [k for k, h in self._hits.items()
                if not h or now - h[-1] > window_seconds]
        for k in dead:
            del self._hits[k]

    def size(self) -> int:
        return len(self._hits)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


device_limiter = SlidingWindowLimiter()    # requêtes par clé API
register_limiter = SlidingWindowLimiter()  # enregistrements par IP
public_limiter = SlidingWindowLimiter()    # endpoints publics (/stats) par IP
