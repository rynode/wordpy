import random

from wordpy.utils import rand

class Game():
    def __init__(self):
        self.wordbox = None
        self.players = dict()
        self.guesses = set()
        self.turns = list()

    def append(self, nick):
        if nick in self.players.keys():
            return 1

        player = Player(nick)
        self.players.update({nick: player})
        return 0

    def remove(self, nick):
        if nick not in self.players.keys():
            return 1

        player = self.players.pop(nick)
        self.turns.remove(player)
        return 0

    def start(self):
        if len(self.players.keys()) <= 0:
            return 1

        # load a new word into wordbox.
        self.wordbox = Wordbox()
        self.wordbox.load()

        # clear previous guessses.
        self.guesses.clear()

        # construct random turns list.
        self.turns.clear()
        for player in self.players.values():
            self.turns.append(player)
        random.shuffle(self.turns)

        # give players random chances.
        maximum = len(self.wordbox.letters)
        minimum = int(maximum / len(self.players.keys()))
        for player in self.players.values():
            player.charge(minimum, maximum)

        return 0

    def guess(self, nick, letter):
        if nick not in self.players.keys():
            return 1

        # check if it is player's turn.
        if nick != self.turns[0].nick:
            return 2

        player = self.players[nick]

        # check if player has chances.
        if player.is_burnt():
            return 3

        status = self.wordbox.guess(letter)
        if status == 0:
            # correct guess, do nothing.
            return 0
        if status == 2:
            # for incorrect guess:
            # add letter to previous guesses.
            self.guesses.add(letter)
        # for incorrect and repeated guesses:
        # punish player by reducing chances.
        player.punish()
        # choose next player's turn.
        self._next()
        # 5: incorrect, 4: repeated
        return 3 + status

    def recap(self):
        if len(self.players.keys()) <= 0:
            # no players
            return 1

        if self.wordbox.is_revealed():
            # guessed
            return 2

        for player in self.players.values():
            if player.is_alive():
                return 0

        # all burnt
        return 3

    def is_active(self):
        return len(self.turns) > 0

    def is_booted(self):
        return len(self.players.keys()) > 0

    def _next(self):
        # remove player from the head of turns queue.
        player = self.turns.pop(0)

        # only restore alive players to the tail of turns queue.
        if player.is_alive():
            self.turns.append(player)

class Player():
    def __init__(self, nick):
        self.nick = nick
        self.chances = 0

    def punish(self):
        self.chances -= 1

    def charge(self, minimum, maximum):
        self.chances = random.randint(minimum, maximum)

    def is_alive(self):
        return self.chances > 0

    def is_burnt(self):
        return self.chances <= 0

class Wordbox():
    def __init__(self):
        self.letters = list()
        self.guessed = list()

    def load(self):
        self.letters.clear()
        self.guessed.clear()

        for letter in list(rand()):
            self.letters.append(letter)
            self.guessed.append(None)

    def guess(self, letter):
        if letter in self.guessed:
            # repeated 
            return 1

        if letter not in self.letters:
            # incorrect
            return 2

        # correct
        for index, _letter in enumerate(self.letters):
            if letter == _letter:
                self.guessed[index] = letter

        return 0

    def is_revealed(self):
        return len(self.letters) > 0 and self.letters == self.guessed
