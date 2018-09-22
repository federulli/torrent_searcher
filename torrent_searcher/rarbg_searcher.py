from rarbgapi import RarbgAPI
import re


class RarbgSearcher(object):

    def __init__(self):
        self._rarbggateway = RarbgAPI()

    def search_for_tv_show(self, name, season, chapters=0):
        chapters = {chapter: None for chapter in range(1, chapters + 1)}
        torrents = self._rarbggateway.search(
            search_string="{} s{}e".format(name, str(season).zfill(2)),
            limit=100
        )
        for torrent in torrents:
            try:
                chapter = self._get_chapter_from_file(torrent.filename, season)
                if not chapters[chapter]:
                    chapters[chapter] = torrent
            except:
                continue
        not_found_chapters = [key for key, value in chapters.items() if value is None]
        for chapter in not_found_chapters:
            torrents = self._rarbggateway.search(
                search_string="{} s{}e{}".format(
                    name,
                    str(season).zfill(2),
                    str(chapter).zfill(2)
                ),
                limit=25
            )
            for torrent in torrents:
                try:
                    chapter = self._get_chapter_from_file(torrent.filename, season)
                    if not chapters[chapter]:
                        chapters[chapter] = torrent
                except:
                    continue
        return chapters

    @staticmethod
    def _get_chapter_from_file(file, season):
        file = str(file).lower()
        seas = re.sub(r".*s([0-9][0-9])e[0-9][0-9].*", r"\1", file)
        chapter = re.sub(r".*e([0-9][0-9]).*", r"\1", file)
        assert chapter != file and seas != file
        assert chapter and seas and int(seas) == season
        return int(chapter)
