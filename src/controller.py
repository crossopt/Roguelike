""" Module containing the main controller logic for the game. """

import sys
sys.path.append(".")

from src.model import Model
from src.view import View
import tcod.event

class Controller(object):

    def __init__(self, view):
        self.view = View()
        self.model = Model()
        self.isAppRunning = True

    def run_loop(self):
        for event in tcod.event.wait():
            print(event.type) 



if __name__ == "__main__":
    Controller().run_loop()


