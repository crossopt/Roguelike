""" Module containing the implementation of various in-game fighters. """

from enum import Enum

from src import world_map


class FighterIntention(Enum):
    """ Enum encapsulating the preferred action for a fighter. """
    STAY = 0
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4


class Fighter:
    """ Class for storing the various in-game fighter characters. """

    def __init__(self, initial_position):
        """ Initializes a fighter with the given initial position. """
        self.position = initial_position
        self.intention = FighterIntention.STAY

    def move(self, new_position):
        """ Changes the fighter's position. """
        self.position = new_position

    def set_intention(self, new_intention):
        """ Sets the fighter's move intention to a new one. """
        self.intention = new_intention

    def choose_move(self, _current_map):
        """ Selects a move based on the state of the game map. """
        move = {FighterIntention.STAY: (0, 0),
                FighterIntention.MOVE_UP: (-1, 0),
                FighterIntention.MOVE_LEFT: (0, -1),
                FighterIntention.MOVE_DOWN: (1, 0),
                FighterIntention.MOVE_RIGHT: (0, 1)}
        if self.intention not in move:
            raise ValueError('FighterIntention is incorrect')
        dx, dy = move[self.intention]
        chosen_position = world_map.Position(self.position.x + dx, self.position.y + dy)
        return chosen_position
