from aioresponses import aioresponses
import pytest
import json
from torrent_searcher.errors import NotFoundException
from torrent_searcher.searchers.movies.async_yts import search

URL = 'https://yts.am/api/v2/list_movies.json?query_term=return+of+the+jedi'

@pytest.mark.asyncio
async def test_find_magnet_ok():
    with aioresponses() as m:
        with open ("torrent_searcher/tests/data/yts_response.json") as f:
            payload = json.load(f)
            m.get(URL, payload=payload)
            m.get(URL, payload=payload)

        magnet = await search("return of the jedi", "1080p", 1983)
        assert "C92F656155D0D8E87D21471D7EA43E3AD0D42723" in magnet

        magnet = await search("return of the jedi", "720p", 1983)
        assert "6828DF5E1037A95695A8713B99DBE57A20AE8530" in magnet


@pytest.mark.asyncio
async def test_no_movies():
    with aioresponses() as m:
        m.get(URL, payload=dict(data=dict(movies=[])))
        with pytest.raises(NotFoundException):
            await search("return of the jedi", "720p", 1983)
