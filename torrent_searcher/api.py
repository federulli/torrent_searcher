from torrent_searcher.searchers.eztv_searcher import EztvSearcher
from torrent_searcher.searchers.yts_searcher import YTSSearcher
from .settings import (
    DEFAULT_YTS_URL,
    DEFAULT_EZTV_URL,
)


class Searcher(object):

    def __init__(self, **kwargs):
        self._series = (
            EztvSearcher(kwargs.get('eztv_url', DEFAULT_EZTV_URL)),
        )
        self._movies = (
            YTSSearcher(kwargs.get('yts_url', DEFAULT_YTS_URL)),
        )

    def search_for_series(self, name, season, chapters):
        return self._series[0].search_for_tv_show(name, season, chapters)

    def search_movie(self, name, quality='1080p'):
        return self._movies[0].search_movie(name, quality)
