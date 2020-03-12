""" Module containing the main controller logic for the game. """

import sys
sys.path.append(".")

from src.model import Model
from src.view import View

import tcod
import tcod.event

class Controller(object):

    def __init__(self):
        self.model = Model()
        self.isAppRunning = True

    def run_loop(self):
        with tcod.console_init_root(80, 60, order='F') as root_console:
            self.view = View(root_console)
            for event in tcod.event.wait():
                print(event.type)



if __name__ == "__main__":
    Controller().run_loop()


