""" Module containing the implementation of various in-game fighters. """

from enum import Enum

from src import world_map
from src.world_map import Position, WorldMap


class FighterIntention(Enum):
    """ Enum encapsulating the preferred action for a fighter. """
    STAY = 0
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4


class Fighter:
    """ Class for storing the various in-game fighter characters. """

    def __init__(self, initial_position: Position):
        """ Initializes a fighter with the given initial position. """
        self.position = initial_position
        self.intentions = []

    def move(self, new_position: Position):
        """ Changes the fighter's position. """
        self.position = new_position

    def add_intention(self, new_intention: FighterIntention):
        """ Sets the fighter's move intention to a new one. """
        self.intentions.append(new_intention)

    def choose_move(self, _current_map: WorldMap):
        """ Selects a move based on the state of the game map. """
        move = {FighterIntention.STAY: (0, 0),
                FighterIntention.MOVE_UP: (-1, 0),
                FighterIntention.MOVE_LEFT: (0, -1),
                FighterIntention.MOVE_DOWN: (1, 0),
                FighterIntention.MOVE_RIGHT: (0, 1)}

        if len(self.intentions) == 0:
            intention = FighterIntention.STAY
        else:
            intention = self.intentions[0]
            self.intentions = self.intentions[1:]
        dx, dy = move[intention]
        chosen_position = world_map.Position(self.position.x + dx, self.position.y + dy)
        return chosen_position
