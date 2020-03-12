""" Module containing the main controller logic for the game. """

import sys

from src import model
from src import world_map as package_map
from src import view
# from src.model import Model, Will
# from src.view import View

import tcod
import tcod.event

class Controller(object):

    def __init__(self):
        self.model = model.Model()
        self.isAppRunning = True
        self.view = None

    def run_loop(self):
        tcod.console_set_custom_font(
            "big_font.png",
            tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE,
            16,
            16,
        )

        self.model.map.generate(10, 10)
        with tcod.console_init_root(10, 10, vsync=True, order='C') as root_console:
            self.view = view.View(root_console)
            
            while self.isAppRunning:
                self.view.draw(self.model)
                tcod.console_flush()

                self.model.set_player_will(model.Will.STAY)

                for event in tcod.event.wait():
                    print(event.type)

                    if event.type == "QUIT":
                        self.isAppRunning = False
                        break

                    if event.type == "KEYDOWN":
                        if event.repeat:
                            continue

                        print(event.scancode, event.mod)
                        self.dispatch(event.scancode, event.mod)

                world_map = self.model.map
                tiles = world_map.tiles
                fighters = self.model.get_fighters()

                for fighter in fighters:
                    print(fighter, fighter.position.x, fighter.position.y)
                    intentable_position = fighter.choose_move(world_map)
                    if world_map.is_on_map(intentable_position) and \
                        tiles[intentable_position.x][intentable_position.y] == package_map.MapTile.EMPTY: # ideally ask map
                        
                        fighter.move(intentable_position)

    def dispatch(self, code, mod):
        if code == tcod.event.SCANCODE_W:
            self.model.set_player_will(model.Will.MOVE_UP)
        elif code == tcod.event.SCANCODE_A:
            self.model.set_player_will(model.Will.MOVE_LEFT)
        elif code == tcod.event.SCANCODE_S:
            self.model.set_player_will(model.Will.MOVE_DOWN)
        elif code == tcod.event.SCANCODE_D:
            self.model.set_player_will(model.Will.MOVE_RIGHT)            



if __name__ == "__main__":
    Controller().run_loop()


