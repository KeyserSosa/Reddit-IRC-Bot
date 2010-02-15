###
# Copyright (c) 2010, Christopher Slowe
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re 
from reddit import RedditSession
from mako.filters import url_escape

reddit = RedditSession()

domain_re = re.compile(r"(http://\S+)")
reddit_re = re.compile(r"(http://([^/]*\.)?reddit.com/\S*)")
reddituser_re = re.compile(r"(http://([^/]*\.)?reddit.com/user/(?P<username>[^/]+))")

def find_links(text):
    print "HERE", text
    links = domain_re.findall(text)
    for link in links:
        m = reddit_re.match(link)
        if m:
            m = reddituser_re.match(link)
            if m:
                d = m.groupdict()
                res = reddit.API_GET("/user/%s/about.json" % d['username'])
                d = res.get("data")
                if d:
                    yield ("User '%(name)s' has karma %(link_karma)s" % d)
        else:
            res = reddit.API_GET("/api/info.json?limit=1&url=%s" %
                                 url_escape(link))
            d = res.get("data", {}).get("children", [{}])[0].get("data",{}) 
            if d:
                d['link'] = link
                yield ("%(url)s ==> http://www.reddit.com/r/%(subreddit)s/comments/%(id)s/ which has %(ups)s ups and %(downs)s downs." % d)


class RedditLinks(callbacks.Plugin):
    """Add the help for "@plugin help RedditLinks" here
    This should describe *how* to use this plugin."""
    noIgnore = True
    def __init__(self, irc):
        self.__parent = super(RedditLinks, self)
        self.__parent.__init__(irc)

    def __call__(self, irc, msg):
        self.__parent.__call__(irc, msg)
        recipients, text = msg.args
        print irc.__class__
        return "\n".join(l for l in find_links(text))

Class = RedditLinks


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
