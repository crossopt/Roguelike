""" Module containing strategies for various types of mobs. """

import src.model

from abc import abstractmethod
from random import choice


def sign(x):
    """ Returns the sign of an integer: 0 for 0, -1 for negative integers and 1 for positive ones.  """
    return x and (1, -1)[x < 0]


def strategy_serializer(obj, **_kwargs):
    """ Serializer for the various strategy types. """
    if isinstance(obj, AggressiveStrategy):
        return {'type': 'aggressive'}
    if isinstance(obj, CowardlyStrategy):
        return {'type': 'cowardly'}
    if isinstance(obj, PassiveStrategy):
        return {'type': 'passive'}
    if isinstance(obj, ConfusedStrategy):
        return {'type': 'confused',
                'original': strategy_serializer(obj.original_strategy),
                'confusion_time': obj.confusion_time}
    return None


def strategy_deserializer(obj, cls: type, **_kwargs):
    """ Deserializer for the various strategy types. """
    if obj['type'] == 'aggressive':
        return AggressiveStrategy()
    if obj['type'] == 'cowardly':
        return CowardlyStrategy()
    if obj['type'] == 'passive':
        return PassiveStrategy()
    if obj['type'] == 'confused':
        return ConfusedStrategy(strategy_deserializer(obj['original'], cls=FightingStrategy), obj['confusion_time'])
    return None


class FightingStrategy:
    """ The base class for all fighting strategies for mobs. """
    @staticmethod
    @abstractmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        """ Selects a move for a given mob based on the state of the model world. """
        raise NotImplementedError()

    def update_strategy(self):
        """
        Is called once per move choice.
        Returns a strategy that is updated with the new time and move choice.
        """
        return self


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
    def __init__(self, original_strategy: FightingStrategy, confusion_time: int):
        """ Creates a strategy that moves randomly confusion_time ticks. """
        self.original_strategy = original_strategy
        self.confusion_time = confusion_time

    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        neighbours = current_model.map.get_empty_neighbors(mob.position)
        return choice(neighbours)

    def update_strategy(self):
        self.confusion_time -= 1
        return self if self.confusion_time else self.original_strategy
