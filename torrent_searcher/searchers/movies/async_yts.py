from aiohttp_requests import requests

from torrent_searcher import Movie
from torrent_searcher.settings import YTS_TRACKER_LIST
from torrent_searcher.errors import NotFoundException


TRACKER_LIST = (
    'udp://open.demonii.com:1337/announce',
    'udp://tracker.openbittorrent.com:80',
    'udp://tracker.coppersurfer.tk:6969',
    'udp://glotorrents.pw:6969/announce',
    'udp://tracker.opentrackr.org:1337/announce',
    'udp://torrent.gresille.org:80/announce',
    'udp://p4p.arenabg.com:1337',
    'udp://tracker.leechers-paradise.org:6969',
)

URL = 'https://yts.am/api/v2'


def build_magnet_uri(movie_hash: str) -> str:
    return 'magnet:?xt=urn:btih:{}&dn=Url+Encoded+Movie+Name&tr={}'.format(
        movie_hash,
        '&tr='.join(YTS_TRACKER_LIST)
    )


def get_movie_json(payload: dict, name: str, year: str) -> dict:
    for movie in payload['data']['movies']:
        criteria = (
            name.upper() in movie['title'].upper(),
            not year or int(year) == int(movie['year'])
        )
        if all(criteria):
            return movie
    return {}


async def search(movie: Movie) -> None:
    r = await requests.get(
        '{}/list_movies.json'.format(URL), params={'query_term': movie.name}
    )
    r.raise_for_status()
    movie_payload = await r.json()
    try:
        movie_data = get_movie_json(movie_payload, movie.name, movie.year)
        movie.magnet = next(
            build_magnet_uri(torrent['hash'])
            for torrent in movie_data.get('torrents', []) if torrent['quality'] == movie.quality
        )
    except StopIteration:
        raise NotFoundException(f"YTS: Could not find {movie.name} with {movie.quality} quality")
