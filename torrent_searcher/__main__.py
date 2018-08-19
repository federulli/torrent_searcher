from pirate_bay_searcher import PirateBaySearcher
s = PirateBaySearcher("https://thepiratebay.org/")
a = s.search_for_tv_show("luke cage", 2)
for key in a.keys():
    print(str(a[key].magnet_link))


"""from yts_searcher import YTSSearcher

a = YTSSearcher('https://yts.am/api/v2')
p = a.search_movie('robocop 2')
print (p)"""