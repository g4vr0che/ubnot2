# -*- Encoding: utf-8 -*-
###
# Copyright (c) 2006-2007 Dennis Kaarsemaker
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import random, re, time, subprocess, urllib.request, urllib.error, urllib.parse
import supybot.ircmsgs as ircmsgs
import supybot.conf as conf
import threading
import os

mess = {
    'bofh':        ('BOFH excuses', '%s/bofh.txt' % os.path.split(os.path.abspath(__file__))[0], 'BOFH Excuse #%d: ', False),
    '42':          ('HHGTTG quotes', '%s/42.txt' % os.path.split(os.path.abspath(__file__))[0], '', False),
    'magic8ball':       ('The magic 8ball', '%s/ball.txt' % os.path.split(os.path.abspath(__file__))[0], '', False),
    'ferengi':     ('Ferengi rules of acquisition', '%s/ferengi.txt' % os.path.split(os.path.abspath(__file__))[0], 'Ferengi rule of acquisition ', False),
}
data = {}
for m in mess.keys():
    if mess[m][1].startswith('http'):
        mess[m] = (mess[m][0], mess[m][1],re.compile(mess[m][2], re.I|re.DOTALL), mess[m][3])
    else:
        fd = open(mess[m][1])
        data[mess[m][1]] = [x.strip() for x in fd.readlines()]
        fd.close()

badwords = ['sex','masturbate','fuck','rape','dick','pussy','prostitute','hooker',
            'orgasm','sperm','cunt','penis','shit','piss','urin','bitch','semen','cock',
            'retard', 'cancer', 'hiv', 'aids']
tagre = re.compile(r'<.*?>')
def filter(txt,off):
    _txt = txt.lower()
    if not off:
        for b in badwords:
            if b in _txt:
                return None
    txt = txt.replace('<br />','').replace('\n','').replace('\r','')
    txt = txt.replace('<i>','/').replace('</i>','/').replace('<b>','*').replace('</b>','*')
    txt = txt.replace('&quot;','"').replace('&lt;','<').replace('&gt;','>')
    txt = tagre.sub('',txt)
    return txt

times = {}

def ok(func):
    def newfunc(*args, **kwargs):
        global time
        plugin = args[0]
        channel = args[2].args[0]
        if not channel.startswith('#'):
            delay = 5
        else:
            if not plugin.registryValue('enabled', channel):
                return
            delay = plugin.registryValue('delay', channel)
        if channel not in times.keys():
            times[channel] = time.time()
        elif times[channel] < time.time() - delay:
            times[channel] = time.time()
        else:
            return
        i=0
        func(*args, **kwargs)
    newfunc.__doc__ = func.__doc__
    return newfunc

