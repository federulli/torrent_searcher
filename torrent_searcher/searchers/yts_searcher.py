import requests
from torrent_searcher.settings import YTS_TRACKER_LIST
from torrent_searcher.errors.torrent_not_found import TorrentNotFound


class YTSSearcher(object):

    def __init__(self, url):
        self._url = url

    def search_movie(self, name, quality='1080p'):
        movie_payload = requests.get(
            '{}/list_movies.json'.format(self._url), params={'query_term': name}
        )
        try:
            return next(
                self._build_magnet_uri(movie['hash'])
                for movie in self._get_movie_json(movie_payload, name)['torrents']
                if movie['quality'] == quality
            )
        except Exception:
            raise TorrentNotFound("Couldn't find movie {} with {} quality".format(name, quality))

    @staticmethod
    def _build_magnet_uri(movie_hash):
        return 'magnet:?xt=urn:btih:{}&dn=Url+Encoded+Movie+Name&tr={}'.format(
            movie_hash,
            '&tr='.join(YTS_TRACKER_LIST)
        )

    def _get_movie_json(self, payload, name):
        return next(iter([
            movie for movie in payload.json()['data']['movies']
            if name.upper() in movie['title'].upper()
        ]), None)
