import structlog
import asyncio

from typing import List, Union
from torrent_searcher import Movie, Series
from torrent_searcher.errors import NotCompletedException, NotFoundException
from torrent_searcher.searchers.series import async_eztv
from torrent_searcher.searchers.movies import async_yts

logger = structlog.get_logger()


class Searcher(object):
    series_sem = asyncio.Semaphore(3)
    movies_sem = asyncio.Semaphore(3)
    
    def search(self, entities: List[Union[Movie, Series]]) -> None:
        group = self._gather_searchers(entities)           
        asyncio.run(group)
    
    async def _gather_searchers(self, entities: List[Union[Movie, Series]]):
        coroutines = []
        for entity in entities:
            if isinstance(entity, Movie):
                coroutines.append(self._search_for_movie(entity))
            elif isinstance(entity, Series):
                coroutines.append(self._search_for_series(entity))
        await asyncio.gather(*coroutines)

    async def _search_for_series(self, series: Series) -> None:
        series.episodes = {
            chapter: None for chapter in range(1, series.episode_count + 1)
        }
        for search_coroutine in (async_eztv.search,):
            try:
                async with self.series_sem:
                    await search_coroutine(series)
            except (NotFoundException, NotCompletedException) as e:
                logger.info(str(e))
            except Exception:
                logger.exception(str(search_coroutine), exc_info=True)
        logger.info(series.episodes)
        if not all(series.episodes.values()):
            logger.info(f"Could not complete {series.name} {series.season} with any searcher")
    
    async def _search_for_movie(self, movie: Movie) -> None:
        for search_coroutine in (async_yts.search,):
            try:
                async with self.movies_sem:
                    await search_coroutine(movie)
                break
            except NotFoundException as e:
                logger.info(str(e))
            except Exception:
                logger.exception("ERROR", exc_info=True)
        if not movie.magnet:
            logger.info(
                f"Could not find {movie.name} {movie.year} {movie.quality} with any searcher"
            )
