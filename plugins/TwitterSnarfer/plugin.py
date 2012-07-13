###
# Copyright (c) 2011, Michael B. Klein
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

import simplejson
import supybot.utils.web as web
import time
import urllib2
from urllib import urlencode, quote
import httplib
from BeautifulSoup import BeautifulStoneSoup as BSS
from random import randint

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Twitter Plugin; http://code4lib.org/irc)')
SNARFERS = ['binged.it','bit.ly','fb.me','goo.gl','is.gd','ow.ly','su.pr','tinyurl.com','tr.im','youtu.be']

class TwitterSnarfer(callbacks.PluginRegexp):
  regexps = ['tweetSnarfer']#,'shortUrlSnarfer']

  def _fetch_json(self, url):
      doc = web.getUrl(url, headers=HEADERS)
      try:
          json = simplejson.loads(doc)
      except ValueError:
          return None
      return json

  def tweetSnarfer(self, irc, msg, match):
    r'https?://(?:www\.)?twitter\.com.*/status(?:es)?/([0-9]+)'
    print match.group(1)
    tweet_id = match.group(1)
  
    def recode(text):
        return BSS(text.encode('utf8','ignore'), convertEntities=BSS.HTML_ENTITIES)

    def lengthen_urls(tweet):
        for link in tweet['entities']['urls']:
            tweet['text'] = tweet['text'].replace(link['url'], link['expanded_url'])
        for media in tweet['entities']["media"]:
            tweet['text'] = tweet['text'].replace(media['url'], media['media_url'])

    resp = 'Gettin nothin from teh twitter.'
    url = 'http://api.twitter.com/1/statuses/show/%s.json?include_entities=true' % (tweet_id)
    tweet = self._fetch_json(url)
    lengthen_urls(tweet)
    resp = "<%s> %s" % (tweet['user']['screen_name'], recode(tweet['text']))
    irc.reply(resp.replace('\n',' ').strip(' '), prefixNick=False)

  def shortUrlSnarfer(self, irc, msg, match):
    r'https?://(binged.it|bit.ly|fb.me|goo.gl|is.gd|ow.ly|su.pr|tinyurl.com|tr.im|youtu.be)(/[^\s,;.]+)'
    snarks = ["I believe you're referring to <%s>","Don't you mean <%s>?","C'mon, <%s> is where it's really at."]
    domain = match.group(1)
    path = match.group(2)
    conn = httplib.HTTPConnection(domain)
    conn.request("HEAD", path)
    res = conn.getresponse()
    print res.status
    if res.status == 301 or res.status == 302:
      resolved = res.getheader('location')
      snark = snarks[randint(0,len(snarks)-1)]
      irc.reply(snark % resolved, prefixNick=True)
    
Class = TwitterSnarfer


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
