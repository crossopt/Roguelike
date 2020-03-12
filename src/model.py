""" Module containing the world logic for the game. """

from src.map import Map, Position
from src.fighter import Fighter


class Model(object):
    """ Class encapsulating the state of the game world. """
    def __init__(self):
        self.map = Map()
        self.player = Fighter(Position(0, 0))
