""" Module containing the world logic for the game. """

from src import fighter
from src.world_map import Position
from src.world_map import WorldMap


class Model:
    """ Class encapsulating the state of the game world. """
    def __init__(self, initial_map: WorldMap, player_start: Position):
        """ Initialises model with given initial map and player's start position """
        self.map = initial_map
        self.player = fighter.Fighter(player_start)

    def set_player_intention(self, intention):
        """ Sets player's move intention according to given """
        self.player.set_intention(intention)

    def get_fighters(self):
        """ Gets fighters present in the game """
        return [self.player]
