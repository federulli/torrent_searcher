from typing import Dict
from enum import Enum
from dataclasses import dataclass, field


SERIES = "SERIES"
MOVIES = 'MOVIES'


class QualityEnum(Enum):
    FULLHD = '1080p'
    HD = '720p' 


@dataclass
class Movie:
    name: str
    quality: QualityEnum
    year: int = None
    magnet: str = None


@dataclass
class Series:
    name: str
    quality: QualityEnum
    season: int
    episode_count: int
    episodes: Dict[int, str] = field(default_factory=dict)
