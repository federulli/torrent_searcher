from distutils.util import strtobool
import requests
from collections import namedtuple

Torrent = namedtuple("Torrent", ['filename', 'season', 'episode', 'magnet'])


def get_imdb_id(name):
    r = requests.get("http://www.omdbapi.com/?t={}&apikey=8a90e315".format(name))
    r.raise_for_status()
    if not strtobool(r.json()["Response"]):
        raise Exception("{} Doesn't exists")
    return r.json()["imdbID"][2:]


class EztvSearcher(object):

    def __init__(self, url):
        self._url = url

    def search_for_tv_show(self, name, season, chapters=0):
        chapters = {chapter: None for chapter in range(1, chapters + 1)}
        imdb_id = get_imdb_id(name)
        page = 1
        torrents = self._get_torrents(imdb_id, page)
        while not all(chapters.values()) and torrents:
            for torrent in torrents:
                validations = (
                    torrent.season == season,
                    chapters.get(torrent.episode) is None
                )
                if all(validations):
                    chapters[torrent.episode] = torrent.magnet
            page += 1
            torrents = self._get_torrents(imdb_id, page)
        return chapters

    def _get_torrents(self, imdb_id, page):
        r = requests.get(
            "{}?imdb_id={}&limit=100&page={}".format(self._url, imdb_id, page)
        )
        r.raise_for_status()
        return [
            Torrent(
                torrent['filename'],
                int(torrent['season']),
                int(torrent['episode']),
                torrent['magnet_url']
            )
            for torrent in r.json().get('torrents', []) if torrent["imdb_id"] == imdb_id
        ]
