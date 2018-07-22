from pirate_bay_searcher import PirateBaySearcher
s = PirateBaySearcher("https://thepiratebay.org/")
a = s.search_for_tv_show("luke cage", 2)
a.keys().sort()
for key in a:
    print str(a[key].magnet_link)
