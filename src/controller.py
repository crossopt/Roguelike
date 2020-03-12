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
        with tcod.console_init_root(80, 60, vsync=True, order='F') as root_console:
            self.view = View(root_console)
            
            while self.isAppRunning:
                tcod.console_flush()

                for event in tcod.event.wait():
                    print(event.type)

                    if event.type == "QUIT":
                        self.isAppRunning = False
                        break



if __name__ == "__main__":
    Controller().run_loop()


