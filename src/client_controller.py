""" Module containing the main controller logic for the game clients. """

import os
import random
from abc import abstractmethod
from argparse import ArgumentParser
import threading

import grpc
import tcod
import tcod.event

import src.roguelike_pb2_grpc
from src import view
from src.fighter import RemoteFighter, Player
from src.model import ClientModel
from src.roguelike_pb2 import Intention
from src.view import TOTAL_WIDTH, TOTAL_HEIGHT
from src.weapon import WeaponBuilder
from src.world_map import WorldMap, MapTile, Position, FileWorldMapSource, RandomV1WorldMapSource

import src.fighter
import src.strategies
from src import model
from src.fighting_system import CoolFightingSystem


SAVE_FILE_NAME = 'save'


class Controller:
    """ Class responsible for controlling the main game flow. """
    DEFAULT_MAP_WIDTH = 30
    DEFAULT_MAP_HEIGHT = 30
    MOB_COUNT = 8

    TILESET_PATH = 'fonts/medium_font.png'
    TILESET_OPTIONS = tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE
    TILESET_HORIZONTAL = 16
    TILESET_VERTICAL = 16

    DEFAULT_WEAPON_SET = [
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
                .with_confusion_prob(0.7)]

    @abstractmethod
    def run_loop(self):
        """ Starts a new game and runs it until the user quits the game. """

    @staticmethod
    def wait_for_any_key():
        """ Waits for a key press event to happen and returns it. """
        for _ in tcod.event.wait():
            pass
        while True:
            for event in tcod.event.wait():
                if event.type in ['QUIT', 'KEYDOWN']:
                    return

    @staticmethod
    def dispatch(code, _mod, commands):
        """ Handles the user's key down presses and sets the relevant intentions for a player.

        :param code: a scancode of the main key pressed.
        :param _mod: a modifier, a mask of the functional keys pressed with the main one.
        :param commands: a list of commands to which the key presses match.
        """
        code_to_cmd = {tcod.event.SCANCODE_SPACE: commands['stay'],
                       tcod.event.SCANCODE_W: commands['go_up'],
                       tcod.event.SCANCODE_A: commands['go_left'],
                       tcod.event.SCANCODE_S: commands['go_down'],
                       tcod.event.SCANCODE_D: commands['go_right'],
                       tcod.event.SCANCODE_0: commands['select_0'],
                       tcod.event.SCANCODE_1: commands['select_1'],
                       tcod.event.SCANCODE_2: commands['select_2'],
                       tcod.event.SCANCODE_3: commands['select_3']}
        if code in code_to_cmd:
            code_to_cmd[code]()


class OfflineController(Controller):
    """ The class responsible for controlling the main game flow for an offline game. """

    def __init__(self, args):
        """ Initializes the game controller so it is ready to start a new game. """
        no_save_file = not os.path.isfile(SAVE_FILE_NAME)

        if args.new_game_demanded or no_save_file:
            if args.map_path is not None:
                game_map = FileWorldMapSource(args.map_path).get()
            else:
                game_map = RandomV1WorldMapSource(Controller.DEFAULT_MAP_HEIGHT,
                                                  Controller.DEFAULT_MAP_WIDTH).get()

            mobs_count = Controller.MOB_COUNT
            positions = game_map.get_random_empty_positions(mobs_count + 1)
            player = src.fighter.Player(positions[0], Controller.DEFAULT_WEAPON_SET)
            mobs = [src.fighter.Mob(positions[i], random.choice([
                                src.strategies.AggressiveStrategy(),
                                src.strategies.PassiveStrategy(),
                                src.strategies.CowardlyStrategy()])) for i in range(1, mobs_count + 1)]

            self.model = model.FullModel(game_map, [player], mobs)
        else:
            with open(SAVE_FILE_NAME, 'r') as file:
                self.model = model.FullModel(None, None, None)
                self.model.set_snapshot(file.read())

        self.program_is_running = True
        self.view = None
        self.player_died = False
        self.fighting_system = CoolFightingSystem()

    def run_loop(self):
        tcod.console_set_custom_font(
            Controller.TILESET_PATH,
            Controller.TILESET_OPTIONS,
            Controller.TILESET_HORIZONTAL,
            Controller.TILESET_VERTICAL,
        )

        with tcod.console_init_root(TOTAL_WIDTH,
                                    TOTAL_HEIGHT,
                                    vsync=True, order='C') as root_console:
            self.view = view.View(root_console)

            while self.program_is_running:
                self.view.draw(self.model)
                tcod.console_flush()

                commands = self.model.players[0].get_commands()

                for event in tcod.event.wait():
                    if event.type == 'QUIT':
                        self.program_is_running = False
                        break

                    if event.type == 'KEYDOWN':
                        if event.repeat:
                            continue
                        self.dispatch(event.scancode, event.mod, commands)

                if not self.program_is_running:
                    break

                while self.model.players[0].has_intention():
                    self._tick()

            if self.player_died:
                if os.path.isfile(SAVE_FILE_NAME):
                    os.remove(SAVE_FILE_NAME)
                self.view.draw_death_screen()
                tcod.console_flush()
                Controller.wait_for_any_key()
            else:
                with open(SAVE_FILE_NAME, 'w') as file:
                    file.write(self.model.get_snapshot())

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

        if self.model.players[0].hp <= 0:
            self.program_is_running = False
            self.player_died = True
        mobs = []
        for mob in self.model.mobs:
            if mob.hp > 0:
                mobs.append(mob)
        self.model.mobs = mobs


