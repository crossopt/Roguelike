""" Module containing the implementation of the map generation and storage. """
from abc import ABC, abstractmethod
from enum import Enum
from random import randrange
from itertools import product
from dataclasses import dataclass
from typing import List, Iterable

import random


@dataclass
class Position:
    """ Class for storing the position of various objects on the map. """
    x: int
    y: int


class MapParsingException(Exception):
    """ Exception raised if errors in loading the map occur. """


class MapTile(Enum):
    """ The contents of a given tile on the map. """
    EMPTY = 0
    BLOCKED = 1
    INVALID = 2

    @staticmethod
    def parse(char: str):
        """ Converts a character to the corresponding enum.

        '.' is an empty space on the map, 'X' a blocked space.

        :param char: a single-character string to convert to a MapTile.
        :returns the corresponding MapTile, or MapTile.INVALID if the char is incorrect.
        """
        return {'.': MapTile.EMPTY,
                'X': MapTile.BLOCKED}.get(char, MapTile.INVALID)


class WorldMap:
    """ Class for storing the world map. """
    _DEFAULT_MAP_SIZE = 10

    def __init__(self, height: int = _DEFAULT_MAP_SIZE, width: int = _DEFAULT_MAP_SIZE,
                 tiles: 'List[List[MapTile]]' = None):
        """ Generates a default map example. """
        self.height = height
        self.width = width
        if tiles is None:
            tiles = [[MapTile.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        self.tiles = tiles

    @staticmethod
    def from_tiles(tiles: List[List[MapTile]]):
        """ Builds a world map from the given tiles. """
        height = len(tiles)
        width = len(tiles[0])
        game_map = WorldMap(height, width)
        game_map.tiles = tiles
        return game_map

    def get_random_empty_positions(self, count=1):
        """ Returns a list of random non-repeating empty positions on the map of length count. """
        positions = []
        empty = []
        for i in range(self.height):
            for j in range(self.width):
                if self.tiles[i][j] == MapTile.EMPTY:
                    empty.append(Position(i, j))
        for i in range(count):
            p = random.randrange(0, len(empty))
            positions.append(empty[p])
            empty.pop(p)
        return positions

    def is_empty(self, position: Position):
        """ Checks whether a tile on the map is empty. """
        return self.is_on_map(position) and self.tiles[position.x][position.y] == MapTile.EMPTY

    @staticmethod
    def get_distance(first_position: Position, second_position: Position):
        """ Returns the distance in map metrics between two positions on the map. """
        return abs(first_position.x - second_position.x) + abs(first_position.y - second_position.y)

    def get_empty_neighbors(self, position: Position):
        """ Returns list of positions of empty tiles at manhattan distance 1. """
        empty_neighbors = []
        for dx, dy in {(0, 1), (0, -1), (1, 0), (-1, 0)}:
            neighbor = Position(position.x + dx, position.y + dy)
            if self.is_empty(neighbor):
                empty_neighbors.append(neighbor)
        return empty_neighbors

    def is_on_map(self, position: Position):
        """ Returns True if the given position exists on the map, False otherwise. """
        return 0 <= position.x < self.height and 0 <= position.y < self.width

    def is_one_component(self) -> bool:
        """ Checks whether the map contains one connected component.

        :returns True if all of the empty tiles are reachable from any empty tile
        on the given map, or False otherwise.
        """
        was_visited = list(map(lambda x: list(map(lambda y: y != MapTile.EMPTY, x)), self.tiles))

        def _is_valid_tile(x, y):
            return 0 <= x < len(was_visited) and 0 <= y < len(was_visited[x])

        def _dfs(x, y):
            if _is_valid_tile(x, y) and not was_visited[x][y]:
                was_visited[x][y] = True
                for dx, dy in {(0, 1), (0, -1), (1, 0), (-1, 0)}:
                    _dfs(x + dx, y + dy)

        component_amount = 0
        for x, y in product(range(len(self.tiles)), range(max(map(len, self.tiles)))):
            if not was_visited[x][y]:
                _dfs(x, y)
                component_amount += 1
        return component_amount == 1


class WorldMapSource(ABC):
    """ Base class for map loaders/generators. """

    @abstractmethod
    def get(self) -> WorldMap:
        """ Produces a world map. """


class FileWorldMapSource(WorldMapSource):
    """ Loads a map from the given file.

    The file should contain a height x width board (height rows with width board symbols in each).
    A board symbol is one of '.' for an empty tile, 'X' for a blocked tile.
    The empty tiles should all be reachable from any empty tile on the board.

    If the map loading fails and an exception is thrown the old map is left unmodified.
    """

    def __init__(self, file_name: str):
        self.file_name = file_name

    def get(self) -> WorldMap:
        """
        :raises MapParsingException if the file's contents could not be parsed into a valid map.
        """
        try:
            with open(self.file_name, 'r') as fin:
                lines = FileWorldMapSource._trim_lines(fin.readlines())
                game_map = WorldMap.from_tiles(FileWorldMapSource._convert_to_tiles(lines))
                if not game_map.is_one_component():
                    raise MapParsingException('Map is not a connected component')
        except IOError as exception:
            raise MapParsingException(exception)
        return game_map

    @staticmethod
    def _trim_lines(lines: Iterable[str]):
        """ Removes excess empty symbols from lines before their conversion to a map. """
        return list(filter(lambda x: x != '', map(lambda x: x.strip(), lines)))

    @staticmethod
    def _convert_to_tiles(string_list: List[str]) -> List[List[MapTile]]:
        """ Converts a list of strings containing a board to a MapTile 2d array.

        Fails if the string list is empty, if the board widths are inconsistent,
        if the strings contain invalid symbols or if the resulting map is not a
        single connected component.
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
        return converted_tiles


class RandomV1WorldMapSource(WorldMapSource):
    """ Randomly generates a map of size height x width. """
    _WALL_PERCENTAGE = 0.4

    def __init__(self, height: int, width: int) -> None:
        """ :raises ValueError if height or width are incorrect. """
        if height <= 0:
            raise ValueError('Invalid map height')
        if width <= 0:
            raise ValueError('Invalid map width')
        self.height = height
        self.width = width

    def get(self) -> WorldMap:
        game_map = WorldMap(self.height, self.width)

        for _ in range(int(self.height * self.width * RandomV1WorldMapSource._WALL_PERCENTAGE)):
            block_x = randrange(self.height)
            block_y = randrange(self.width)
            game_map.tiles[block_x][block_y] = MapTile.BLOCKED
            if not game_map.is_one_component():
                game_map.tiles[block_x][block_y] = MapTile.EMPTY

        return game_map
