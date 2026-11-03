"""In-memory rate limits for the public demo.

Two caps, both reset when the process restarts:
- per visitor: at most `per_ip` requests in any rolling `window_s` seconds
- whole service: at most `daily` requests per UTC day

In-memory is enough for one free-tier instance. If the service ever runs on
more than one instance, each instance keeps its own counts.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable


class RateLimiter:
    def __init__(
        self,
        per_ip: int,
        window_s: int,
        daily: int,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.per_ip = per_ip
        self.window_s = window_s
        self.daily = daily
        self.clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._day = self._today()
        self._day_count = 0

    def _today(self) -> int:
        return int(self.clock() // 86400)

    def check(self, ip: str) -> tuple[bool, int]:
        """Record a request. Returns (allowed, retry_after_seconds)."""
        now = self.clock()
        today = self._today()
        if today != self._day:
            self._day, self._day_count = today, 0
        if self.daily and self._day_count >= self.daily:
            return False, int((today + 1) * 86400 - now) + 1

        hits = self._hits[ip]
        while hits and now - hits[0] >= self.window_s:
            hits.popleft()
        if self.per_ip and len(hits) >= self.per_ip:
            return False, int(self.window_s - (now - hits[0])) + 1

        hits.append(now)
        self._day_count += 1
        return True, 0
