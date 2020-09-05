
import pytest
import json
from aioresponses import aioresponses

from torrent_searcher.api import Searcher, Movie, Series
from torrent_searcher.tests.data.eztv_responses import PAGE_1
from torrent_searcher.searchers.series.async_eztv import URL

YTS_URL = 'https://yts.am/api/v2/list_movies.json?query_term=return+of+the+jedi'


@pytest.mark.asyncio
async def test_series_completeted_ok(aresponses):
    for page in range(1, 7):
        with open ("torrent_searcher/tests/data/eztv_ag_response_page{}.json".format(page)) as f:
            aresponses.add(
                'eztv.ag', '/api/get-torrents',
                'get', response=json.load(f)
            )

    aresponses.add(
        'www.omdbapi.com', '/',
        'get', response={"imdbID": "tt3107288", "Response": "True"}
    )
    series = Series(
        name="the flash", season=2, episode_count=21, quality='1080p')
    searcher = Searcher()
    await searcher._search_for_series(series)
    assert series.name == 'the flash'
    assert series.season == 2
    assert all(series.episodes.values())


@pytest.mark.asyncio
async def test_find_movie_magnet_ok():
    movie = Movie(name="return of the jedi", quality="1080p", year=1983)
    with aioresponses() as m:
        with open ("torrent_searcher/tests/data/yts_response.json") as f:
            payload = json.load(f)
            m.get(YTS_URL, payload=payload)
            searcher = Searcher()
            await searcher._search_for_movie(movie)
            assert movie.name == 'return of the jedi'
            assert movie.quality == '1080p'
            assert "C92F656155D0D8E87D21471D7EA43E3AD0D42723" in movie.magnet


@pytest.mark.asyncio
async def test_find_movie_magnet_not_found():
    movie = Movie(name="return of the jedi", quality="1080p", year=1983)
    with aioresponses() as m:
        m.get(YTS_URL, payload=dict(data=dict(movies=[])))
        searcher = Searcher()
        await searcher._search_for_movie(movie)
        assert movie.name == 'return of the jedi'
        assert movie.quality == '1080p'
        assert movie.magnet is None


def test_find_movie_and_series_magnet_with_search_ok():
    with aioresponses() as m:
        with open ("torrent_searcher/tests/data/yts_response.json") as f:
            payload = json.load(f)
            m.get(YTS_URL, payload=payload)
            searcher = Searcher()
            entities = [
                Movie(
                    name="return of the jedi",
                    quality="1080p",
                    year=1983
                ),
                Series(
                   name="the flash",
                   season=2,
                   episode_count=21,
                   quality='1080p'      
                )
            ]
            searcher.search(entities)
            assert "C92F656155D0D8E87D21471D7EA43E3AD0D42723" in entities[0].magnet