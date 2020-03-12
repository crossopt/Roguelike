""" Module containing the implementation of various in-game fighters. """

import model
import world_map

class Fighter(object):
    """ Class for storing the various in-game fighter characters. """
    def __init__(self, initial_position):
        """ Initializes a fighter with the given initial position. """
        self.position = initial_position
        self.intention = model.Will.STAY

    def move(self, new_position):
        """ Changes the fighter's position. """
        self.position = new_position

    def set_intention(self, will):
        self.intention = will


    def choose_move(self, current_map):

        if self.intention == model.Will.STAY:
            dx, dy = 0, 0
        elif self.intention == model.Will.MOVE_UP:
            dx, dy = -1, 0
        else:
            print(type(self.intention))
            print(type(model.Will.MOVE_UP))
            print(self.intention.__eq__(model.Will.MOVE_UP))
            raise ValueError("?")

        intentable_position = world_map.Position(self.position.x + dx, self.position.y + dy)
        return intentable_position
