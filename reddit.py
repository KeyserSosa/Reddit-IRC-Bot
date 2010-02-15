import httplib, urllib
from mako.filters import url_escape
from BeautifulSoup import BeautifulSoup
import simplejson

def query_string(dict):
    pairs = []
    for k,v in dict.iteritems():
        if v is not None:
            try:
                k = url_escape(unicode(k).encode('utf-8'))
                v = url_escape(unicode(v).encode('utf-8'))
                pairs.append(k + '=' + v)
            except UnicodeDecodeError:
                continue
    if pairs:
        return '&'.join(pairs)
    else:
        return ''


class Session(object):
    ignore_cookies = []
    def __init__(self, domain, port = 80):
        self.domain = domain
        self.port = port
        self.cookies = {}

    def GET(self, page, headers = {}):
        return self.request("GET", page, "", headers = headers)

    def POST(self, page, params, headers = {}):
        headers.update({"Content-type": "application/x-www-form-urlencoded"})
        return self.request("POST", page, urllib.urlencode(params),
                            headers = headers)

    def request(self, method, page, params, headers = {}):
        # build up cookie headers
        for name, value in self.cookies.iteritems():
             headers.setdefault("cookie", "")
             if headers["cookie"]:
                 headers["cookie"] += ";"
             headers["cookie"] += "%s=%s" % (name, value)
        # make connection
        conn = httplib.HTTPConnection(self.domain, self.port)
        conn.request(method, page, params, headers)
        r = conn.getresponse()
        # store set cookies
        for name, value in r.getheaders():
            if name == "set-cookie":
                value = value.split("=")
                if value[0] not in self.ignore_cookies:
                    self.cookies[value[0]] = "=".join(value[1:])

        res = r.read()
        conn.close()
        return res

class RedditSession(Session):
    ignore_cookies = ["reddit_first"]
    def __init__(self, user = None, password = None, 
                 domain = "www.reddit.com", port = 80):
        self.modhash = None
        self.user = user
        Session.__init__(self, domain, port)
        if user and password:
            r = self.API("login", dict(user = user, passwd = password))
            if r:
                r = r['json']
                if not r['errors']:
                    self.modhash = r['data']['modhash']

    def API_POST(self, path, params):
        params.setdefault("api_type", "json")
        if self.modhash:
            params['uh'] = self.modhash
        try:
            return simplejson.loads(self.POST("/api/%s" % path, params))
        except ValueError:
            return {}


    def API_GET(self, path):
        if self.modhash:
            params['uh'] = self.modhash
        try:
            return simplejson.loads(self.GET(path))
        except ValueError:
            return {}

