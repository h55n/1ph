"""
base.py — Abstract base class every connector must implement.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RawHackathon:
    """Normalised intermediate before DB write. All fields from BRD data model."""
    source_id: str
    title: str
    organizer_name: str
    apply_url: str
    registration_close: str          # ISO 8601 string  e.g. "2025-08-31"
    registration_open: Optional[str] = None
    event_start: Optional[str] = None
    event_end: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    mode: str = "ONLINE"             # ONLINE | OFFLINE | HYBRID
    entry_fee: Optional[float] = None
    entry_fee_currency: Optional[str] = "USD"
    team_size_min: int = 1
    team_size_max: Optional[int] = None
    eligibility: str = "OPEN"        # STUDENTS | OPEN | PROFESSIONALS
    duration_type: str = "CUSTOM"    # HR24 | HR48 | WEEK | MONTH | CUSTOM
    prize_pool: Optional[float] = None
    prize_currency: Optional[str] = "USD"
    prize_description: Optional[str] = None
    theme_tags: list = field(default_factory=list)
    sponsors: list = field(default_factory=list)
    organizer_logo_url: Optional[str] = None
    scope: str = "GLOBAL"            # GLOBAL | INDIA
    india_region: Optional[str] = None


@dataclass
class ConnectorResult:
    source: str
    records: list          # list[RawHackathon]
    status: str            # SUCCESS | PARTIAL | FAILED
    error: Optional[str] = None


class BaseConnector(ABC):
    """Every source connector inherits this. Implement fetch() only."""

    SOURCE: str = ""       # set in each subclass e.g. "DEVPOST"
    SCOPE: str = "GLOBAL"  # default; override in India-specific connectors

    @abstractmethod
    def fetch(self) -> ConnectorResult:
        """Fetch from source and return a ConnectorResult."""
        ...

    def run(self) -> ConnectorResult:
        """
        Public entry point. Wraps fetch() so one connector crashing
        never kills the rest of the pipeline.
        """
        try:
            return self.fetch()
        except Exception as e:
            return ConnectorResult(
                source=self.SOURCE,
                records=[],
                status="FAILED",
                error=str(e),
            )
