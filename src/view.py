""" Module containing the implementation of the graphic output for the game. """

import tcod
from tcod.console import Console

from src.model import Model
from src.world_map import Position

WALL_COLOR = tcod.grey
PATH_COLOR = tcod.black
PLAYER_COLOR = tcod.yellow
TEXT_COLOR = tcod.white
HUD_COLOR = tcod.black

ORD_SMILEY = 1

MOB_SYMBOL = ORD_SMILEY
PLAYER_SYMBOL = ORD_SMILEY

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
        assert len(model.players) == 1
        player = model.players[0]
        offset = - player.position.x + OFFSETX, - player.position.y + OFFSETY
        for i in range(VIEW_HEIGHT):
            for j in range(VIEW_WIDTH):
                self.console.bg[i, j] = PATH_COLOR if model.map.is_empty(Position(i - offset[0], j - offset[1])) else WALL_COLOR
        for mob in model.mobs:
            self._draw_character(mob.position, offset, ch=MOB_SYMBOL, fg=self._style_to_color(mob.get_style(), mob.get_intensity()))
        self._draw_character(player.position, offset, ch=PLAYER_SYMBOL, fg=PLAYER_COLOR)

        # draw HUD

        for i in range(VIEW_HEIGHT):
            for j in range(VIEW_WIDTH, VIEW_WIDTH + HUD_WIDTH):
                self.console.bg[i, j] = HUD_COLOR

        self.console.print(VIEW_WIDTH, 0, 'HP  ' + str(player.hp))
        self.console.print(VIEW_WIDTH, 1, 'ATK ' + str(player.get_base_attack()) + '+' + str(player.get_additional_attack()))
        self.console.print(VIEW_WIDTH, 2, 'DEF ' + str(player.get_defence()))
        self.console.print(VIEW_WIDTH, 4, 'ITEMS:')
        for i in range(len(player.inventory)):
            start = '*' if i == player.used_weapon else ' '
            self.console.print(VIEW_WIDTH, 5 + i, start + player.inventory[i].name)

    def draw_death_screen(self):
        self.draw_message('YOU ARE DEAD')

    def draw_message(self, msg: str):
        self.console.clear(bg=tcod.black)
        self.console.print(TOTAL_WIDTH // 2, TOTAL_HEIGHT // 2, msg, alignment=tcod.CENTER)

    def _style_to_color(self, style: str, intensity: int):
        style_to_color = {
            'confused': (0, intensity, 0),
            'passive': (0, 0, intensity),
            'aggressive': (intensity, 0, 0),
            # 'cowardly': ,
            # 'other_player': ,
            # 'unknown': ,
        }
        return style_to_color.get(style, (intensity, intensity, intensity))

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
