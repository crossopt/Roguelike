""" Module containing the implementation of the map generation and storage. """

from enum import Enum
from random import randrange


class Position(object):
    """ Class for storing the position of various objects on the map. """
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MapParsingException(Exception):
    """ Exception raised if errors in loading the map occur. """


class MapTile(Enum):
    """ The contents of a given tile on the map. """
    EMPTY = 0
    BLOCKED = 1
    INVALID = 2

    @staticmethod
    def parse(char):
        """ Converts a character to the corresponding enum.

        '.' is an empty space on the map, 'X' a blocked space.

        :param char: a single-character string to convert to a MapTile.
        :return: the corresponding MapTile, or MapTile.INVALID if the char is incorrect.
        """
        return {'.': MapTile.EMPTY,
                'X': MapTile.BLOCKED}.get(char, MapTile.INVALID)


class WorldMap(object):
    """ Class for storing the world map. """
    _WALL_PERCENTAGE = 0.4

    def __init__(self):
        """ Generates a map example of size 5x5. """
        self.height = 5
        self.width = 5
        self.tiles = [[MapTile.EMPTY for i in range(self.width)] for j in range(self.height)]

    def generate(self, height, width):
        """ Randomly generates a map of size height x width. """
        self.height = height
        self.width = width
        self.tiles = [[MapTile.EMPTY for i in range(self.width)] for j in range(self.height)]

        for block in range(height * width * WorldMap._WALL_PERCENTAGE):
            block_x = randrange(height)
            block_y = randrange(width)
            self.tiles[block_x][block_y] = MapTile.BLOCKED
            if not WorldMap._is_one_component(self.tiles):
                self.tiles[block_x][block_y] = MapTile.EMPTY

    def load(self, file_name):
        """ Loads a map from the given file.

        The file should contain a height x width board (height rows with width board symbols in each).
        A board symbol is one of '.' for an empty tile, 'X' for a blocked tile.
        The empty tiles should all be reachable from any empty tile on the board.

        If the map loading fails and an exception is thrown the old map is left unmodified.

        :raise: MapParsingException if the file's contents could not be parsed into a valid map.
        """
        try:
            with open(file_name, 'r') as fin:
                lines = WorldMap._trim_lines(fin.readlines())
                converted_tiles = WorldMap._convert_to_tiles(lines)
                self.height = len(lines)
                self.width = len(lines[0])
                self.tiles = converted_tiles
        except IOError as exception:
            raise MapParsingException(exception)

    @staticmethod
    def _trim_lines(lines):
        """ Removes excess empty symbols from lines before their conversion to a map. """
        return list(filter(lambda x: x != "", map(lambda x: x.strip(), lines)))

    @staticmethod
    def _convert_to_tiles(string_list):
        """ Converts a list of strings containing a board to a MapTile 2d array.

        Fails if the string list is empty, if the board widths are inconsistent,
        if the strings contain invalid symbols or if the resulting map is not a
        single connected component.

        :raise: MapParsingException if the string list encodes an invalid board.
        """
        if len(string_list) <= 0:
            raise MapParsingException('Invalid map height')
        width = len(string_list[0])
        converted_tiles = []
        for string in string_list:
            converted_string = []
            if len(string) != width:
                raise MapParsingException('Line does not match width: {}'.format(string))
            for symbol in string:
                converted_symbol = MapTile.parse(symbol)
                if converted_symbol == MapTile.INVALID:
                    raise MapParsingException('Invalid symbol {} in line {}'.format(symbol, string))
                converted_string.append(converted_symbol)
            converted_tiles.append(converted_string)
        if not WorldMap._is_one_component(converted_tiles):
            raise MapParsingException('WorldMap is not a connected component')
        return converted_tiles

    @staticmethod
    def _is_one_component(world_map):
        """ Checks whether the passed map contains one connected component.

        Returns True if all of the empty tiles are reachable from any empty tile
        on the given map, or False otherwise.
        """
        pass
