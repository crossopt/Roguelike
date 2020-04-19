""" Module containing the main controller logic for the game. """

from argparse import ArgumentParser

import tcod
import tcod.event

import random

import src.fighter
import src.strategies
from src.fighting_system import CoolFightingSystem
from src import model
from src import view
from src import world_map
from src.world_map import FileWorldMapSource, RandomV1WorldMapSource


class Controller:
    """ The class responsible for controlling the main game flow. """
    _DEFAULT_MAP_WIDTH = 10
    _DEFAULT_MAP_HEIGHT = 10

    _TILESET_PATH = 'fonts/medium_font.png'
    _TILESET_OPTIONS = tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE
    _TILESET_HORIZONTAL = 16
    _TILESET_VERTICAL = 16

    def __init__(self):
        """ Initializes the game controller so it is ready to start a new game. """
        parser = ArgumentParser(description='A simple console-based rogue-like game.')
        parser.add_argument('map_path', type=str, nargs='?', help='path to map file to load')

        args = parser.parse_args()

        if args.map_path is not None:
            game_map = FileWorldMapSource(args.map_path).get()
        else:
            game_map = RandomV1WorldMapSource(Controller._DEFAULT_MAP_HEIGHT,
                                              Controller._DEFAULT_MAP_WIDTH).get()

        mobs_count = 3
        positions = game_map.get_random_empty_positions(mobs_count + 1)
        player = src.fighter.Player(positions[0])
        mobs = [src.fighter.Mob(positions[i], src.strategies.AggressiveStrategy()) for i in range(1, mobs_count + 1)]

        self.model = model.Model(game_map, player, mobs)
        self.program_is_running = True
        self.view = None
        self.fighting_system = CoolFightingSystem()

    def run_loop(self):
        """ Starts a new game and runs it until the user quits the game. """
        tcod.console_set_custom_font(
            Controller._TILESET_PATH,
            Controller._TILESET_OPTIONS,
            Controller._TILESET_HORIZONTAL,
            Controller._TILESET_VERTICAL,
        )

        with tcod.console_init_root(self.model.map.width,
                                    self.model.map.height,
                                    vsync=True, order='C') as root_console:
            self.view = view.View(root_console)

            while self.program_is_running:
                self.view.draw(self.model)
                tcod.console_flush()

                commands = self.model.player.get_commands()

                for event in tcod.event.wait():
                    if event.type == 'QUIT':
                        self.program_is_running = False
                        break

                    if event.type == 'KEYDOWN':
                        if event.repeat:
                            continue
                        self.dispatch(event.scancode, event.mod, commands)

                while self.model.player.has_intention():
                    self.tick()

    def tick(self):
        game_map = self.model.map
        fighters = self.model.get_fighters()

        random.shuffle(fighters)

        for fighter in fighters:
            intended_position = fighter.choose_move(self.model)
            if not game_map.is_empty(intended_position):
                intended_position = fighter.position
            target = self.model.get_fighter_at(intended_position)
            if target is not None and intended_position != fighter.position:
                self.fighting_system.fight(fighter, target)
            if target is None:
                fighter.position = intended_position

        if self.model.player.hp == 0:
            pass # TODO game over
        mobs = []
        for mob in self.model.mobs:
            if mob.hp > 0:
                mobs.append(mob)
        self.model.mobs = mobs

    @staticmethod
    def dispatch(code, _mod, commands):
        """ Handles the user's key down presses and sets the relevant intentions for a player.

        :param code: a scancode of the main key pressed.
        :param _mod: a modifier, a mask of the functional keys pressed with the main one.
        """
        code_to_cmd = {tcod.event.SCANCODE_W: commands['go_up'],
                       tcod.event.SCANCODE_A: commands['go_left'],
                       tcod.event.SCANCODE_S: commands['go_down'],
                       tcod.event.SCANCODE_D: commands['go_right']}
        if code in code_to_cmd:
            code_to_cmd[code]()
