import json
import responses
from torrent_searcher.api import Searcher
from torrent_searcher.tests.data.eztv_responses import PAGE_1
from torrent_searcher.searchers.series.eztv import URL


@responses.activate
def test_no_completeted(caplog):
    for page in range(1, 7):
        with open ("torrent_searcher/tests/data/eztv_ag_response_page{}.json".format(page)) as f:
            responses.add(
                responses.GET,
                URL.format(page),
                json=json.load(f),
                status=200
            )    
    responses.add(
        responses.GET,
        'http://www.omdbapi.com/?t=the%20flash&apikey=8a90e315',
        json={"imdbID": "tt3107288", "Response": "True"},
        status=200
    )
    searcher = Searcher()
    episodes = searcher.search(
        {
            "type": "SERIES",
            "name": "the flash",
            "season": "2",
            "episode_count": "21"
        }
    )
    assert all(magnet is not None for number, magnet in episodes.items())
