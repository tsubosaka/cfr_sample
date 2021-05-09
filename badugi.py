import cfr
import sys
import re
import time
import collections
from typing import List, Dict
import random

NUM_ROUND = 2
MAX_BET_NUM = 2

class BadugiGame(cfr.AbstractGame):
    def __init__(self, deck: List[int], oop_badugi : int):
        self.deck = deck
        self.oop_badugi = oop_badugi

    @staticmethod
    def num_draw(history: str) -> int:
        return history.count('1')

    def active_player(self, history: str) -> int:
        if len(history) == 0:
            return 0
        last_action = history[-1]
        if last_action == '0' or last_action == '1':
            return 0
        arr = re.split("0|1", history)
        cur_round = arr[-1]
        if last_action == 'c' and len(cur_round) > 1 and len(arr) < NUM_ROUND:
            return 1
        if last_action == 'c' and cur_round != 'c' and len(arr) >= NUM_ROUND:
            return 1 if len(cur_round) % 2 == 0 else 0
        return 0 if len(cur_round) % 2 == 0 else 1

    def next_player(self, history: str, action : str) -> int:
        if action == '0' or action == '1':
            return 0
        active_player = self.active_player(history)
        if action == 'f': # lose pot
            return active_player
        arr = re.split("0|1", history)
        cur_round = arr[-1]
        if action == 'c' and len(cur_round) > 0:
            if len(arr) < NUM_ROUND:
                return 1
            # show down
            return active_player
        return 1 - active_player

    @staticmethod
    def calc_pay(history: str) -> float:
        initial_pot_size = 11.5
        arr = re.split("0|1", history)
        SB = 2
        BB = 2
        if history[-1] == 'f':
            sb_raise_count = arr[0].count("r")
            if len(arr) == 1:
                if sb_raise_count > 0:
                    return initial_pot_size * 1 + (sb_raise_count - 1) * SB
                else:
                    return initial_pot_size * 1
            tot_raise_count = history.count("r")
            bb_raise_count = tot_raise_count - sb_raise_count
            pay = initial_pot_size * 1 + sb_raise_count * SB
            if bb_raise_count > 0:
                return pay + (bb_raise_count - 1) * BB
            else:
                return pay
        sb_raise_count = arr[0].count("r")
        tot_raise_count = history.count("r")
        bb_raise_count = tot_raise_count - sb_raise_count
        pay = initial_pot_size * 1 + sb_raise_count * SB + bb_raise_count * BB
        return pay

    @staticmethod
    def calc_pay_pot_limit(history: str) -> float:
        initial_pot_size = 20
        pay = initial_pot_size
        arr = re.split("0|1", history)
        if history[-1] == 'f':
            half_pot_bets = [0, 0.5, 1.5, 3.5, 7.5]
            pre_raise_count = arr[0].count("r")
            if len(arr) == 1:
                if pre_raise_count <= 1:
                    return pay
                pre_raise_count -= 1
                return pay + half_pot_bets[pre_raise_count] * initial_pot_size
            pot_size = initial_pot_size + 2 * half_pot_bets[pre_raise_count] * initial_pot_size
            pay += half_pot_bets[pre_raise_count] * initial_pot_size
            last_raise_count = arr[1].count("r") - 1
            if last_raise_count <= 0:
                return pay
            pot_bets = [0, 1, 4, 13, 40]
            pay += pot_size * pot_bets[last_raise_count]
            return pay
        half_pot_bets = [0, 0.5, 1.5, 3.5, 7.5]
        pre_raise_count = arr[0].count("r")
        pot_size = initial_pot_size + 2 * half_pot_bets[pre_raise_count] * initial_pot_size
        pay += half_pot_bets[pre_raise_count] * initial_pot_size
        pot_bets = [0, 1, 4, 13, 40]
        last_raise_count = arr[1].count("r")
        pay += pot_size * pot_bets[last_raise_count]
        return pay

    def payoff(self, history: str) -> float:
#        pay = self.calc_pay(history)
        pay = self.calc_pay_pot_limit(history)
        if history[-1] == 'f':
            return - pay
        active_player = self.active_player(history)
        r0 = self.oop_badugi
        r1 = self.deck[self.num_draw(history)]
        if r0 < r1:
            if active_player == 0:
                return pay
            else:
                return - pay
        else:
            if r0 == r1 and (r0 <= 5):
                return 0
            if active_player == 0:
                return - pay
            else:
                return pay

    def is_chance(self, history) -> bool:
        return False

    def is_terminal(self, history) -> bool:
        if len(history) == 0:
            return False
        if history[-1] == 'f':
            return True
        arr = re.split("0|1", history)
        if len(arr) == NUM_ROUND and history[-1] == 'c' and arr[-1] != 'c':
            return True
        return False

    def get_info_set(self, i_map : Dict[str,cfr.InformationSet], history : str) -> cfr.InformationSet:
        active_player = self.active_player(history)
        if active_player == 0:
            hand = str(self.oop_badugi)
        else:
            r = self.deck[self.num_draw(history)]
            hand = str(r)
        key = hand + "|" + history
        arr = re.split("0|1", history)
        if key not in i_map:
            cur_round_action = arr[-1]
            if len(cur_round_action) == 0:
#                info_set = cfr.InformationSet(key, 3, ['f', 'c' , 'r'])
                info_set = cfr.InformationSet(key, 1, ['r'])
            elif len(arr) < NUM_ROUND and cur_round_action[-1] == 'c' and cur_round_action != 'c':
                info_set = cfr.InformationSet(key, 2, ['0', '1'])
            elif cur_round_action.count("r") >= MAX_BET_NUM:
                info_set = cfr.InformationSet(key, 2, ['f', 'c'])
#                info_set = cfr.InformationSet(key, 1, ['c'])
            else:
                info_set = cfr.InformationSet(key, 3, ['f', 'c', 'r'])
#                info_set = cfr.InformationSet(key, 1, ['c'])
            i_map[key] = info_set
        return i_map[key]

    def get_chance_reslut(self, history: str) -> str:
        return None

    def __str__(self):
        return str(self.deck)



def sample_badugi(num_combo : List[int]):
    tot_combo = sum(num_combo)
    r = random.randint(1, tot_combo)
    S = 0
    for i in range(len(num_combo)):
        S += num_combo[i]
        if r <= S:
            return 4 + i

def train():
    deck = [14] * 39
    for i in range(4, 14):
        deck.append(i)
    num_combo = [1, 4, 10, 20, 35, 56, 84, 120, 165, 220]
    i_map = {}
    exp = 0.0
    exp_hand = collections.Counter()
    N = 100000
    start_time = time.time()
    for i in range(N):
        oop_badugi = sample_badugi(num_combo)
        random.shuffle(deck)
        game = BadugiGame(deck[0:3], oop_badugi)
#        state = str(oop_badugi) + "|" + str(deck[0]) + "|" + str(deck[1])
        state = str(oop_badugi)
        result = cfr.cfr(game, i_map, "", 1.0 , 1.0, i % 2)
        exp += result
        exp_hand[state] += result
        if (i + 1) % 1000 == 0:
            cur_time = time.time()
            print(i, (exp / (i + 1)) , (cur_time - start_time))
            print(exp_hand)
    out = open("badugi_sol_round2_call_pl2.txt", "w")
    for _, v in sorted(i_map.items(), key= lambda  x : (len(x[1].key) , x[1].key)):
        out.write(str(v)+"\n")
    out.close()

train()