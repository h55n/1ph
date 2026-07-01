"""
ZeroCrawl — Request Timing
Gaussian delay generator + per-domain rate limiting.
"""
from __future__ import annotations

import asyncio
import random
import time
from collections import defaultdict


class TimingController:
    """
    Gaussian-distributed delays and per-domain rate limits.
    One shared instance per scraping session.
    """

    def __init__(
        self,
        mean_seconds: float = 2.0,
        stddev_seconds: float = 1.0,
        min_seconds: float = 0.5,
        requests_per_second_per_domain: float = 1.0,
    ) -> None:
        self.mean = mean_seconds
        self.stddev = stddev_seconds
        self.minimum = min_seconds
        self.rps_per_domain = requests_per_second_per_domain

        # Per-domain: timestamps of recent requests (deque would be cleaner but dict+list is fine)
        self._domain_timestamps: dict[str, list[float]] = defaultdict(list)
        # Per-domain: accumulated request count for burst detection
        self._domain_counts: dict[str, int] = defaultdict(int)

    def _sample_delay(self) -> float:
        """Sample a delay from the Gaussian distribution."""
        delay = random.gauss(self.mean, self.stddev)
        return max(self.minimum, delay)

    async def wait_for_domain(self, domain: str) -> None:
        """
        Enforce rate limiting for a domain.
        Blocks until the next request is allowed, then records the attempt.
        """
        now = time.monotonic()
        timestamps = self._domain_timestamps[domain]

        # Keep only timestamps from the last 1 second
        cutoff = now - 1.0
        timestamps[:] = [t for t in timestamps if t > cutoff]

        if len(timestamps) >= self.rps_per_domain:
            # Need to wait until the oldest request is more than 1s ago
            oldest = timestamps[0]
            wait_time = (oldest + 1.0 / self.rps_per_domain) - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        # Gaussian inter-request delay
        delay = self._sample_delay()
        await asyncio.sleep(delay)

        # Record this request
        self._domain_timestamps[domain].append(time.monotonic())
        self._domain_counts[domain] += 1

        # Burst detection: extra pause every 10 requests to same domain
        count = self._domain_counts[domain]
        if count > 0 and count % 10 == 0:
            burst_pause = random.uniform(3.0, 8.0)
            await asyncio.sleep(burst_pause)

    async def human_pause(self, min_s: float = 0.5, max_s: float = 3.0) -> None:
        """A shorter random pause for in-page actions (Mode 3)."""
        await asyncio.sleep(random.uniform(min_s, max_s))

    async def gaussian_pause(self, mean: float = 2.0, stddev: float = 0.8) -> None:
        """Gaussian pause for use in human simulation."""
        delay = max(0.2, random.gauss(mean, stddev))
        await asyncio.sleep(delay)


# Default shared controller — replaced per-job if custom settings required
_default_controller: TimingController | None = None


def get_default_controller() -> TimingController:
    global _default_controller
    if _default_controller is None:
        from zerocrawl.config import settings
        _default_controller = TimingController(
            mean_seconds=settings.delay_mean_seconds,
            stddev_seconds=settings.delay_stddev_seconds,
            min_seconds=settings.delay_min_seconds,
            requests_per_second_per_domain=settings.requests_per_second_per_domain,
        )
    return _default_controller
