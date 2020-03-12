""" Module containing the implementation of various in-game fighters. """
from enum import Enum

from src import world_map


class Fighter:
    """ Class for storing the various in-game fighter characters. """
    def __init__(self, initial_position):
        """ Initializes a fighter with the given initial position. """
        self.position = initial_position
        self.intention = Will.STAY

    def move(self, new_position):
        """ Changes the fighter's position. """
        self.position = new_position

    def set_intention(self, will):
        self.intention = will

    def choose_move(self, _current_map):
        if self.intention == Will.STAY:
            dx, dy = 0, 0
        elif self.intention == Will.MOVE_UP:
            dx, dy = -1, 0
        elif self.intention == Will.MOVE_LEFT:
            dx, dy = 0, -1
        elif self.intention == Will.MOVE_DOWN:
            dx, dy = 1, 0
        elif self.intention == Will.MOVE_RIGHT:
            dx, dy = 0, 1
        else:
            raise ValueError("Will is incorrect")

        chosen_position = world_map.Position(self.position.x + dx, self.position.y + dy)
        return chosen_position


class Will(Enum):
    STAY = 0
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4
