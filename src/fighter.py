""" Module containing the implementation of various in-game fighters. """

from enum import Enum

import src.model
import src.world_map

class FighterIntention(Enum):
    """ Enum encapsulating the preferred action for a fighter. """
    STAY = 0
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4


class Fighter:
    """ Class for storing the various in-game fighter characters. """

    def __init__(self, initial_position: 'src.model.Position'):
        """ Initializes a fighter with the given initial position. """
        self.position = initial_position
        # self.intentions = []

    def move(self, new_position: 'src.model.Position'):
        """ Changes the fighter's position. """
        self.position = new_position

    # def add_intention(self, new_intention: FighterIntention):
    #     """ Sets the fighter's move intention to a new one. """
    #     self.intentions.append(new_intention)

    def choose_move(self, current_model: 'src.model.Model'):
        """ Selects a move based on the state of the game map. """
        raise NotImplementedError()
        

class Player(Fighter):

    def __init__(self, initial_position: 'src.model.Position'):
        super(Player, self).__init__(initial_position)
        self.intentions = []

    def add_intention(self, new_intention: FighterIntention):
        """ Sets the fighter's move intention to a new one. """
        self.intentions.append(new_intention)

    def choose_move(self, current_model: 'src.model.Model'):
        world_map = current_model.map
        move = {FighterIntention.STAY: (0, 0),
                FighterIntention.MOVE_UP: (-1, 0),
                FighterIntention.MOVE_LEFT: (0, -1),
                FighterIntention.MOVE_DOWN: (1, 0),
                FighterIntention.MOVE_RIGHT: (0, 1)}

        if len(self.intentions) == 0:
            intention = FighterIntention.STAY
        else:
            intention = self.intentions[0]
            self.intentions = self.intentions[1:]
        dx, dy = move[intention]
        chosen_position = src.world_map.Position(self.position.x + dx, self.position.y + dy)
        return chosen_position

class Mob(Fighter):

    def __init__(self, initial_position: 'src.model.Position', fighting_strategy):
        super(Mob, self).__init__(initial_position)
        self.fighting_strategy = fighting_strategy

    def choose_move(self, current_model: 'src.model.Model'):
        (dx, dy) = fighting_strategy.choose_move(current_model, self)
        return src.world_map.Position(self.position.x + dx, self.position.y + dy)
