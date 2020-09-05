import asyncio
import itertools
from collections import namedtuple
from distutils.util import strtobool

from aiohttp_requests import requests

from torrent_searcher.errors import NotCompletedException, NotFoundException
from torrent_searcher import Series


URL = 'https://eztv.ag/api/get-torrents'
Torrent = namedtuple("Torrent", ['filename', 'season', 'episode', 'magnet'])


async def get_imdb_id(name: str):
    r = await requests.get("http://www.omdbapi.com", params={"t": name, "apikey": "8a90e315"})
    r.raise_for_status()
    payload = await r.json()
    if not strtobool(payload["Response"]):
        raise NotFoundException(f"Could not find {name} with EZTV")
    return payload["imdbID"][2:]


async def get_torrents(imdb_id):
    for page in itertools.count(1):
        r = await requests.get(URL, params={"imdb_id": imdb_id, "limit": 100, "page": page})
        r.raise_for_status()

        payload = await r.json()
        
        torrents = payload.get('torrents', [])
        if not torrents:
            return

        for torrent in torrents:
            if str(torrent["imdb_id"]) == str(imdb_id):
                yield Torrent(
                    torrent['filename'], int(torrent['season']),
                    int(torrent['episode']), torrent['magnet_url']
                )


async def search(series: Series):
    imdb_id = await get_imdb_id(series.name)
    async for torrent in get_torrents(imdb_id):
        validations = (
            int(torrent.season) == int(series.season),
            series.episodes.get(torrent.episode) is None
        )
        if all(validations):
            series.episodes[torrent.episode] = torrent.magnet
        if all(series.episodes.values()):
            break
    if not all(series.episodes.values()):
        raise NotCompletedException(f"Could not complete {series.name} {series.season} with EZTV")
