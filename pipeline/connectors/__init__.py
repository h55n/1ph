from .mlh import MLHConnector
from .dorahacks import DoraHacksConnector
from .hackerearth import HackerEarthConnector
from .devfolio import DevfolioConnector
from .hack2skill import Hack2SkillConnector
from .startup_grants_india import StartupGrantsIndiaConnector
from .devpost import DevpostConnector
from .unstop import UnstopConnector
from .hackerrank import HackerRankConnector
from .luma import LumaConnector
from .toplang import TopLangConnector

ALL_CONNECTORS = [
    MLHConnector,
    DoraHacksConnector,
    HackerEarthConnector,
    DevfolioConnector,
    Hack2SkillConnector,
    StartupGrantsIndiaConnector,
    DevpostConnector,
    UnstopConnector,
    HackerRankConnector,
    LumaConnector,
    TopLangConnector,
]
