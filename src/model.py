""" Module containing the world logic for the game. """

from typing import List

import jsons

import src.fighter
from src.strategies import FightingStrategy, strategy_deserializer, strategy_serializer
from src.world_map import WorldMap, Position

jsons.set_serializer(strategy_serializer, FightingStrategy)
jsons.set_deserializer(strategy_deserializer, FightingStrategy)


class Model:
    """ Class encapsulating the state of the game world. """

    def __init__(self, map: WorldMap = None, player: 'src.fighter.Player' = None,
                 mobs: 'List[src.fighter.Mob]' = None):
        """ Initializes a model with a given initial map, player and list of current mobs. """
        self.map = map
        self.player = player
        self.mobs = mobs

    def get_fighters(self):
        """ Returns a list of the fighters currently present in the game. """
        return [self.player] + self.mobs

    def get_snapshot(self):
        """ Returns a string with the serialized current model world state. """
        return jsons.dumps(self, strip_privates=True)

    def set_snapshot(self, data):
        """ Deserializes the model world state from a given string to the current model. """
        instance = jsons.loads(data, Model, strict=True)
        self.map = instance.map
        self.player = instance.player
        self.mobs = instance.mobs

    def get_fighter_at(self, pos: Position):
        """ Returns the fighter in a given position if it exists, None otherwise. """
        for fighter in self.get_fighters():
            if fighter.position == pos:
                return fighter