class Mess(callbacks.PluginRegexp):
    """Random Mess plugin"""
    threaded = True
    regexps = ['hugme']
    hugs = ["hugs %s","gives %s a big hug","gives %s a sloppy wet kiss",
            "huggles %s","squeezes %s","humps %s"]


    def isCommandMethod(self, name):
        if not callbacks.PluginRegexp.isCommandMethod(self, name):
            if name in mess:
                return True
            else:
                return False
        else:
            return True

    def listCommands(self):
        commands = callbacks.PluginRegexp.listCommands(self)
        commands.remove('messcb')
        commands.extend(mess.keys())
        commands.sort()
        return commands

    def getCommandMethod(self, command):
        try:
            return callbacks.PluginRegexp.getCommandMethod(self, command)
        except AttributeError:
            return self.messcb

    def getCommandHelp(self, command):
        try:
            return callbacks.PluginRegexp.getCommandMethod(self, command)
        except AttributeError:
            return mess[command[0]][0]

    def _callCommand(self, command, irc, msg, *args, **kwargs):
        method = self.getCommandMethod(command)
        if command[0] in mess:
            msg.tag('messcmd', command[0])
        try:
            method(irc, msg, *args, **kwargs)
        except Exception as e:
            self.log.exception('Mess: Uncaught exception in %s.', command)
            if conf.supybot.reply.error.detailed():
                irc.error(utils.exnToString(e))
            else:
                irc.replyError()
    
    @ok
    def messcb(self, irc, msg, args, text):
        """General mess"""
        t = threading.Thread(target=self.messthread, args=(irc, msg, args, text))
        t.start()

    def messthread(self, irc, msg, args, text):
        global data
        cmd = msg.tagged('messcmd')
        try:
            (doc, loc, tx, off) = mess[cmd]
        except:
            cmd = cmd[1:]
            (doc, loc, tx, off) = mess[cmd]
        if off and not self.registryValue('offensive', msg.args[0]):
            return
        if loc.startswith('http'):
            i = 0
            while i < 5:
                inp = utils.web.getUrl(loc)
                fact = tx.search(inp).group('fact')
                fact = filter(fact,off)
                if fact:
                    irc.reply(fact)
                    return
                i += 1
        else:
            i = random.randint(0,len(data[loc])-1)
            if '%d' in tx:
                tx = tx % i
            irc.reply(tx + data[loc][i])
    messcb = wrap(messcb, [additional('text')])

    # WARNING: depends on an alteration in supybot/callbacks.py - don't do
    # str(s) if s is unicode!
    @ok
    def dice(self, irc, msg, args, count):
        """[<count>]
        Roll the dice, if count is given then roll that many times.
        """
        if not count: count = 1 
        elif count > 5: count = 5
        elif count < 1: count = 1
        t = ' '.join([x.__call__(["\u2680","\u2681","\u2682","\u2683","\u2684","\u2685"]) for x in [random.choice]*count])
        irc.reply(t)
    dice = wrap(dice, [additional('int')])

    @ok
    def hugme(self, irc, msg, match):
        r""".*hug.*ubotu"""
        irc.queueMsg(ircmsgs.action(msg.args[0], self.hugs[random.randint(0,len(self.hugs)-1)] % msg.nick))

    @ok
    def fortune(self, irc, msg, args):
        """ Display a fortune cookie """
        f = subprocess.getoutput('/usr/games/fortune -s')
        f.replace('\t','    ')
        f = f.split('\n')
        for l in f:
            if l:
                irc.reply(l)
    fortune = wrap(fortune)

    @ok
    def ofortune(self, irc, msg, args):
        """ Display a possibly offensive fortune cookie """
        if not self.registryValue('offensive', msg.args[0]):
            return
        f = subprocess.getoutput('/usr/games/fortune -so')
        f.replace('\t','    ')
        f = f.split('\n')
        for l in f:
            if l:
                irc.reply(l)
    ofortune = wrap(ofortune)

    @ok
    def pony(self, irc, msg, args, text):
        """[<user>]
        Can you or <user> have a pony?
        """
        if not text:
            text = 'you'
        irc.reply("No %s can't have a pony, %s!" % (text, msg.nick))
    pony = wrap(pony, [additional('text')])
    
    @ok
    def magicball(self, irc, msg, args, text):
        """[<user>]
        The magic 8 ball!
        """
        replies = [
            'Yes',
            'No',
            'Most likely',
            'Definitely not',
            'Ask again later',
            'Maybe',
            'Could be',
            'Only when it rains',
            'Let\'s hope not',
            'I don\'t think so',
            'Are you kidding me?',
            'Of course',
            'When pigs fly',
            'No way',
            'Definitely',
            'Of course',
            'Hell no!',
            'Hell yeah!',
            'Keep on dreaming',
            'The stars say so',
            'I have no doubts about it',
            'Forty-Two!',
            'Your guess is as good as mine',
            'Maybe',
            'That seems to be right',
            'That seems to be wrong'
        ]
        rep = random.choice(replies)
        irc.reply(rep)
    magicball = wrap(magicball, [additional('text')])
    
    @ok
    def hoersi(self, irc, msg, args, text):
        """[<user>]
        Can you or <user> have a hoers?
        """
        if not text:
            text = 'you'
        irc.reply("No they can't... OK fine, %s can have a hoers %s!" % (text, msg.nick))
    hoersi = wrap(hoersi, [additional('text')])

    def callPrecedence(self, irc):
        before = []
        for cb in irc.callbacks:
            if cb.name() == 'IRCLogin':
                before.append(cb)
        return (before, [])

    def inFilter(self, irc, msg):
        if not msg.command == 'PRIVMSG':
            return msg
        if not conf.supybot.defaultIgnore():
            return msg
        s = callbacks.addressed(irc.nick, msg)
        if not s:
            return msg
        if checkIgnored(msg.prefix):
            return msg
        try:
            if ircdb.users.getUser(msg.prefix):
                return msg
        except:
            pass
        cmd, args = (s.split(None, 1) + [None])[:2]
        if cmd and cmd[0] in str(conf.supybot.reply.whenAddressedBy.chars.get(msg.args[0])):
            cmd = cmd[1:]
        if cmd in self.listCommands():
            tokens = callbacks.tokenize(s, channel=msg.args[0])
            self.Proxy(irc, msg, tokens)
        return msg
#        self._callCommand([cmd], irc, msg, [])
Class = Mess
