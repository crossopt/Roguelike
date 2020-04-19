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
        for mob in model.mobs:
            self.set_position(mob.position, ch=ORD_SMILEY, fg=MOB_COLOR)
        self.set_position(model.player.position, ch=ORD_SMILEY, fg=PLAYER_COLOR)

    def set_position(self, pos, ch=None, fg=None, bg=None):
        pos_pair = pos.x, pos.y
        if ch is not None:
            self.console.ch[pos_pair] = ch
        if fg is not None:
            self.console.fg[pos_pair] = fg
        if bg is not None:
            self.console.bg[pos_pair] = bg
