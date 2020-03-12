""" Module containing the implementation of the graphic output for the game. """

from .model import Model
from .fighter import Fighter
from .map import Map


class View:
    def __init__(self):
        pass

    def draw(self, model: Model):
        pass