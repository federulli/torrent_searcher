import requests
import itertools
from collections import namedtuple
from distutils.util import strtobool
from torrent_searcher.errors import NotCompletedException, NotFoundException


URL = 'https://eztv.ag/api/get-torrents'
Torrent = namedtuple("Torrent", ['filename', 'season', 'episode', 'magnet'])


def get_imdb_id(name):
    r = requests.get("http://www.omdbapi.com/?t={}&apikey=8a90e315".format(name))
    r.raise_for_status()
    if not strtobool(r.json()["Response"]):
        raise NotFoundException(f"Could not find {name} with EZTV")
    return r.json()["imdbID"][2:]


def get_torrents(imdb_id):
    for page in itertools.count(1):
        r = requests.get("{}?imdb_id={}&limit=100&page={}".format(URL, imdb_id, page))
        r.raise_for_status()

        torrents = r.json().get('torrents', [])
        if not torrents:
            return

        for torrent in torrents:
            if str(torrent["imdb_id"]) == str(imdb_id):
                yield Torrent(
                    torrent['filename'], int(torrent['season']),
                    int(torrent['episode']), torrent['magnet_url']
                )


def search(name, season, episodes):
    imdb_id = get_imdb_id(name)
    torrents = get_torrents(imdb_id)
    try:
        torrent = next(torrents)
    except StopIteration:
        raise NotFoundException(f"Could not find {name} {season} with EZTV")
    try:
        while not all(episodes.values()):
            validations = (
                int(torrent.season) == int(season),
                episodes.get(torrent.episode) is None
            )
            if all(validations):
                episodes[torrent.episode] = torrent.magnet
            torrent = next(torrents)
    except StopIteration:
        raise NotCompletedException(f"Could not complete {name} {season} with EZTV")
