import pytest
import responses
import json
import requests
from torrent_searcher.searchers.eztv_searcher import EztvSearcher, Torrent
from data.eztv_responses import PAGE_1


@responses.activate
def test_get_torrents():
    responses.add(responses.GET, 'https://eztv.ag/api/get-torrents?imdb_id=3107288&limit=100&page=1',
                  json=PAGE_1, status=200)

    expected_result = [
        Torrent(
            filename=torrent['filename'],
            season=int(torrent['season']),
            episode=int(torrent['episode']),
            magnet=torrent['magnet_url']
        ) for torrent in PAGE_1["torrents"]
    ]
    searcher = EztvSearcher("https://eztv.ag/api/get-torrents")
    torrents = searcher._get_torrents(3107288, 1)
    import pdb; pdb.set_trace()
    assert torrents == expected_result
