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

        dx = [0, 1, 0, -1, 0]
        dy = [1, 0, -1, 0, 0]

        minimal_distance = abs(mob.position.x - player.position.x) + abs(mob.position.y - player.position.y)
        target_dir = 4

        for direction in range(4):
            nx = mob.position.x + dx[direction]
            ny = mob.position.y + dy[direction]

            if not current_model.map.is_empty(src.world_map.Position(nx, ny)):
                continue
            
            distance = abs(nx - player.position.x) + abs(ny - player.position.y)
            if distance < minimal_distance:
                minimal_distance = distance
                target_dir = direction

        return dx[target_dir], dy[target_dir]


class CowardlyStrategy(FightingStrategy):
    """ A cowardly strategy that always moves away from the player. """
    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        player = current_model.player

        dx = [0, 1, 0, -1, 0]
        dy = [1, 0, -1, 0, 0]

        maximal_distance = abs(mob.position.x - player.position.x) + abs(mob.position.y - player.position.y)
        target_dir = 4

        for direction in range(4):
            nx = mob.position.x + dx[direction]
            ny = mob.position.y + dy[direction]

            if not current_model.map.is_empty(src.world_map.Position(nx, ny)):
                continue
            
            distance = abs(nx - player.position.x) + abs(ny - player.position.y)
            if distance > maximal_distance:
                maximal_distance = distance
                target_dir = direction

        return dx[target_dir], dy[target_dir]


class PassiveStrategy(FightingStrategy):
    """ A passive strategy that does not move. """
    @staticmethod
    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        return 0, 0
