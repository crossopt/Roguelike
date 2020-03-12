""" Module containing the world logic for the game. """

from src.map import Map, Position
# from src.fighter import Fighter
import fighter

from enum import Enum


class Model(object):
    """ Class encapsulating the state of the game world. """
    def __init__(self):
        self.map = Map()
        self.player = fighter.Fighter(Position(0, 0))

    def set_player_will(self, will):
        self.player.set_intention(will)

    def get_fighters(self):
        return [self.player]


class Will(Enum):

    STAY = 0
    MOVE_UP = 1