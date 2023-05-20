import random

from wordpy.constants import *

def draw(box):
    top = TLC
    mid = VS
    bot = BLC

    cnt = len(box)

    for idx, txt in enumerate(box):
        sym = txt if txt != None else (SP + ' ' + SP)

        top += (3 * HS) + (TE if idx < cnt - 1 else TRC)
        mid += ' ' + sym + ' ' + VS
        bot += (3 * HS) + (BE if idx < cnt - 1 else BRC)

    return '\n'.join([top, mid, bot])

def rand():
    with open(WORDS) as words:
        word = next(words)

        for index, _word in enumerate(words, 2):
            if random.randrange(index):
                continue
            word = _word

        return word.strip()

def pick(choices):
    if len(choices) <= 0:
        return None

    choice = choices.pop(0)
    choices.append(choice)
    return choice
