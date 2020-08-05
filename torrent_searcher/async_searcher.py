import structlog

from torrent_searcher.errors import NotCompletedException, NotFoundException
from torrent_searcher.searchers.series import async_eztv
from torrent_searcher.searchers.movies import async_yts
logger = structlog.get_logger()

SERIES = "SERIES"
MOVIE = "MOVIE"

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

    """def __init__(self):
        self._searchers = {
            "SERIES": self._search_for_series,
            "MOVIES": self._search_for_movie
        }
    """
    
    """
    def search(self, data):
        coroutines = []
        for entity in data:
            type = data.pop('type')
            magnet = await self._searchers[type](**data)
        return 
    """
       
    async def _search_for_series(self, name, season, episode_count):
        episodes = {chapter: None for chapter in range(1, int(episode_count) + 1)}
        for search_coroutine in (async_eztv.search,):
            try:
                await search_coroutine(name, season, episodes)
            except (NotFoundException, NotCompletedException) as e:
                logger.info(str(e))
            except Exception:
                logger.exception(str(search_coroutine), exc_info=True)
        logger.info(episodes)
        if not all(episodes.values()):
            logger.info(f"Could not complete {name} {season} with any searcher")
        return {
            "name": name,
            "season": season,
            "episodes": episodes,
            "episode_count": episode_count,
            "type": SERIES
        }
        

    async def _search_for_movie(self, name, quality='1080p', year=None):
        magnet = None
        for search_coroutine in (async_yts.search,):
            try: 
                magnet = await search_coroutine(name, quality, year)
                break
            except NotFoundException as e:
                logger.info(str(e))
            except Exception:
                logger.exception("ERROR", exc_info=True)
        if not magnet:
            logger.info(f"Could not find {name} {year} {quality} with any searcher")
        return {
            "name": name,
            "quality": quality,
            "year": year,
            "magnet": magnet
        }
    
