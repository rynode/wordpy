import asyncio

import wordpy.base as base
import wordpy.game as word

from wordpy.utils import draw, pick
from wordpy.constants import *
from wordpy.dialogues import *

class Master(base.Root):
    def __init__(self):
        base.Root.__init__(self)

        self.game = word.Game()

    async def on_text(self, text, nick):
        print("[info]", "[app]", "text:", nick, text)

    async def on_whisper(self, text, nick):
        print("[info]", "[app]",  "whisper:", nick, text)

        # strip text from extra garbage passed along
        text = text.replace("{} whispered: ".format(nick), "")
        text = text.lower()
        text = text.strip()

        if len(text) == 1 and text.isalpha():
            await self.do_guess(nick, text)
        elif text == 'quit':
            await self.do_quit()
        else:
            await self.whisper(nick, pick(WHISPER_UNKNOWN))

    async def on_login(self, nicks):
        print("[info]", "[app]", "login:", nicks)

        # remove own nick from nicks
        nicks.remove(self.nick)

        # announce welcoming text
        await self.say(pick(LOGIN_TOPIC))

        # add all nicks to the game
        for nick in nicks:
            await self.do_append(nick)

        # start a new round if any nicks in channel
        if len(nicks) > 0:
            await self.do_start()

    async def on_join(self, nick):
        print("[info]", "[app]", "join:", nick)

        # add new nick to the game
        await self.do_append(nick)

        # if a game is already in progress inform nick to wait
        # else start a new round.
        if self.game.is_active():
            await self.whisper(nick, pick(JOIN_WAIT))
        else:
            await self.do_start()

    async def on_leave(self, nick):
        print("[info]", "[app]", "leave:", nick)

        # remove nick from the game
        await self.do_remove(nick)

    async def on_warn(self, text):
        print("[info]", "[app]", "warning:", text)

    # begining of private action methods

    async def do_append(self, nick):
        status = self.game.append(nick)
        if status == 1:
            await self.whisper(nick, pick(APPEND_PLAYER))
        else:
            await self.whisper(nick, pick(APPEND_UNKNOWN))

    async def do_remove(self, nick):
        status = self.game.remove(nick)
        if status == 1:
            await self.say(pick(REMOVE_UNKNOWN))
        else:
            await self.say(pick(REMOVE_PLAYER))

        # if it's turn for nick and they are gone
        # inform next nick's turn

    async def do_start(self):
        status = self.game.start()
        if status == 1:
            await self.say(pick(START_EMPTY))
        else:
            # announce start of new round publicly.
            await self.say(pick(START_READY))
            # inform all players about their assinged chances.
            for player in self.game.players.values():
                await self.whisper(player.nick, pick(START_INFORM).format(player.chances))
            await self.do_print()

    async def do_guess(self, nick, text):
        status = self.game.guess(nick, text)
        if status == 1:
            await self.whisper(nick, pick(GUESS_UNKNOWN))
        elif status == 2:
            await self.whisper(nick, pick(GUESS_TURN))
        elif status == 3:
            await self.whisper(nick, pick(GUESS_BURNT))
        elif status == 4:
            await self.say(pick(GUESS_REPEATED).format(nick))
        elif status == 5:
            await self.say(pick(GUESS_INCORRECT).format(nick))
        else:
            await self.say(pick(GUESS_CORRECT).format(nick))

        if status >= 4 or status == 0:
            await self.do_recap(nick)

        if status >= 4:
            await self.do_inform(nick)

    async def do_recap(self, nick):
        status = self.game.recap()
        if status == 1:
            await self.say(pick(RECAP_EMPTY))
        elif status == 2:
            await self.say(pick(RECAP_REVEALED).format(self.game.turns[0].nick))
            await self.do_start()
        elif status == 3:
            await self.say(pick(RECAP_BURNT).format("".join(self.game.wordbox.letters)))
            await self.say(draw(self.game.wordbox.letters))
            await self.do_start()
        else:
            await self.do_print(nick)

    async def do_print(self, nick=""):
        # inform next nick's turn only if it differs from previous nick
        if nick != self.game.turns[0].nick:
            await self.say(pick(PRINT_TURN).format(self.game.turns[0].nick))

        # draw the wordbox
        await self.say(draw(self.game.wordbox.guessed))

        # inform previous wrong guesses if any
        if len(self.game.guesses) > 0:
            await self.say(pick(PRINT_GUESS).format(" ".join(self.game.guesses)))

    async def do_inform(self, nick):
        if nick not in self.game.players.keys():
            return

        player = self.game.players[nick]

        if player.is_burnt():
            await self.say(pick(INFORM_BURNT).format(nick))
        else:
            await self.whisper(nick, pick(INFORM_CHANCES).format(player.chances, "s" if player.chances != 1 else ""))

    async def do_quit(self):
        await self.say(pick(QUIT_SIGNAL))
        raise Exception("quit signal received, terminating . . .")
