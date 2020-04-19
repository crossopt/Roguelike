""" Module containing strategies for various types of mobs. """

import src.model

from abc import abstractmethod
from random import choice


def sign(x):
    """ Returns the sign of an integer: 0 for 0, -1 for negative integers and 1 for positive ones.  """
    return x and (1, -1)[x < 0]


class FightingStrategy:
    """ The base class for all fighting strategies for mobs. """
    @staticmethod
    @abstractmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        """ Selects a move for a given mob based on the state of the model world. """
        raise NotImplementedError()


class AggressiveStrategy(FightingStrategy):
    """ An aggressive strategy that always moves towards the player and attacks them. """
    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        player_position = current_model.player.position
        best_position = mob.position

        for new_position in current_model.map.get_empty_neighbors(mob.position):
            new_distance = current_model.map.get_distance(new_position, player_position)
            if new_distance < current_model.map.get_distance(best_position, player_position):
                best_position = new_position

        return best_position


class CowardlyStrategy(FightingStrategy):
    """ A cowardly strategy that always moves away from the player. """
    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        player_position = current_model.player.position
        best_position = mob.position

        for new_position in current_model.map.get_empty_neighbors(mob.position):
            new_distance = current_model.map.get_distance(new_position, player_position)
            if new_distance > current_model.map.get_distance(best_position, player_position):
                best_position = new_position

        return best_position


class PassiveStrategy(FightingStrategy):
    """ A passive strategy that does not move. """
    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        return mob.position


class ConfusedStrategy(FightingStrategy):
    """ Strategy for a mob that has been confused. """
    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        return choice(current_model.map.get_empty_neighbors(mob.position))
