import pytest
import json
from torrent_searcher.async_searcher import Searcher
from torrent_searcher.tests.data.eztv_responses import PAGE_1
from torrent_searcher.searchers.series.eztv import URL


@pytest.mark.asyncio
async def test_completeted_ok(aresponses):
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
    episodes = await searcher._search_for_series("the flash", "2", 21)
    
    assert all(episodes.values())
