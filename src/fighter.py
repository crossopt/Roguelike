""" Module containing the implementation of various in-game fighters. """


class Fighter(object):
    """ Class for storing the various in-game fighter characters. """
    def __init__(self, initial_position):
        """ Initializes a fighter with the given initial position. """
        self.position = initial_position

    def move(self, new_position):
        """ Changes the fighter's position. """
        self.position = new_position

    def choose_move(self, world_map):
        """ Initializes a fighter with the given initial position. """
        pass
