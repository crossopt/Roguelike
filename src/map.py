""" Module containing the implementation of the map generation and storage. """

from enum import Enum


class Position(object):
    """ Class for storing the position of various objects on the map. """
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MapLoadingException(Exception):
    """ Exception raised if errors in loading the map occur. """


class MapTile(Enum):
    """ The contents of a given tile on the map. """
    EMPTY = 0
    BLOCKED = 1
    PLAYER = 2


class Map(object):
    """ Class for storing the world map. """
    def __init__(self):
        """ Generates a map example of size 5x5. """
        self.height = 5
        self.width = 5
        self.tiles = [[MapTile.EMPTY for i in range(self.width)] for j in range(self.height)]

    def generate(self, height, width):
        """ Randomly generates a map of size height x width. """
        pass

    def load(self, file):
        """ Loads a map from the given file.

        :raise: MapLoadingException if the file's contents could not be parsed into a valid map.
        """
        pass
