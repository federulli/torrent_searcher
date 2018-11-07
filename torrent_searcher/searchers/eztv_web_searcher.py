from collections import defaultdict
import requests
from collections import namedtuple
from bs4 import BeautifulSoup
import re

# Callback data constants
SERIE = r'SERIE_'
LATEST_EPISODES = SERIE + 'LATEST_EPISODES'
LOAD_MORE_LATEST = SERIE + 'MORE_LATEST'
LOAD_EPISODES = SERIE + 'LOAD_EPISODES'
GO_BACK_TO_MAIN = SERIE + 'GO_TO_MAIN_RESULT'
SEASON_T = SERIE + 'SEASON_{}'
EPISODE_T = SERIE + 'EPISODE_{}'
SERIE_REGEX = re.compile(SERIE)


# Regex to find season and episode data
SEASON_REGEX = re.compile(r'S(\d{1,})E(\d{1,})')  # S01E15
ALT_SEASON_REGEX = re.compile(r'(\d{1,})x(\d{1,})')  # 1x15
EPISODE_PATTERNS = [SEASON_REGEX, ALT_SEASON_REGEX]

# Indexes to build Episode from html row
NAME, SIZE, RELEASED, SEEDS = 0, 2, 3, 4
MAGNET, TORRENT = 0, 1


Torrent = namedtuple("Torrent", ['filename', 'season', 'episode', 'magnet'])


def get_all_seasons(series_name, raw_user_query):
    """Parses eztv search page in order to return all episodes of a given series.
    Args:
        series_name: Full series name as it is on tmdb
        raw_user_query: The user query, with possible typos or the incomplete series_name
    Unlike get_latest_episodes handler function, this does not communicate directly
    with the eztv api because the api is in beta mode and has missing season and episode info
    for many episodes.
    In order to present the series episodes in an orderly manner, we need to rely on
    that information consistency and completeness. Neither of those requirements
    are satisfied by the api. That's why we parse the web to get consistent results.
    Quite a paradox..
    Returns:
        {
            1: # season
                1: [ # episode
                    {Episode()},
                    {Episode()},
                    ...
                ],
                2: [
                    {Episode()},
                    {Episode()},
                    ...
                ]
            2:
                1: [
                    {Episode()},
                    {Episode()},
                    ...
                ],
                ...
            ...
        }
    """
    series_episodes = defaultdict(lambda: defaultdict(list))

    def get_link(links, key):
        try:
            link = links[key]['href']
        except (IndexError, AttributeError):
            link = ''

        return link

    def get_episode_info(torrent):
        """Parse html to return an episode data.
        Receives an html row, iterates its tds
        (leaving the first and last values out).
        and returns an episode namedtuple
        """

        # First and last cell contain useless info (link with info and forum link)
        torrent = torrent.find_all('td')[1:-1]
        links = torrent[1].find_all('a')
        name = torrent[NAME].text.strip()

        # Filter fake results that include series name but separated between other words.
        # For example, a query for The 100 also returns '*The* TV Show S07E00 Catfish Keeps it *100*' which we don't want
        # We also use the raw_user_query because sometimes the complete name from tmdb is not the same name used on eztv.
        if not series_name.lower() in name.lower() and not raw_user_query.lower() in name.lower():
            # The tradeoff is that we don't longer work for series with typos. But it's better than giving fake results.
            return None

        for pattern in EPISODE_PATTERNS:
            match = pattern.search(name)
            if match:
                season, episode = match.groups()
                break
        else:
            # No season and episode found
            return None

        return Torrent(
            filename=name.replace('[', '').replace(']', ''),
            season=int(season),
            episode=int(episode),
            magnet=get_link(links, MAGNET)
        )

    # Parse episodes from web
    series_query = raw_user_query.replace(' ', '-')
    r = requests.get("https://eztv.ag/search/{}".format(series_query))
    soup = BeautifulSoup(r.text, 'lxml')
    torrents = soup.find_all('tr', {'class': 'forum_header_border'})

    # Build the structured dict
    for torrent in torrents:
        episode_info = get_episode_info(torrent)
        if not episode_info:
            # We should skip torrents if they don't belong to a season
            continue

        season, episode = episode_info.season, episode_info.episode
        # Attach the episode under the season key, under the episode key, in a list of torrents of that episode
        series_episodes[season][episode].append(episode_info)
    return series_episodes


class EztvWebSearcher(object):

    def __init__(self, url):
        self._url = url

    def search_for_tv_show(self, name, season, chapters):
        chapters_per_season = get_all_seasons(name, name)
        for chapter, torrent in chapters_per_season[season].items():
            if not chapters[chapter]:
                chapters[chapter] = torrent[0].magnet
