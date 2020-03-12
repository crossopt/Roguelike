""" Module containing the main controller logic for the game. """

import tcod
import tcod.event

import src.fighter
from src import model
from src import view
from src import world_map


class Controller:
    def __init__(self):
        wmap = world_map.WorldMap()
        wmap.generate(10, 10)
        self.model = model.Model(wmap, wmap.get_player_start())
        self.program_is_running = True
        self.view = None

    def run_loop(self):
        tcod.console_set_custom_font(
            "big_font.png",
            tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE,
            16,
            16,
        )

        with tcod.console_init_root(10, 10, vsync=True, order='C') as root_console:
            self.view = view.View(root_console)

            while self.program_is_running:
                self.view.draw(self.model)
                tcod.console_flush()

                self.model.set_player_will(src.fighter.FighterIntention.STAY)

                for event in tcod.event.wait():
                    print(event.type)

                    if event.type == "QUIT":
                        self.program_is_running = False
                        break

                    if event.type == "KEYDOWN":
                        if event.repeat:
                            continue

                        print(event.scancode, event.mod)
                        self.dispatch(event.scancode, event.mod)

                wmap = self.model.map
                tiles = wmap.tiles
                fighters = self.model.get_fighters()

                for fighter in fighters:
                    print(fighter, fighter.position.x, fighter.position.y)
                    intentable_position = fighter.choose_move(world_map)
                    if wmap.is_on_map(intentable_position) and \
                        tiles[intentable_position.x][intentable_position.y] == world_map.MapTile.EMPTY: # ideally ask map

                        fighter.move(intentable_position)

    def dispatch(self, code, _mod):
        if code == tcod.event.SCANCODE_W:
            self.model.set_player_will(src.fighter.FighterIntention.MOVE_UP)
        elif code == tcod.event.SCANCODE_A:
            self.model.set_player_will(src.fighter.FighterIntention.MOVE_LEFT)
        elif code == tcod.event.SCANCODE_S:
            self.model.set_player_will(src.fighter.FighterIntention.MOVE_DOWN)
        elif code == tcod.event.SCANCODE_D:
            self.model.set_player_will(src.fighter.FighterIntention.MOVE_RIGHT)
