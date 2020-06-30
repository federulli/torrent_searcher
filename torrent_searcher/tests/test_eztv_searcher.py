import pytest
import responses
import json
import requests

from torrent_searcher.errors import NotFoundException, NotCompletedException
from torrent_searcher.searchers.series.eztv import (
    search,
    get_torrents,
    Torrent
)

from torrent_searcher.tests.data.eztv_responses import PAGE_1

URL = 'https://eztv.ag/api/get-torrents?imdb_id=3107288&limit=100&page={}'


@responses.activate
def test_get_torrents():
    responses.add(responses.GET, URL.format(1),
                  json=PAGE_1, status=200)
    responses.add(responses.GET, URL.format(2),
                  json={}, status=200)
    expected_result = [
        Torrent(
            filename=torrent['filename'],
            season=int(torrent['season']),
            episode=int(torrent['episode']),
            magnet=torrent['magnet_url']
        ) for torrent in PAGE_1["torrents"]
    ]
    torrents = get_torrents(3107288)
    assert list(torrents) == expected_result


@responses.activate
def test_for_tv_show():
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
    episodes = {chapter: None for chapter in range(1, 22)}
    search("the flash", 2, episodes)
    assert all(magnet is not None for number, magnet in episodes.items())


@responses.activate
def test_no_magnet_found():
    responses.add(
        responses.GET,
        'http://www.omdbapi.com/?t=the%20flash&apikey=8a90e315',
        json={"imdbID": "tt3107288", "Response": "True"},
        status=200
    )
    responses.add(
        responses.GET,
        URL.format(1),
        json={},
        status=200
    )
    episodes = {chapter: None for chapter in range(1, 22)}
    with pytest.raises(NotFoundException):
        search("the flash", 2, episodes)


@responses.activate
def test_no_completed():
    responses.add(
        responses.GET,
        'http://www.omdbapi.com/?t=the%20flash&apikey=8a90e315',
        json={"imdbID": "tt3107288", "Response": "True"},
        status=200
    )
    responses.add(responses.GET, URL.format(1),
                  json=PAGE_1, status=200)
    responses.add(responses.GET, URL.format(2),
                  json={}, status=200)

    episodes = {chapter: None for chapter in range(1, 22)}
    with pytest.raises(NotCompletedException):
        search("the flash", 2, episodes)
