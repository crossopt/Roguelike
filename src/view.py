""" Module containing the implementation of the graphic output for the game. """

import tcod
from tcod.console import Console

from .model import Model

from .world_map import MapTile

wall_color = tcod.white
path_color = tcod.black

tile_to_bg = {
    MapTile.BLOCKED: wall_color,
    MapTile.EMPTY: path_color
}


class View:
    def __init__(self, root_console: Console):
        self.console = root_console
        self.console.default_bg = wall_color

    def draw(self, model: Model):
        self.console.clear()
        for i in range(model.map.height):
            for j in range(model.map.width):
                self.console.bg[i, j] = tile_to_bg[model.map[i][j]]
        self.console.ch[model.player.position.x, model.player.position.y] = ord("F")
