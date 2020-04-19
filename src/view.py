""" Module containing the implementation of the graphic output for the game. """

import tcod
from tcod.console import Console

from src.fighter import MOB_HP
from src.model import Model
from src.strategies import ConfusedStrategy
from src.world_map import Position

WALL_COLOR = tcod.grey
PATH_COLOR = tcod.black
PLAYER_COLOR = tcod.yellow
MOB_COLOR = tcod.red
TEXT_COLOR = tcod.white
HUD_COLOR = tcod.black

ORD_SMILEY = 1

VIEW_HEIGHT = 13
VIEW_WIDTH = 13
HUD_WIDTH = 8
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
        for mob in model.mobs:
            intensity = 50 + int(mob.hp / MOB_HP * 200)
            if isinstance(mob.fighting_strategy, ConfusedStrategy):
                color = (0, intensity, 0)
            else:
                color = (intensity, 0, 0)
            self._draw_character(mob.position, offset, ch=ORD_SMILEY, fg=color)
        self._draw_character(model.player.position, offset, ch=ORD_SMILEY, fg=PLAYER_COLOR)

        # draw HUD

        for i in range(VIEW_HEIGHT):
            for j in range(VIEW_WIDTH, VIEW_WIDTH + HUD_WIDTH):
                self.console.bg[i, j] = HUD_COLOR

        self.console.print(VIEW_WIDTH, 0, 'HP  ' + str(model.player.hp))
        self.console.print(VIEW_WIDTH, 1, 'ATK ' + str(model.player.get_base_attack()) + '+' + str(model.player.get_additional_attack()))
        self.console.print(VIEW_WIDTH, 2, 'DEF ' + str(model.player.get_defence()))
        self.console.print(VIEW_WIDTH, 4, 'ITEMS:')
        for i in range(len(model.player.inventory)):
            start = '*' if i == model.player.used_weapon else ' '
            self.console.print(VIEW_WIDTH, 5 + i, start + model.player.inventory[i].name)

    def _draw_character(self, pos, offset, ch=None, fg=None, bg=None):
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
