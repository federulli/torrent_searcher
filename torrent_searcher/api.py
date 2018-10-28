from torrent_searcher.searchers.eztv_searcher import EztvSearcher
from torrent_searcher.searchers.rarbg_searcher import RarbgSearcher
from torrent_searcher.searchers.yts_searcher import YTSSearcher
from .settings import (
    DEFAULT_YTS_URL,
    DEFAULT_EZTV_URL,
)


class Searcher(object):

    def __init__(self, **kwargs):
        self._series = (
            EztvSearcher(kwargs.get('eztv_url', DEFAULT_EZTV_URL)),
            RarbgSearcher(),
        )
        self._movies = (
            YTSSearcher(kwargs.get('yts_url', DEFAULT_YTS_URL)),
        )

    def search_for_series(self, name, season, chapter_count):
        chapters = {chapter: None for chapter in range(1, chapter_count + 1)}
        iterator = iter(self._series)
        searcher = next(iterator, None)
        while searcher and any(value is None for value in chapters.values()):
            searcher.search_for_tv_show(name, season, chapters)
            searcher = next(iterator, None)
        return chapters

    def search_movie(self, name, quality='1080p'):
        return self._movies[0].search_movie(name, quality)
