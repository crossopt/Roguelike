""" Module containing the implementation of the graphic output for the game. """

import tcod
from tcod.console import Console

from src.model import Model
from src.world_map import MapTile

WALL_COLOR = tcod.white
PATH_COLOR = tcod.black
PLAYER_COLOR = tcod.yellow
MOB_COLOR = tcod.red
TEXT_COLOR = tcod.grey

ORD_SMILEY = 1

TILE_TO_BG = {
    MapTile.BLOCKED: WALL_COLOR,
    MapTile.EMPTY: PATH_COLOR
}


class View:
    """ Class responsible for displaying a view of the game world state to the user. """
    def __init__(self, root_console: Console):
        """ Initializes a View that will display to the given console. """
        self.console = root_console
        self.console.default_bg = WALL_COLOR
        self.console.default_fg = TEXT_COLOR

    def draw(self, model: Model):
        """ Displays the current state of the given Model. """
        self.console.clear()
        for i in range(model.map.height):
            for j in range(model.map.width):
                self.console.bg[i, j] = TILE_TO_BG[model.map.tiles[i][j]]
        player_coords = model.player.position.x, model.player.position.y
        for mob in model.mobs:
            mob_coords = mob.position.x, mob.position.y
            self.console.ch[mob_coords] = ORD_SMILEY
            self.console.fg[mob_coords] = MOB_COLOR
        self.console.ch[player_coords] = ORD_SMILEY
        self.console.fg[player_coords] = PLAYER_COLOR
