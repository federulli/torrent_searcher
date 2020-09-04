import structlog
import asyncio
from dataclasses import dataclass, field
from enum import Enum

from torrent_searcher.errors import NotCompletedException, NotFoundException
from torrent_searcher.searchers.series import async_eztv
from torrent_searcher.searchers.movies import async_yts
logger = structlog.get_logger()
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
    episodes: dict = field(default_factory=dict)


input_example = [
    {
        "type": "SERIES",
        "name": "blabla",
        "quality": "720p, 1080p",
        "season": 1,
        "episode_count": 23 
    },
    {
        "type": "MOVIE",
        "quality": "720p, 1080p",
        "name": "asdasd",
        "year": 1990
    }
]
response_1 = [
    {
        "type": "SERIES",
        "name": "blabla",
        "quality": "720p, 1080p",
        "season": 1,
        "episode_count": 23,
        "episodes": {
            1: "",
            2: ""
        } 
    },
    {
        "type": "MOVIE",
        "quality": "720p, 1080p",
        "name": "asdasd",
        "year": 1990,
        "magnet": ""
    }
]

class Searcher(object):
    series_sem = asyncio.Semaphore(3)
    movies_sem = asyncio.Semaphore(3)
    
    
    def search(self, data):
        entities = [self._format(entity) for entity in data]
        group = self._gather_searchers(entities)           
        asyncio.run(group)
        return entities
    
    def _format(self, entity):
        type = entity.pop("type", None)
        if type == "MOVIE":
            return Movie(**entity)
        elif type == 'SERIES':
            return Series(**entity)
    
    async def _gather_searchers(self, entities):
        coroutines = []
        for entity in entities:
            if isinstance(entity, Movie):
                coroutines.append(self._search_for_movie(entity))
            elif isinstance(entity, Series):
                coroutines.append(self._search_for_series(entity))
        await asyncio.gather(*coroutines)

    
    async def _search_for_series(self, series: Series):
        series.episodes = {chapter: None for chapter in range(1, series.episode_count + 1)}
        for search_coroutine in (async_eztv.search,):
            try:
                async with self.series_sem:
                    await search_coroutine(
                        series.name,
                        series.season,
                        series.episodes
                    )
            except (NotFoundException, NotCompletedException) as e:
                logger.info(str(e))
            except Exception:
                logger.exception(str(search_coroutine), exc_info=True)
        logger.info(series.episodes)
        if not all(series.episodes.values()):
            logger.info(f"Could not complete {series.name} {series.season} with any searcher")
        
    async def _search_for_movie(self, movie: Movie):
        for search_coroutine in (async_yts.search,):
            try: 
                async with self.movies_sem:
                    movie.magnet = await search_coroutine(
                        movie.name,
                        movie.quality,
                        movie.year
                    )
                break
            except NotFoundException as e:
                logger.info(str(e))
            except Exception:
                logger.exception("ERROR", exc_info=True)
        if not movie.magnet:
            logger.info(f"Could not find {movie.name} {movie.year} {movie.quality} with any searcher")
