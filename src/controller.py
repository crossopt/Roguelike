""" Module containing the main controller logic for the game. """

import os
import random
from argparse import ArgumentParser

import tcod
import tcod.event

import src.fighter
import src.strategies
from src import model
from src import view
from src.fighting_system import CoolFightingSystem
from src.view import TOTAL_WIDTH, TOTAL_HEIGHT
from src.weapon import WeaponBuilder
from src.world_map import FileWorldMapSource, RandomV1WorldMapSource

SAVE_FILE_NAME = 'save'


class Controller:
    """ The class responsible for controlling the main game flow. """
    _DEFAULT_MAP_WIDTH = 30
    _DEFAULT_MAP_HEIGHT = 30
    _MOB_COUNT = 8

    _TILESET_PATH = 'fonts/medium_font.png'
    _TILESET_OPTIONS = tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE
    _TILESET_HORIZONTAL = 16
    _TILESET_VERTICAL = 16

    def __init__(self, _test_args=None):
        """ Initializes the game controller so it is ready to start a new game. """

        parser = ArgumentParser(description='A simple console-based rogue-like game.')
        parser.add_argument('map_path', type=str, nargs='?', help='path to map file to load')
        parser.add_argument('--new_game', nargs='?', dest='new_game_demanded', const=True,
                            default=False)

        args = parser.parse_args(_test_args)

        no_save_file = not os.path.isfile(SAVE_FILE_NAME)

        if args.new_game_demanded or no_save_file:
            if args.map_path is not None:
                game_map = FileWorldMapSource(args.map_path).get()
            else:
                game_map = RandomV1WorldMapSource(Controller._DEFAULT_MAP_HEIGHT,
                                                  Controller._DEFAULT_MAP_WIDTH).get()

            mobs_count = Controller._MOB_COUNT
            positions = game_map.get_random_empty_positions(mobs_count + 1)
            player = src.fighter.Player(positions[0], [
                WeaponBuilder()
                .with_name('SABER')
                .with_attack(2)
                .with_defence(2)
                .with_confusion_prob(0.2),
                WeaponBuilder()
                .with_name('SPEAR')
                .with_attack(4)
                .with_defence(1)
                .with_confusion_prob(0.1),
                WeaponBuilder()
                .with_name('SWORD')
                .with_attack(1)
                .with_defence(3)
                .with_confusion_prob(0.7)])
            mobs = [src.fighter.Mob(positions[i], random.choice([
                src.strategies.AggressiveStrategy(),
                src.strategies.PassiveStrategy(),
                src.strategies.CowardlyStrategy()])) for i in range(1, mobs_count + 1)]

            self.model = model.Model(game_map, player, mobs)
        else:
            self._read_saved_game()

        self.program_is_running = True
        self.view = None
        self.player_died = False
        self.fighting_system = CoolFightingSystem()

    def run_loop(self):
        """ Starts a new game and runs it until the user quits the game. """
        tcod.console_set_custom_font(
            Controller._TILESET_PATH,
            Controller._TILESET_OPTIONS,
            Controller._TILESET_HORIZONTAL,
            Controller._TILESET_VERTICAL,
        )

        with tcod.console_init_root(TOTAL_WIDTH,
                                    TOTAL_HEIGHT,
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
                        self._dispatch(event.scancode, event.mod, commands)

                if not self.program_is_running:
                    break

                while self.model.player.has_intention():
                    self._tick()

            if self.player_died:
                self._remove_saved_game()
                self.view.draw_death_screen()
                tcod.console_flush()
                self._wait_for_any_key()
            else:
                self._save_game()

    def _save_game(self):
        if self.player_died:
            return
        with open(SAVE_FILE_NAME, 'w') as file:
            file.write(self.model.get_snapshot())

    @staticmethod
    def _remove_saved_game():
        if os.path.isfile(SAVE_FILE_NAME):
            os.remove(SAVE_FILE_NAME)

    def _read_saved_game(self):
        with open(SAVE_FILE_NAME, 'r') as file:
            self.model = model.Model(None, None, None)
            self.model.set_snapshot(file.read())

    @staticmethod
    def _wait_for_any_key():
        for _ in tcod.event.wait():
            pass
        while True:
            for event in tcod.event.wait():
                if event.type in ['QUIT', 'KEYDOWN']:
                    return

    def _tick(self):
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

        if self.model.player.hp <= 0:
            self.program_is_running = False
            self.player_died = True
        mobs = []
        for mob in self.model.mobs:
            if mob.hp > 0:
                mobs.append(mob)
        self.model.mobs = mobs

    @staticmethod
    def _dispatch(code, _mod, commands):
        """ Handles the user's key down presses and sets the relevant intentions for a player.

        :param code: a scancode of the main key pressed.
        :param _mod: a modifier, a mask of the functional keys pressed with the main one.
        :param commands: a list of commands to which the key presses match.
        """
        code_to_cmd = {tcod.event.SCANCODE_W: commands['go_up'],
                       tcod.event.SCANCODE_A: commands['go_left'],
                       tcod.event.SCANCODE_S: commands['go_down'],
                       tcod.event.SCANCODE_D: commands['go_right'],
                       tcod.event.SCANCODE_1: commands['select_1'],
                       tcod.event.SCANCODE_2: commands['select_2'],
                       tcod.event.SCANCODE_3: commands['select_3']}
        if code in code_to_cmd:
            code_to_cmd[code]()
