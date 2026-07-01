"""
ZeroCrawl — Configuration
Reads from environment variables and .env file.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ZeroCrawlSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ZEROCRAWL_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Browser pool ──────────────────────────────────────────────────────────
    browser_pool_size: int = Field(default=1, ge=1, le=10)
    browser_headless: bool = Field(default=True)
    browser_timeout_ms: int = Field(default=30_000)

    # ── Default scrape behaviour ──────────────────────────────────────────────
    default_mode: str = Field(default="auto")
    default_timeout: int = Field(default=60)
    default_cache_ttl: int = Field(default=3600)
    default_concurrency: int = Field(default=3)
    respect_robots_txt: bool = Field(default=True)

    # ── Rate limiting ─────────────────────────────────────────────────────────
    requests_per_second_per_domain: float = Field(default=1.0)
    delay_mean_seconds: float = Field(default=2.0)
    delay_stddev_seconds: float = Field(default=1.0)
    delay_min_seconds: float = Field(default=0.5)

    # ── Storage ───────────────────────────────────────────────────────────────
    data_dir: Path = Field(default=Path(".zerocrawl"))
    db_path: Optional[Path] = None  # defaults to data_dir/zerocrawl.db

    # ── API server ────────────────────────────────────────────────────────────
    api_host: str = Field(default="127.0.0.1")
    api_port: int = Field(default=8765)
    api_cors_origins: list[str] = Field(default=["*"])

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")
    log_file: Optional[Path] = None

    # ── AI providers (optional) ───────────────────────────────────────────────
    ollama_host: str = Field(default="http://localhost:11434")
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # ── Proxy ─────────────────────────────────────────────────────────────────
    proxy_strategy: str = Field(default="own_ip")
    custom_proxy: Optional[str] = None
    tor_socks_port: int = Field(default=9050)

    def get_db_path(self) -> Path:
        if self.db_path:
            return self.db_path
        return self.data_dir / "zerocrawl.db"

    def get_screenshots_dir(self) -> Path:
        return self.data_dir / "screenshots"

    def get_results_dir(self) -> Path:
        return self.data_dir / "results"

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.get_screenshots_dir().mkdir(parents=True, exist_ok=True)
        self.get_results_dir().mkdir(parents=True, exist_ok=True)

    @classmethod
    def auto_browser_pool_size(cls) -> int:
        """Detect available RAM and suggest appropriate browser pool size."""
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        except ImportError:
            # fallback: read /proc/meminfo on Linux
            try:
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal"):
                            kb = int(line.split()[1])
                            ram_gb = kb / (1024 ** 2)
                            break
                    else:
                        ram_gb = 4.0
            except Exception:
                ram_gb = 4.0

        if ram_gb < 4:
            return 1
        elif ram_gb < 8:
            return 1
        elif ram_gb < 16:
            return 2
        else:
            return 3


# Singleton settings instance
settings = ZeroCrawlSettings()
