import structlog

from torrent_searcher.searchers import MOVIES, SERIES
from torrent_searcher.errors import NotCompletedException, NotFoundException

logger = structlog.get_logger()


class Searcher(object):

    def __init__(self):
        self._searchers = {
            "SERIES": self._search_for_series,
            "MOVIES": self._search_for_movie
        }

    def search(self, data):
        type = data.pop('type')
        return self._searchers[type](**data)
       
    def _search_for_series(self, name, season, episode_count):
        episodes = {chapter: None for chapter in range(1, int(episode_count) + 1)}
        iterator = iter(SERIES)
        search_function = next(iterator)
        try:
            while any(value is None for value in episodes.values()):
                try:
                    search_function(name, season, episodes)
                except (NotFoundException, NotCompletedException) as e:
                    logger.info(str(e))
                except Exception:
                    logger.exception(str(search_function), exc_info=True)
                search_function = next(iterator)
        except StopIteration:
            logger.info(f"Could not complete {name} {season} with any searcher")
        logger.info(episodes)
        return episodes

    def _search_for_movie(self, name, quality='1080p', year=None):
        try:
            return MOVIES[0].search_movie(name, quality, year)
        except Exception:
            logger.exception("ERROR", exc_info=True)
