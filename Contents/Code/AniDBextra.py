import re
import os
import common

def getAltName(typ,id,default):
  try:
    headers = {'pragma': 'no-cache',
               'x-lcontrol': 'x-no-cache',
               'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    API = 'http://anidb.net/perl-bin/animedb.pl?show=json&action=info_popup&type={}&id={}'
    c = common.LoadFile(filename="{}-{}.json".format(typ,id),
                        relativeDirectory=os.path.join("AniDB", "json"), url=API.format(typ,id),
                        cache=CACHE_1DAY*365*100, headers=headers)
    regex = r"alternateName.*?>(.*?)<"
    matches = list(re.finditer(regex, c['html'], re.MULTILINE))
    match = matches[-1].group(1)
    assert match != ""
    return match
  except Exception:
    return default