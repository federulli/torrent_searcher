"""from pirate_bay_searcher import PirateBaySearcher
s = PirateBaySearcher("https://thepiratebay.org/")
a = s.search_for_tv_show("spartacus", 2)
for key in a.keys():
    print(str(a[key].magnet_link))"""

"""
from yts_searcher import YTSSearcher

a = YTSSearcher('https://yts.am/api/v2')
p = a.search_movie('robocop 2')
print (p)"""
"""
from rarbg_searcher import RarbgSearcher

s = RarbgSearcher()
a = s.search_for_tv_show("The Haunting of Hill House", 1, 13)
for key in a.keys():
    print(key)
    print (a[key].download)
    print ("---------------------------------")
"""

from torrent_searcher.api import Searcher

a = Searcher().search_for_series("Outlander", 1, 23)
print (a)