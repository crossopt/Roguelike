""" Module containing the implementation of the graphic output for the game. """

import tcod
from tcod.console import Console

import model as package_model
import world_map

wall_color = tcod.white
path_color = tcod.black
player_color = tcod.yellow
text_color = tcod.grey

tile_to_bg = {
    world_map.MapTile.BLOCKED: wall_color,
    world_map.MapTile.EMPTY: path_color
}


class View:
    def __init__(self, root_console: Console):
        self.console = root_console
        self.console.default_bg = wall_color
        self.console.default_fg = text_color

    def draw(self, model: package_model.Model):
        self.console.clear()
        for i in range(model.map.height):
            for j in range(model.map.width):
                self.console.bg[i, j] = tile_to_bg[model.map[i][j]]
        player_coords = model.player.position.x, model.player.position.y
        self.console.ch[player_coords] = ord("F")
        self.console.fg[player_coords] = player_color
