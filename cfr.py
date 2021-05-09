from abc import ABCMeta, abstractmethod
from typing import Dict, List
import numpy as np

# sample from https://justinsermeno.com/posts/cfr/

class InformationSet():
    def __init__(self, key, num_actions : int, action_types: List[str]):
        self.key = key
        self.num_actions = num_actions
        self.action_types = action_types
        self.regret_sum = np.zeros(num_actions)
        self.strategy_sum = np.zeros(num_actions)
        self.strategy = np.repeat(1/num_actions, num_actions)
        self.reach_pr_sum = 0

    def next_strategy(self, reach_pr: float):
        self.strategy_sum += reach_pr * self.strategy
        self.strategy = self.calc_strategy()
        self.reach_pr_sum += reach_pr

    def calc_strategy(self):
        """
        Calculate current strategy from the sum of regret.
        """
        strategy = self.make_positive(self.regret_sum)
        total = sum(strategy)
        if total > 0:
            strategy = strategy / total
        else:
            n = self.num_actions
            strategy = np.repeat(1/n, n)

        return strategy

    def get_average_strategy(self):
        """
        Calculate average strategy over all iterations. This is the
        Nash equilibrium strategy.
        """
        #print(self.regret_sum)
        strategy = self.strategy_sum / self.reach_pr_sum
        # Purify to remove actions that are likely a mistake
        strategy = np.where(strategy < 0.001, 0, strategy)

        # Re-normalize
        total = sum(strategy)
        strategy /= total

        return strategy

    def make_positive(self, x):
        return np.where(x > 0, x, 0)

    def __str__(self):
        strategies = ['{:03.2f}'.format(x)
                      for x in self.get_average_strategy()]
        return '{} {}'.format(str(self.key), strategies)


class AbstractGame(metaclass=ABCMeta):
    @abstractmethod
    def active_player(self, history: str) -> int:
        return 0
    @abstractmethod
    def next_player(self, history: str, action : str) -> int:
        return 0
    @abstractmethod
    def payoff(self, history: str) -> float:
        return 0
    @abstractmethod
    def is_terminal(self, history) -> bool:
        return True
    @abstractmethod
    def is_chance(self, history) -> bool:
        return True
    @abstractmethod
    def get_info_set(self, i_map : Dict[str,InformationSet], history) -> InformationSet:
        return None
    @abstractmethod
    def get_chance_reslut(self, hisotry: str) -> str:
        return None


def cfr(game: AbstractGame, i_map : Dict[str,InformationSet], history : str,
        p0 : float, p1:float, relearn_player: int) -> float:
    if game.is_terminal(history):
        return game.payoff(history)
    if game.is_chance(history):
        next_history = game.get_chance_reslut(history)
        return cfr(game, i_map, next_history, p0, p1, relearn_player)
    info_set = game.get_info_set(i_map, history)
    strategy = info_set.strategy
    action_utils = np.zeros(info_set.num_actions)
    action_types = info_set.action_types
    active_player = game.active_player(history)
    for select in range(info_set.num_actions):
        next_history = history + action_types[select]
        next_player = game.next_player(history, action_types[select])
        mul = 1 if active_player == next_player else -1
        if active_player == 0:
            action_utils[select] = mul * cfr(game, i_map, next_history, p0 * strategy[select], p1, relearn_player)
        else:
            action_utils[select] = mul * cfr(game, i_map, next_history, p0, p1 * strategy[select], relearn_player)
    util = sum(action_utils * strategy)
    regrets = action_utils - util
    if relearn_player == active_player:
        if active_player == 0:
            info_set.regret_sum += p1 * regrets
            info_set.next_strategy(p0)
        else:
            info_set.regret_sum += p0 * regrets
            info_set.next_strategy(p1)
    return util
