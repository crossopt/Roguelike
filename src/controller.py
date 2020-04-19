""" Module containing the main controller logic for the game. """

from argparse import ArgumentParser

import tcod
import tcod.event

import src.fighter
import src.strategies
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
            
        player = src.fighter.Player(game_map.get_random_empty_position())
        mobs = [src.fighter.Mob(game_map.get_random_empty_position(), src.strategies.CowardlyStrategy())]

        self.model = model.Model(game_map, player, mobs)
        self.program_is_running = True
        self.view = None

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

                while self.model.player.want_to_move():
                    self.tick()

    def tick(self):
        game_map = self.model.map
        tiles = game_map.tiles
        fighters = self.model.get_fighters()

        for fighter in fighters:
            intended_position = fighter.choose_move(self.model)
            if game_map.is_on_map(intended_position) and \
                tiles[intended_position.x][intended_position.y] == world_map.MapTile.EMPTY:
                fighter.move(intended_position)


    def dispatch(self, code, _mod, commands):
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
