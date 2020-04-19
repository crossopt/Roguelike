""" Module containing the world logic for the game. """

import src.fighter
from src.world_map import Position
from src.world_map import WorldMap


class Model:
    """ Class encapsulating the state of the game world. """
    def __init__(self, initial_map: WorldMap, player: 'src.fighter.Player', mobs: 'List[src.fighter.Mob]'):
        """ Initializes a model with a given initial map and player's start position. """
        self.map = initial_map
        self.player = player
        self.mobs = mobs

    def get_fighters(self):
        """ Returns a list of the fighters currently present in the game. """
        return [self.player] + self.mobs
