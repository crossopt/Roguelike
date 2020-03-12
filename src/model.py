""" Module containing the world logic for the game. """

# from src.map import Map, Position
# from src.fighter import Fighter
from src import fighter
from src import world_map
from src.world_map import WorldMap
from src.world_map import Position

from enum import Enum


class Model(object):
    """ Class encapsulating the state of the game world. """
    def __init__(self, wmap: WorldMap, player_start: Position):
        self.map = wmap
        self.player = fighter.Fighter(self.map.get_player_start())

    def set_player_will(self, will):
        self.player.set_intention(will)

    def get_fighters(self):
        return [self.player]


class Will(Enum):

    STAY = 0
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4
