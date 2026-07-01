"""
ZeroCrawl — Session Persistence
Cookie jars and browser session profiles that persist across requests.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Optional


# Real-world screen resolutions weighted by market share
_SCREEN_RESOLUTIONS = [
    (1920, 1080),  # ~22%
    (1920, 1080),
    (1366, 768),   # ~15%
    (1366, 768),
    (1440, 900),   # ~8%
    (1280, 800),   # ~5%
    (2560, 1440),  # ~5%
    (1536, 864),   # ~5%
    (1600, 900),   # ~4%
    (1280, 720),   # ~4%
]

_HARDWARE_CONCURRENCY = [2, 4, 4, 8, 8, 8, 12, 16]  # weighted
_DEVICE_MEMORY_GB = [4, 8, 8, 16]  # weighted

_WINDOWS_UA_STRINGS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

_MACOS_UA_STRINGS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:120.0) Gecko/20100101 Firefox/120.0",
]

_WEBGL_RENDERERS = [
    "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (AMD Radeon RX 5700 XT Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
    "Apple M1",
    "Apple M2",
    "ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
]


@dataclass
class FingerprintProfile:
    """A consistent browser fingerprint profile for a session."""
    profile_id: str
    platform: str             # "Windows", "macOS", "Linux"
    screen_width: int
    screen_height: int
    hardware_concurrency: int
    device_memory: int        # GB
    timezone: str
    language: str
    locale: str
    canvas_noise_seed: int
    webgl_renderer: str
    user_agent: str
    color_depth: int = 24
    request_count: int = 0
    max_requests: int = 50    # retire after N requests
    created_at: float = field(default_factory=time.time)
    cookies: dict[str, dict[str, str]] = field(default_factory=dict)  # domain → {name: value}

    @property
    def is_retired(self) -> bool:
        return self.request_count >= self.max_requests

    def record_request(self) -> None:
        self.request_count += 1

    def get_cookies(self, domain: str) -> dict[str, str]:
        return self.cookies.get(domain, {})

    def set_cookies(self, domain: str, cookies: dict[str, str]) -> None:
        if domain not in self.cookies:
            self.cookies[domain] = {}
        self.cookies[domain].update(cookies)


def generate_fingerprint_profile(profile_id: Optional[str] = None) -> FingerprintProfile:
    """Generate a new, internally consistent fingerprint profile."""
    import uuid
    import hashlib

    pid = profile_id or str(uuid.uuid4())

    # Consistent OS selection
    platform_choice = random.choice(["Windows", "Windows", "macOS", "Linux"])
    if platform_choice == "Windows":
        ua = random.choice(_WINDOWS_UA_STRINGS)
        timezone = random.choice([
            "America/New_York", "America/Chicago", "America/Denver",
            "America/Los_Angeles", "Europe/London",
        ])
        language = "en-US"
        locale = "en-US"
    elif platform_choice == "macOS":
        ua = random.choice(_MACOS_UA_STRINGS)
        timezone = random.choice(["America/New_York", "America/Los_Angeles", "Europe/London"])
        language = "en-US"
        locale = "en-US"
    else:
        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        timezone = "America/New_York"
        language = "en-US"
        locale = "en-US"

    width, height = random.choice(_SCREEN_RESOLUTIONS)
    seed = int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)

    return FingerprintProfile(
        profile_id=pid,
        platform=platform_choice,
        screen_width=width,
        screen_height=height,
        hardware_concurrency=random.choice(_HARDWARE_CONCURRENCY),
        device_memory=random.choice(_DEVICE_MEMORY_GB),
        timezone=timezone,
        language=language,
        locale=locale,
        canvas_noise_seed=seed,
        webgl_renderer=random.choice(_WEBGL_RENDERERS),
        user_agent=ua,
        max_requests=random.randint(40, 60),
    )


class SessionPool:
    """
    Manages a pool of fingerprint profiles.
    Returns active profiles; replaces retired ones automatically.
    """

    def __init__(self, pool_size: int = 1) -> None:
        self.pool_size = pool_size
        self._profiles: list[FingerprintProfile] = [
            generate_fingerprint_profile() for _ in range(pool_size)
        ]

    def get_profile(self) -> FingerprintProfile:
        """Return the next active profile, replacing retired ones."""
        for i, profile in enumerate(self._profiles):
            if profile.is_retired:
                self._profiles[i] = generate_fingerprint_profile()
        return self._profiles[0]

    def rotate(self) -> FingerprintProfile:
        """Force-retire the current lead profile and get a fresh one."""
        self._profiles[0] = generate_fingerprint_profile()
        return self._profiles[0]
