
import pytest
import json
from aioresponses import aioresponses

from torrent_searcher.async_searcher import Searcher
from torrent_searcher.tests.data.eztv_responses import PAGE_1
from torrent_searcher.searchers.series.eztv import URL

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
    searcher = Searcher()
    series = await searcher._search_for_series("the flash", 2, 21)
    assert series['name'] == 'the flash'
    assert series['season'] == 2
    assert all(series['episodes'].values())


@pytest.mark.asyncio
async def test_find_movie_magnet_ok():
    with aioresponses() as m:
        with open ("torrent_searcher/tests/data/yts_response.json") as f:
            payload = json.load(f)
            m.get(YTS_URL, payload=payload)
            searcher = Searcher()
            movie = await searcher._search_for_movie("return of the jedi", "1080p", 1983)
            assert movie['name'] == 'return of the jedi'
            assert movie['quality'] == '1080p'
            assert "C92F656155D0D8E87D21471D7EA43E3AD0D42723" in movie['magnet']


@pytest.mark.asyncio
async def test_find_movie_magnet_not_found():
    with aioresponses() as m:
        m.get(YTS_URL, payload=dict(data=dict(movies=[])))
        searcher = Searcher()
        movie = await searcher._search_for_movie("return of the jedi", "1080p", 1983)
        assert movie['name'] == 'return of the jedi'
        assert movie['quality'] == '1080p'
        assert movie['magnet'] is None