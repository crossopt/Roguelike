""" Module containing the world logic for the game. """
from abc import ABC, abstractmethod
from typing import List, Optional

import jsons

import src.fighter
from src.strategies import FightingStrategy, strategy_deserializer, strategy_serializer
from src.world_map import WorldMap, Position

jsons.set_serializer(strategy_serializer, FightingStrategy)
jsons.set_deserializer(strategy_deserializer, FightingStrategy)


class DrawableModel(ABC):
    """ Class containing all of the necessary information to draw a model. """
    @abstractmethod
    def get_drawable_fighters(self) -> 'List[src.fighter.DrawableFighter]':
        """ Returns a list of the model's drawable fighters. """

    @abstractmethod
    def get_player(self) -> 'src.fighter.Player':
        """ Returns the model's player. """

    @abstractmethod
    def get_map(self) -> 'src.world_map.WorldMap':
        """ Returns the model's map. """


class FullModel(DrawableModel):
    """ Class encapsulating the state of the game world. """

    def __init__(self, map: WorldMap = None, players: 'List[src.fighter.Player]' = None,
                 mobs: 'List[src.fighter.Mob]' = None):
        """ Initializes a model with a given initial map, players and list of current mobs. """
        self.map = map
        self.players = players
        self.mobs = mobs

    def get_fighters(self):
        """ Returns a list of the fighters currently present in the game. """
        return self.players + self.mobs

    def get_drawable_fighters(self):
        return self.get_fighters()

    def get_map(self):
        return self.map

    def get_player(self):
        assert len(self.players) == 1
        return self.players[0]

    def get_snapshot(self) -> str:
        """ Returns a string with the serialized current model world state. """
        return jsons.dumps(self, strip_privates=True)

    def set_snapshot(self, data):
        """ Deserializes the model world state from a given string to the current model. """
        instance = jsons.loads(data, FullModel, strict=True)
        self.map = instance.map
        self.players = instance.players
        self.mobs = instance.mobs

    def get_fighter_at(self, pos: Position) -> 'Optional[src.fighter.Fighter]':
        """ Returns the fighter in a given position if it exists, None otherwise. """
        for fighter in self.get_fighters():
            if fighter.position == pos:
                return fighter
        return None


class ClientModel(DrawableModel):
    """ The model of the game world as visible to a client of the game. """
    def __init__(self, map: WorldMap = None, player: 'src.fighter.Player' = None,
                 other_fighters: 'List[src.fighter.RemoteFighter]' = None):
        """ Initializes a model with a given initial map, player and list of current mobs. """
        self.map = map
        self.player = player
        self.other_fighters = other_fighters

    def get_fighters(self):
        """ Returns a list of the fighters currently present in the game. """
        return [self.player] + self.other_fighters

    def get_drawable_fighters(self) -> 'List[src.fighter.DrawableFighter]':
        return [self.player] + self.other_fighters

    def get_player(self):
        return self.player

    def get_map(self):
        return self.map