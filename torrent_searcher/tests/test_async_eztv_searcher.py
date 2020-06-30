import pytest
import json
from torrent_searcher.errors import NotFoundException, NotCompletedException
from torrent_searcher.searchers.series.async_eztv import (
    get_torrents,
    Torrent,
    search
)

from torrent_searcher.tests.data.eztv_responses import PAGE_1


@pytest.mark.asyncio
async def test_get_torrents(aresponses):
    aresponses.add(
        'eztv.ag', '/api/get-torrents',
        'get', response=PAGE_1
    )
    aresponses.add(
        'eztv.ag', '/api/get-torrents',
        'get', response={}
    )
    expected_result = [
        Torrent(
            filename=torrent['filename'],
            season=int(torrent['season']),
            episode=int(torrent['episode']),
            magnet=torrent['magnet_url']
        ) for torrent in PAGE_1["torrents"]
    ]
    torrents = [torrent async for torrent in get_torrents(3107288)]
    assert torrents == expected_result


@pytest.mark.asyncio
async def test_for_tv_show(aresponses):
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

    episodes = {chapter: None for chapter in range(1, 22)}
    await search("the flash", 2, episodes)
    assert all(magnet is not None for number, magnet in episodes.items())


@pytest.mark.asyncio
async def test_no_magnet_found(aresponses):
    aresponses.add(
        'www.omdbapi.com', '/',
        'get', response={"imdbID": "tt3107288", "Response": "True"}
    )
    aresponses.add(
        'eztv.ag', '/api/get-torrents',
        'get', response={}
    )
    episodes = {chapter: None for chapter in range(1, 22)}
    with pytest.raises(NotCompletedException):
        await search("the flash", 2, episodes)


@pytest.mark.asyncio
async def test_no_imdb_found(aresponses):
    aresponses.add(
        'www.omdbapi.com', '/',
        'get', response={"imdbID": "tt3107288", "Response": "False"}
    )
    aresponses.add(
        'eztv.ag', '/api/get-torrents',
        'get', response={}
    )
    episodes = {chapter: None for chapter in range(1, 22)}
    with pytest.raises(NotFoundException):
        await search("the flash", 2, episodes)


@pytest.mark.asyncio
async def test_no_completed(aresponses):
    aresponses.add(
        'www.omdbapi.com', '/',
        'get', response={"imdbID": "tt3107288", "Response": "True"}
    )
    aresponses.add(
        'eztv.ag', '/api/get-torrents',
        'get', response=PAGE_1
    )
    aresponses.add(
        'eztv.ag', '/api/get-torrents',
        'get', response={}
    )

    episodes = {chapter: None for chapter in range(1, 22)}
    with pytest.raises(NotCompletedException):
        await search("the flash", 2, episodes)
