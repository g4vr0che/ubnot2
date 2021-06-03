###
# Copyright (c) 2021, Gaven Royer
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

import os
import sys
import json
from datetime import timedelta
from dateutil import parser, tz
from pathlib import Path

import supybot.log as log
import supybot.utils as utils
from supybot.commands import *
import supybot.callbacks as callbacks

if sys.version_info[0] < 3:
    from urlparse import urlparse, parse_qs
    from urllib2 import urlopen
else:
    from urllib.parse import urlparse, parse_qs
    from urllib.request import urlopen

try:
    from supybot.i18n import PluginInternationalization
    from supybot.i18n import internationalizeDocstring
    _ = PluginInternationalization('Gavyoutube')
except:
    _ = lambda x: x
    internationalizeDocstring = lambda x: x

def _readApiKey(fil='api-key.txt'):
    log.info('Loading API key')
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    log.info(str(dir_path))
    with open(dir_path / fil) as api_file:
        key = api_file.readline()
    return key

def get_isosplit(s, split):
    if split in s:
        n, s = s.split(split)
    else:
        n = 0
    return n, s


def parse_isoduration(s):
        
    # Remove prefix
    s = s.split('P')[-1]
    
    days = None
    hours = None
    minutes = None
    seconds = None
    
    # Step through letter dividers
    days, s = get_isosplit(s, 'D')
    _, s = get_isosplit(s, 'T')
    hours, s = get_isosplit(s, 'H')
    minutes, s = get_isosplit(s, 'M')
    seconds, s = get_isosplit(s, 'S')

    # Convert all to seconds
    dt = timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))
    return dt

@internationalizeDocstring
class Gavyoutube(callbacks.PluginRegexp):
    """Listens for Youtube URLs and retrieves video info."""
    threaded = True
    regexps = ['youtubeSnarfer']
    _api_key = _readApiKey()
    
    _api_url = 'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={}&key={}'

    def _youtubeId(self, value):
        query = urlparse(value)
        yid = None
        if query.hostname == 'youtu.be':
            yid = query.path[1:]
        elif query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                yid = parse_qs(query.query)['v'][0]
            elif (query.path[:7] == '/embed/'
                  or query.path[:3] == '/v/'):
                yid = query.path.split('/')[2]
        elif (query.hostname == 'm.youtube.com'
              and query.path == '/watch'):
            yid = parse_qs(query.query)['v'][0]
        elif (query.hostname == 'youtube.googleapis.com'
              and query.path[:3] == '/v/'):
            yid = query.path.split('/')[2]
        return yid

    def youtubeSnarfer(self, irc, msg, match):
        channel = msg.args[0]
        if not irc.isChannel(channel):
            return
        if self.registryValue('youtubeSnarfer', channel):
            ytid = self._youtubeId(match.group(0))
            if ytid:
                try:
                    apiReq = urlopen(self._api_url.format(ytid, self._api_key))
                except:
                    log.error("Couldn't connect to Youtube's API.")
                    apiReq = None

                if apiReq:
                    if sys.version_info[0] < 3:
                        apiRes = apiReq.read()
                    else:
                        cntCharset = apiReq.headers.get_content_charset()
                        apiRes = apiReq.read().decode(cntCharset)

                    apiRes = json.loads(apiRes)

                    if 'items' in apiRes:
                        vInfo = apiRes['items'][0]
                        vSnippet = vInfo['snippet']
                        vDetails = vInfo['contentDetails']
                        vStats = vInfo['statistics']

                        s = format("YouTube: \x02%s\x02", vSnippet['title'])

                        if 'duration' in vDetails:
                            dur = str(parse_isoduration(vDetails['duration'])).split(':')
                            durstr = ''
                            
                            if dur[0] != '0':
                                durstr += f'{dur[0]}d'
                            durstr += f'{dur[1]}m{dur[2]}s'
                            
                            s += format(" - length: \x02%s\x02", durstr)

                        if 'viewCount' in vStats:
                            s += format(_(" - \x02%s\x02 views"),
                                        "{:,}".format(int(vStats['viewCount'])))

                        if 'likeCount' in vStats and 'dislikeCount' in vStats:
                            s += format(_(" - \x02%s\x02 likes / %s dislikes"),
                                        vStats['likeCount'],
                                        vStats['dislikeCount'])

                        if 'channelTitle' in vSnippet:
                            s += format(_(" - by \x02%s\x02"),
                                        vSnippet['channelTitle'])

                        if 'publishedAt' in vSnippet:
                            published_date = parser.parse(vSnippet['publishedAt']).astimezone(tz.tzlocal())
                            s += format(_(" on \x02%s\x02"),
                                        str(published_date).split()[0])

                        irc.reply(s, prefixNick=False)

    youtubeSnarfer = urlSnarfer(youtubeSnarfer)
    youtubeSnarfer.__doc__ = utils.web._httpUrlRe

Class = Gavyoutube


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