class ClientController:
    """ The class responsible for controlling the main game flow for a game client. """

    def __init__(self, args):
        """ Initializes the game controller for a client so it is ready to start a new game. """
        channel = grpc.insecure_channel(args.address + ':' + str(args.port))
        self.stub = src.roguelike_pb2_grpc.GameStub(channel)
        self.pings = self.stub.Join(src.roguelike_pb2.Room(room=args.room))
        self.id = next(self.pings)

        mapm = self.stub.GetMap(self.id)
        tiles = [[MapTile.EMPTY if mapm.data[i * mapm.width + j].isEmpty else MapTile.BLOCKED for j in
                  range(mapm.width)] for i in range(mapm.height)]
        self.model = ClientModel(WorldMap.from_tiles(tiles), Player(Position(0, 0), Controller.DEFAULT_WEAPON_SET), [])
        self.program_is_running = True
        self.run_loop()

    def run_loop(self):
        tcod.console_set_custom_font(
            Controller.TILESET_PATH,
            Controller.TILESET_OPTIONS,
            Controller.TILESET_HORIZONTAL,
            Controller.TILESET_VERTICAL,
        )

        with tcod.console_init_root(TOTAL_WIDTH,
                                    TOTAL_HEIGHT,
                                    vsync=True, order='C') as root_console:
            self.view = view.View(root_console)

            while self.program_is_running:
                playerm = self.stub.GetPlayer(self.id)
                mobsm = self.stub.GetMobs(self.id)

                self.model.player.position = Position(playerm.position.x, playerm.position.y)
                self.model.player.hp = playerm.hp

                self.model.other_fighters = [RemoteFighter(mob.intensity, mob.style,
                                                           Position(mob.position.x, mob.position.y))
                                             for mob in mobsm.data]

                self.move_done = False

                commands = self.model.player.get_commands()

                def move(dir: int):
                    if self.move_done:
                        return
                    self.stub.SendIntention(Intention(moveId=dir, weaponId=self.model.player.used_weapon, id=self.id))
                    self.move_done = True

                commands['stay'] = lambda: move(0)
                commands['go_up'] = lambda: move(1)
                commands['go_left'] = lambda: move(2)
                commands['go_down'] = lambda: move(3)
                commands['go_right'] = lambda: move(4)

                for event in tcod.event.get():
                    if event.type == 'QUIT':
                        self.program_is_running = False
                        break

                while self.program_is_running and not self.move_done:
                    self.view.draw(self.model)
                    tcod.console_flush()

                    for event in tcod.event.wait():
                        if self.move_done:
                            break

                        if event.type == 'QUIT':
                            self.program_is_running = False
                            break

                        if event.type == 'KEYDOWN':
                            if event.repeat:
                                continue
                            Controller.dispatch(event.scancode, event.mod, commands)

                if not self.program_is_running:
                    break

                result = next(self.pings)

                if result.id == 'dead':
                    self.view.draw_death_screen()
                    tcod.console_flush()
                    Controller.wait_for_any_key()
                    self.program_is_running = False
        self.stub.Disconnect(self.id)
