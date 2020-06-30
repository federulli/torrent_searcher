import pytest
import json

from torrent_searcher.searchers.movies.async_yts import search


@pytest.mark.asyncio
async def test_find_magnet_ok():
    magnet = await search("return of the jedi", "1080p", 1983)
    assert "C92F656155D0D8E87D21471D7EA43E3AD0D42723" in magnet

    magnet = await search("return of the jedi", "720p", 1983)
    assert "6828DF5E1037A95695A8713B99DBE57A20AE8530" in magnet
