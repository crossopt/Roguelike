""" Module containing the main controller logic for the game. """

import tcod
import tcod.event

import src.fighter
from src import model
from src import view
from src import world_map


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
        game_map = world_map.WorldMap()
        game_map.generate(Controller._DEFAULT_MAP_HEIGHT, Controller._DEFAULT_MAP_WIDTH)
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

                self.model.set_player_intention(src.fighter.FighterIntention.STAY)

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

        if code == tcod.event.SCANCODE_W:
            self.model.set_player_intention(src.fighter.FighterIntention.MOVE_UP)
        elif code == tcod.event.SCANCODE_A:
            self.model.set_player_intention(src.fighter.FighterIntention.MOVE_LEFT)
        elif code == tcod.event.SCANCODE_S:
            self.model.set_player_intention(src.fighter.FighterIntention.MOVE_DOWN)
        elif code == tcod.event.SCANCODE_D:
            self.model.set_player_intention(src.fighter.FighterIntention.MOVE_RIGHT)
