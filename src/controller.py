""" Module containing the main controller logic for the game. """

import tcod
import tcod.event

import src.fighter
from src import model
from src import view
from src import world_map
from src.world_map import RandomV1WorldMapSource


class Controller:
    """ The class responsible for controlling the main game flow. """
    _DEFAULT_MAP_WIDTH = 10
    _DEFAULT_MAP_HEIGHT = 10

    _TILESET_PATH = 'big_font.png'
    _TILESET_OPTIONS = tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE
    _TILESET_HORIZONTAL = 16
    _TILESET_VERTICAL = 16

    _WINDOW_HEIGTH = 10
    _WINDOW_WIDTH = 10

    def __init__(self):
        """ Initializes the game controller so it is ready to start a new game. """
        game_map = RandomV1WorldMapSource(Controller._DEFAULT_MAP_HEIGHT,
                                          Controller._DEFAULT_MAP_WIDTH).get()
        self.model = model.Model(game_map, game_map.get_player_start())
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

        with tcod.console_init_root(Controller._WINDOW_WIDTH,
                                    Controller._WINDOW_HEIGTH,
                                    vsync=True, order='C') as root_console:
            self.view = view.View(root_console)

            while self.program_is_running:
                self.view.draw(self.model)
                tcod.console_flush()

                for event in tcod.event.wait():
                    if event.type == 'QUIT':
                        self.program_is_running = False
                        break

                    if event.type == 'KEYDOWN':
                        if event.repeat:
                            continue
                        self.dispatch(event.scancode, event.mod)

                game_map = self.model.map
                tiles = game_map.tiles
                fighters = self.model.get_fighters()

                for fighter in fighters:
                    intended_position = fighter.choose_move(world_map)
                    if game_map.is_on_map(intended_position) and \
                       tiles[intended_position.x][intended_position.y] == world_map.MapTile.EMPTY:
                        fighter.move(intended_position)

    def dispatch(self, code, _mod):
        """ Handles the user's key down presses and sets the relevant intentions for a player.

        :param code: a scancode of the main key pressed.
        :param _mod: a modifier, a mask of the functional keys pressed with the main one.
        """
        code_to_intention = {tcod.event.SCANCODE_W: src.fighter.FighterIntention.MOVE_UP,
                             tcod.event.SCANCODE_A: src.fighter.FighterIntention.MOVE_LEFT,
                             tcod.event.SCANCODE_S: src.fighter.FighterIntention.MOVE_DOWN,
                             tcod.event.SCANCODE_D: src.fighter.FighterIntention.MOVE_RIGHT}
        if code in code_to_intention:
            self.model.add_player_intention(code_to_intention[code])
