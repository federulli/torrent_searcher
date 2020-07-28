import structlog

from torrent_searcher.searchers import MOVIES, SERIES
from torrent_searcher.errors import NotCompletedException, NotFoundException
from torrent_searcher.searchers.series import async_eztv
from torrent_searcher.searchers.movies import async_yts
logger = structlog.get_logger()


class Searcher(object):

    """def __init__(self):
        self._searchers = {
            "SERIES": self._search_for_series,
            "MOVIES": self._search_for_movie
        }
    """
    """def search(self, data):
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
        return episodes
        

    async def _search_for_movie(self, name, quality='1080p', year=None):
        for search_coroutine in (async_yts.search,):
            try: 
                return await search_coroutine(name, quality, year)
            except NotFoundException as e:
                logger.info(str(e))
            except Exception:
                logger.exception("ERROR", exc_info=True)
        logger.info(f"Could not find {name} {year} {quality} with any searcher")
    
