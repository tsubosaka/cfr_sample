import cfr
import sys
import collections
from typing import List, Dict
import random


class LeducGame(cfr.AbstractGame):
    def __init__(self, deck):
        self.deck = deck

    def _is_flop(self, history : str):
        return 'C' in history

    def _current_round(self, history: str):
        if self._is_flop(history):
            return history.split("C")[1]
        return history

    def active_player(self, history: str) -> int:
        if self._is_flop(history):
            return 1 if len(self._current_round(history)) % 2 == 0 else 0
        return 0 if len(history) % 2 == 0 else 1

    def next_player(self, history: str, action : str) -> int:
        active_player = self.active_player(history)
        if action == 'f': # lose pot
            return active_player
        if self._is_flop(history):
            if action == 'c' and self._current_round(history) != '': # showdown
                return active_player
        else:
            if action == 'c' and len(history) >= 1: # go to flop
                return 1
        return 1 - active_player

    def _rank(self, hand: str):
        r = {'KK': 3, 'QQ' : 3, 'JJ' : 3, 'KQ' : 2 , 'KJ' : 2,
             'QK': 1, 'QJ' : 1, 'JQ' : 0, 'JK' : 0}
        return r[hand]

    def payoff(self, history: str) -> int:
        pay = 1
        SB = 2
        BB = 4
        if self._is_flop(history):
            raise_num = history.count('r')
            flop_action = self._current_round(history)
            flop_raise_num = flop_action.count('r')
            preflop_raise_num = raise_num - flop_raise_num
            pay += preflop_raise_num * SB
            if flop_action[-1] == 'f':
                if flop_raise_num > 0:
                    return - pay - (flop_raise_num - 1) * BB
                else:
                    return - pay
            # show down phase
            pay += flop_raise_num * BB
            active_player = self.active_player(history)
            r0 = self._rank(self.deck[0] + self.deck[2])
            r1 = self._rank(self.deck[1] + self.deck[2])
            if r0 == r1:
                return 0
            if active_player == 0:
                return pay if r0 < r1 else - pay
            else:
                return pay if r1 < r0 else - pay
            return pay
        else: #
            assert(history[-1] == 'f')
            raise_num = history.count('r')
            if raise_num > 0:
                return - pay - (raise_num - 1) * SB
            else:
                return - pay

    def is_chance(self, history) -> bool:
        if self._is_flop(history):
            return False
        if len(history) > 1 and history[-1] == 'c':
            return True
        return False

    def is_terminal(self, history) -> bool:
        if len(history) == 0:
            return False
        if history[-1] == 'f':
            return True
        if self._is_flop(history) and history[-1] == 'c' and len(self._current_round(history)) > 1:
            return True
        return False

    def get_info_set(self, i_map : Dict[str,cfr.InformationSet], history : str) -> cfr.InformationSet:
        active_player = self.active_player(history)
        hand = self.deck[active_player]
        if 'C' in history:
            hand += self.deck[2]
        key = hand + "|" + history
        if key not in i_map:
            cur_round_action = self._current_round(history)
            if cur_round_action.count("r") >= 2:
                info_set = cfr.InformationSet(key, 2)
            else:
                info_set = cfr.InformationSet(key, 3)
            i_map[key] = info_set
        return i_map[key]

    def __str__(self):
        return str(self.deck)

def train():
    deck = ['J' , 'J' , 'Q' , 'Q' , 'K' , 'K']
    i_map = {}
    exp = 0.0
    exp_hand = collections.Counter()
    N = 1000000
    for i in range(N):
        random.shuffle(deck)
        game = LeducGame(deck)
        result = cfr.cfr(game, i_map, "", 1.0 , 1.0, i % 2)
        exp += result
        exp_hand[deck[0] + deck[1] + deck[2]] += result
        if (i+1) % 10000 == 0:
            print(i, exp, file = sys.stderr)
            print(i, exp_hand, file = sys.stderr)
            exp = 0.0
            exp_hand = collections.Counter()

    for _, v in sorted(i_map.items(), key= lambda  x : (len(x[1].key) , x[1].key)):
        print(v)

train()