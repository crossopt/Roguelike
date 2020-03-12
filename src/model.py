""" Module containing the world logic for the game. """

from src import fighter
from src.world_map import Position
from src.world_map import WorldMap


class Model(object):
    """ Class encapsulating the state of the game world. """
    def __init__(self, wmap: WorldMap, player_start: Position):
        self.map = wmap
        self.player = fighter.Fighter(player_start)

    def set_player_will(self, will):
        self.player.set_intention(will)

    def get_fighters(self):
        return [self.player]
