import asyncio
from aiohttp_requests import requests
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


def build_magnet_uri(movie_hash):
    return 'magnet:?xt=urn:btih:{}&dn=Url+Encoded+Movie+Name&tr={}'.format(
        movie_hash,
        '&tr='.join(YTS_TRACKER_LIST)
    )


def get_movie_json(payload, name, year):
    for movie in payload['data']['movies']:
        criteria = (
            name.upper() in movie['title'].upper(),
            not year or int(year) == int(movie['year'])
        )
        if all(criteria):
            return movie


async def search(name, quality, year):
    r = await requests.get(
        '{}/list_movies.json'.format(URL), params={'query_term': name}
    )
    r.raise_for_status()
    movie_payload = await r.json()
    try:
        return next(
            build_magnet_uri(movie['hash'])
            for movie in get_movie_json(movie_payload, name, year)['torrents']
            if movie['quality'] == quality
        )
    except StopIteration:
        raise NotFoundException(f"YTS: Could not find {name} with {quality} quality")
