from torrent_searcher.tpb import TPB, ORDERS
import re


class PirateBaySearcher(object):

    def __init__(self, url):
        self._pirategateway = TPB(url)

    def search_for_tv_show(self, name, season, chapters=0):
        chapters = {}
        for page in range(0, 10):
            torrents = self._pirategateway.search(name).order(ORDERS.SEEDERS.DES).page(page)
            for torrent in torrents:
                try:
                    file = str(torrent).lower()
                    seas = re.sub(r".*s([0-9]*)e[0-9]*.*", r"\1", file)
                    chapter = re.sub(r".*e([0-9][0-9]).*", r"\1", file)
                    if chapter == file or seas == file:
                        continue
                    if chapter != "" and seas != "" and int(seas) == season:
                        if not int(chapter) in chapters.keys():
                            chapters[int(chapter)] = torrent
                except:
                    continue
        return chapters
