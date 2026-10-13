from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Level(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class Event:
    timestamp: datetime
    level: Level
    source: str
    message: str
