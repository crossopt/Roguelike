""" Module containing the implementation of the graphic output for the game. """

import tcod
from tcod.console import Console

from src.fighter import MOB_HP
from src.model import Model
from src.world_map import Position

WALL_COLOR = tcod.grey
PATH_COLOR = tcod.black
PLAYER_COLOR = tcod.yellow
MOB_COLOR = tcod.red
TEXT_COLOR = tcod.grey
HUD_COLOR = tcod.black

ORD_SMILEY = 1

VIEW_HEIGHT = 9
VIEW_WIDTH = 9
HUD_WIDTH = 7
TOTAL_WIDTH = VIEW_WIDTH + HUD_WIDTH
TOTAL_HEIGHT = VIEW_HEIGHT

OFFSETX = (VIEW_HEIGHT - 1) // 2
OFFSETY = (VIEW_WIDTH - 1) // 2


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
        offset = - model.player.position.x + OFFSETX, - model.player.position.y + OFFSETY
        for i in range(VIEW_HEIGHT):
            for j in range(VIEW_WIDTH):
                self.console.bg[i, j] = PATH_COLOR if model.map.is_empty(Position(i - offset[0], j - offset[1])) else WALL_COLOR
        for i in range(VIEW_HEIGHT):
            for j in range(VIEW_WIDTH, VIEW_WIDTH + HUD_WIDTH):
                self.console.bg[i, j] = HUD_COLOR
        for mob in model.mobs:
            self.set_position(mob.position, offset, ch=ORD_SMILEY, fg=(50 + int(mob.hp / MOB_HP * 200), 0, 0))
        self.set_position(model.player.position, offset, ch=ORD_SMILEY, fg=PLAYER_COLOR)

    def set_position(self, pos, offset, ch=None, fg=None, bg=None):
        pos_pair = pos.x + offset[0], pos.y + offset[1]
        if pos_pair[0] < 0 or pos_pair[0] >= VIEW_HEIGHT or\
           pos_pair[1] < 0 or pos_pair[1] >= VIEW_WIDTH:
            return
        if ch is not None:
            self.console.ch[pos_pair] = ch
        if fg is not None:
            self.console.fg[pos_pair] = fg
        if bg is not None:
            self.console.bg[pos_pair] = bg
