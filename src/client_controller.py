""" Module containing the main controller logic for the game. """

import os
from argparse import ArgumentParser

import grpc
import tcod
import tcod.event

from src import view
from src.fighter import RemoteFighter
from src.model import ClientModel
from src.roguelike_pb2 import Intention
from src.view import TOTAL_WIDTH, TOTAL_HEIGHT

import src.roguelike_pb2_grpc
from src.world_map import WorldMap, MapTile, Position

SAVE_FILE_NAME = 'save'


class ClientController:
    """ The class responsible for controlling the main game flow. """
    _DEFAULT_MAP_WIDTH = 30
    _DEFAULT_MAP_HEIGHT = 30
    _MOB_COUNT = 8

    _TILESET_PATH = 'fonts/medium_font.png'
    _TILESET_OPTIONS = tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE
    _TILESET_HORIZONTAL = 16
    _TILESET_VERTICAL = 16

    def __init__(self):
        """ Initializes the game controller so it is ready to start a new game. """
        parser = ArgumentParser(description='A simple console-based rogue-like game.')
        parser.add_argument('map_path', type=str, nargs='?', help='path to map file to load')
        parser.add_argument('--new_game', nargs='?', dest='new_game_demanded', const=True,
                            default=False)

        args = parser.parse_args()

        channel = grpc.insecure_channel('localhost:50051')
        self.stub = src.roguelike_pb2_grpc.GameStub(channel)
        self.pings = self.stub.Join(src.roguelike_pb2.Room(room='test'))
        self.id = self.pings.__next__()
        mapm = self.stub.GetMap(self.id)
        tiles = [[MapTile.EMPTY if mapm[i * mapm.width + j].isEmpty else MapTile.BLOCKED for j in
                  range(mapm.width)] for i in range(mapm.height)]
        self.model = ClientModel(WorldMap.from_tiles(tiles), None, None)
        self.run_loop()

    def run_loop(self):
        """ Starts a new game and runs it until the user quits the game. """
        tcod.console_set_custom_font(
            ClientController._TILESET_PATH,
            ClientController._TILESET_OPTIONS,
            ClientController._TILESET_HORIZONTAL,
            ClientController._TILESET_VERTICAL,
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
                                             for mob in mobsm]

                self.move_done = False

                commands = self.model.player.get_commands()

                def move(dir: int):
                    self.stub.SendIntention(Intention(command=dir, weaponId=self.model.player.used_weapon, id=self.id))
                    self.move_done = True

                commands['stay'] = lambda: move(0)
                commands['go_up'] = lambda: move(1)
                commands['go_left'] = lambda: move(2)
                commands['go_down'] = lambda: move(3)
                commands['go_right'] = lambda: move(4)

                while self.program_is_running and not self.move_done:
                    self.view.draw(self.model)
                    tcod.console_flush()

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

                result = self.pings.__next__()

                if result == 'dead':
                    self.view.draw_death_screen()
                    tcod.console_flush()
                    self._wait_for_any_key()
                    self.program_is_running = False

    @staticmethod
    def _wait_for_any_key():
        for _ in tcod.event.wait():
            pass
        while True:
            for event in tcod.event.wait():
                if event.type in ['QUIT', 'KEYDOWN']:
                    return

    @staticmethod
    def _dispatch(code, _mod, commands):
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
                       tcod.event.SCANCODE_1: commands['select_1'],
                       tcod.event.SCANCODE_2: commands['select_2'],
                       tcod.event.SCANCODE_3: commands['select_3']}
        if code in code_to_cmd:
            code_to_cmd[code]()
