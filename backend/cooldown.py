from __future__ import annotations

import hashlib
import threading
import time


class CooldownStore:
    """Process-local cooldown ledger.

    Only a SHA-256 digest of the caller-provided pseudonymous delivery key and
    source is retained. The prototype stores no name, email, raw identifier,
    biometric payload, or message text. Production deployments should replace
    this with a TTL store such as Redis.
    """

    def __init__(self) -> None:
        self._last_delivery: dict[str, float] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _digest(delivery_key: str, source: str) -> str:
        value = f"{source}:{delivery_key}".encode("utf-8")
        return hashlib.sha256(value).hexdigest()

    def remaining_seconds(
        self, delivery_key: str | None, source: str, cooldown_seconds: int
    ) -> int:
        if not delivery_key or cooldown_seconds <= 0:
            return 0
        digest = self._digest(delivery_key, source)
        now = time.monotonic()
        with self._lock:
            last = self._last_delivery.get(digest)
        if last is None:
            return 0
        remaining = cooldown_seconds - (now - last)
        return max(0, int(remaining + 0.999))

    def record(self, delivery_key: str | None, source: str) -> bool:
        if not delivery_key:
            return False
        digest = self._digest(delivery_key, source)
        with self._lock:
            self._last_delivery[digest] = time.monotonic()
        return True

    def clear(self) -> None:
        with self._lock:
            self._last_delivery.clear()
