""" Module containing the world logic for the game. """

from typing import List, Tuple, Iterable
import pickle
# import copy
import src.fighter
from src.world_map import WorldMap, Position


class Model:
    """ Class encapsulating the state of the game world. """
    def __init__(self, initial_map: WorldMap=None, player: 'src.fighter.Player'=None, mobs: 'List[src.fighter.Mob]'=None):
        """ Initializes a model with a given initial map, player and list of current mobs. """
        self.map = initial_map
        self.player = player
        self.mobs = mobs

    def get_fighters(self):
        """ Returns a list of the fighters currently present in the game. """
        print(self.get_snapshot())
        return [self.player] + self.mobs

    def get_snapshot(self):
        return pickle.dumps(self)

    def set_snapshot(self, file):
        instance = pickle.load(file)
        self.map = instance.map
        self.player = instance.player
        self.mobs = instance.mobs

    def get_fighter_at(self, pos: Position):
        for fighter in self.get_fighters():
            if fighter.position == pos:
                return fighter
