import cfr
import sys
import collections
from typing import List, Dict
import random


class KuhnGame(cfr.AbstractGame):
    def __init__(self, deck):
        self.deck = deck

    def active_player(self, history: str) -> int:
        return 0 if len(history) % 2 == 0 else 1

    def next_player(self, history: str, action : str) -> int:
        active_player = self.active_player(history)
        if action == 'f':
            return active_player
        if action == 'c' and len(history) >= 1:
            return active_player
        return 1 - active_player

    def _rank(self, hand: str):
        r = {'K': 2, 'Q' : 1, 'J' : 0}
        return r[hand]

    def payoff(self, history: str) -> int:
        last = history[-1]
        if last == 'f':
            return -1
        active_player = self.active_player(history)
        r0 = self._rank(self.deck[0])
        r1 = self._rank(self.deck[1])
        pay = history.count('r') + 1
        if active_player == 0:
            return pay if r0 < r1 else - pay
        else:
            return pay if r1 < r0 else - pay

    def is_chance(self, history) -> bool:
        return False

    def is_terminal(self, history) -> bool:
        if len(history) == 0:
            return False
        if history[-1] == 'f':
            return True
        if history[-1] == 'c' and len(history) > 1:
            return True
        return False

    def get_info_set(self, i_map : Dict[str,cfr.InformationSet], history : str) -> cfr.InformationSet:
        active_player = self.active_player(history)
        hand = self.deck[active_player]
        key = hand + history
        if key not in i_map:
            if history.count("r") == 1:
                info_set = cfr.InformationSet(key, 2)
            else:
                info_set = cfr.InformationSet(key, 3)
            i_map[key] = info_set
        return i_map[key]

def train():
    deck = ['J' , 'Q', 'K']
    i_map = {}
    exp = 0.0
    exp_hand = collections.Counter()
    N = 100000
    for i in range(N):
        random.shuffle(deck)
        game = KuhnGame(deck)
        result = cfr.cfr(game, i_map, "", 1.0 , 1.0, i % 2)
        exp += result
        exp_hand[deck[0] + deck[1]] += result
        if (i+1) % 10000 == 0:
            print(i, exp, file = sys.stderr)
            print(i, exp_hand, file = sys.stderr)
            for _, v in sorted(i_map.items(), key= lambda  x : (len(x[1].key) , x[1].key)):
                print(v, file = sys.stderr)
            exp = 0.0
            exp_hand = collections.Counter()


train()