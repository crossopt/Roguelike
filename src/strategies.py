""" Module containing strategies for various types of mobs. """

import src.model

from abc import abstractmethod


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
        player = current_model.player
        dx = -player.position.x + mob.position.x
        dy = -player.position.y + mob.position.y
        dx = sign(-dx)
        dy = sign(-dy)
        return dx, dy


class CowardlyStrategy(FightingStrategy):
    """ A cowardly strategy that always moves away from the player. """
    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        player = current_model.player
        dx = -player.position.x + mob.position.x
        dy = -player.position.y + mob.position.y
        dx = (dx > 0) * 2 - 1
        dy = (dy > 0) * 2 - 1
        return dx, dy


class PassiveStrategy(FightingStrategy):
    """ A passive strategy that does not move. """
    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        return 0, 0
