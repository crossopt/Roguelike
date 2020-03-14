""" Module containing the world logic for the game. """

from src import fighter
from src.fighter import FighterIntention
from src.world_map import Position
from src.world_map import WorldMap


class Model:
    """ Class encapsulating the state of the game world. """
    def __init__(self, initial_map: WorldMap, player_start: Position):
        """ Initializes a model with a given initial map and player's start position. """
        self.map = initial_map
        self.player = fighter.Fighter(player_start)

    def add_player_intention(self, intention: FighterIntention):
        """ Sets the player's intended move to the given one. """
        self.player.add_intention(intention)

    def get_fighters(self):
        """ Returns a list of the fighters currently present in the game. """
        return [self.player]
