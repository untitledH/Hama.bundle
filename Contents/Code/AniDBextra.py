try:
    from urllib.request import Request, urlopen  # Python 3
except ImportError:
    from urllib2 import Request, urlopen  # Python 2

def getAltName(typ,id,default=None):
	try:
		import re
		headers = {'pragma': 'no-cache',
	               'x-lcontrol': 'x-no-cache',
	               'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
		api = 'http://anidb.net/perl-bin/animedb.pl?show=json&action=info_popup&type={}&id={}'
		r = Request(api.format(typ,id))
		for k in headers:
			r.add_header(k,headers[k])
		c = urlopen(r).read().decode('utf-8')
		regex = r"alternateName.*?>(.*?)<"
		matches = list(re.finditer(regex, c, re.MULTILINE))
		match = matches[-1].group(1)
		assert match != ""
		return match
	except Exception:
		return default
