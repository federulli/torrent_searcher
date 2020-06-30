import json
import responses

from torrent_searcher.searchers.movies.yts import search


@responses.activate
def test_find_magnet_ok():
    with open("torrent_searcher/tests/data/yts_response.json") as f:
        responses.add(
            responses.GET,
            "https://yts.am/api/v2/list_movies.json?query_term=return of the jedi",
            json=json.load(f),
            status=200
        )
    magnet = search("return of the jedi", "1080p", 1983)
    assert "C92F656155D0D8E87D21471D7EA43E3AD0D42723" in magnet

    magnet = search("return of the jedi", "720p", 1983)
    assert "6828DF5E1037A95695A8713B99DBE57A20AE8530" in magnet


