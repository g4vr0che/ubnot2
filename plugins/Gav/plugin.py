###
# Copyright (c) 2015 G4vr0che
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

import re
import random

import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Gav(callbacks.Plugin):
    def fuchs(self, irc, msg, args, nick):
        """[<victim>]
        
        Causes the <victim> to wake up a grumpy fox.
        """
        irc.reply('%s accidentally snaps a twig and wakes up a very grumpy fox.' % nick)
        if random.randrange(0,2):
            irc.reply('*OMNOMNOMNOM* %s is quickly gobbled up and quite delicious!' % nick)
        else:
            irc.reply('*YAWN* Thankfully, the fox looks uninterested and ignores %s.' % nick)
    fuchs = wrap(fuchs, [('nick')])
    
    def shoot(self, irc, msg, args, nick):
        """[<victim>]

        Shoots the <victim>. 
        """
        shot = random.randrange(0,5)
        if shot == 1:
            irc.reply('shoots %s in the chest with a handgun.' % nick, action=True)
        elif shot == 2:
            irc.reply('shoots %s repeatedly with an automatic assault rifle' % nick, action=True)
        elif shot == 3:
            irc.reply('shoots %s at a distance with a sniper rifle.' % nick, action=True)
        elif shot == 4: 
            irc.reply('shoots %s with a shotgun.' % nick, action=True)
            irc.reply('%s flies backwards and falls over.' % nick)
        else:
            irc.reply('shoots at %s but misses. Lucky!' % nick, action=True)
            return 0
        
        irc.reply('*BANG* %s dies and will be sorely missed. =(' % nick)
    shoot = wrap(shoot, [('nick')])
    
    def guillotine(self, irc, msg, args, nick):
        """[<victim>]

        Uses the guillotine on the <victim>!
        """
        
        irc.reply('straps %s into the guillotine. After a dramatic pause, the blade is dropped.' % nick, action=True)
        irc.reply('*SWICK* %s dies and will be sorely missed. =(' % nick)
    guillotine = wrap(guillotine, [('nick')])
    
    def stab(self, irc, msg, args, nick):
        """[<victim>]

        Stabs <victim> with some kind of sharp implement!
        """
        
        stabbing = random.randrange(0,5)
        if stabbing == 1:
            irc.reply('runs up to %s and runs them through with a saber.' % nick, action=True)
            irc.reply("The blade pokes cleanly through %s's back." % nick)
        elif stabbing == 2:
            irc.reply('sneaks up silently behind %s and pokes a dagger through their back.' % nick, action=True)
        elif stabbing == 3:
            irc.reply('faces his opponent, %s, and silently draws his katana.' % nick, action=True)
            irc.reply("dashes forward like the wind, slicing across %s's belly." % nick, action=True)
        elif stabbing == 4:
            irc.reply('draws a rapier and pokes through %s several times.' % nick, action=True)
        else: 
            irc.reply('tries to stab %s but misses. Lucky.' % nick, action=True)
            return 0
        
        irc.reply('*SWICK* %s dies and will be sorely missed. =(' % nick)
    stab = wrap(stab, [('nick')])
    
    def hug(self, irc, msg, args, nick):
        """[<victim>]

        Hugs the <victim>. Wait, why are they a victim again?
        """
        
        irc.reply('hugs %s lovingly' % nick, action=True)
    hug = wrap(hug, [('nick')])
    
    def slap(self, irc, msg, args, nick):
        """[<victim>]

        Slaps the <victim>.
        """
        
        irc.reply('slaps %s' % nick, action=True)
    slap = wrap(slap, [('nick')])
    
    def trout(self, irc, msg, args, nick):
        """[<victim>]

        Slaps the <victim> around a bit with a large trout.
        """
        
        irc.reply('slaps %s around a bit with a large trout.' % nick, action=True)
    trout = wrap(trout, [('nick')])
    
    def crossbow(self, irc, msg, args, nick):
        """[<victim>]

        Shoots the <victim> with a crossbow!
        """
        
        irc.reply('While skiing in the Swiss Alps, %s is mysteriously shot with a crossbow.' % nick)
        irc.reply('*FWUMP* %s dies and will be sorely missed. =(' % nick)
    crossbow = wrap(crossbow, [('nick')])

Class = Gav


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
