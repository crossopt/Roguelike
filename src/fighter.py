""" Module containing the implementation of various in-game fighters. """
from abc import abstractmethod, ABC
from enum import Enum

import src.model
import src.world_map


PLAYER_HP = 20
MOB_HP    = 10
PLAYER_BASE_ATTACK = 2
MOB_ATTACK = 1


class PlayerIntention(Enum):
    """ Enum encapsulating the preferred action for a fighter. """
    STAY = 0
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4


class Fighter(ABC):
    """ Class for storing the various in-game fighter characters. """
    def __init__(self, initial_position: 'src.model.Position'):
        """ Initializes a fighter with the given initial position. """
        self.position = initial_position
        self.hp       = None

    def move(self, new_position: 'src.model.Position'):
        """ Changes the fighter's position. """
        self.position = new_position

    def take_damage(self, damage: int) -> None:
        """ Deals the given amount of damage to the fighter. """
        damage = min(damage, self.hp)
        self.hp -= damage

    @abstractmethod
    def get_attack(self) -> int:
        """ Returns the strength of the fighter's attack. """
        pass

    @abstractmethod
    def choose_move(self, current_model: 'src.model.Model'):
        """ Selects a move based on the state of the model world. """
        raise NotImplementedError()
        

class Player(Fighter):
    """ Class for storing the player-controlled fighter character. """
    def get_attack(self) -> int:
        return PLAYER_BASE_ATTACK + self.get_additional_attack()

    def __init__(self, initial_position: 'src.model.Position'):
        """ Initializes a player character with the given initial position. """
        super(Player, self).__init__(initial_position)
        self.hp = PLAYER_HP
        self.intentions = []

    def _add_intention(self, new_intention: PlayerIntention):
        """ Sets the fighter's move intention to a new one. """
        self.intentions.append(new_intention)

    def has_intention(self):
        """ Checks whether the player wants to move. """
        return len(self.intentions) > 0

    def get_commands(self):
        """ Returns a list of possible commands for the player. """
        cmd_name_to_intention = {'stay': PlayerIntention.STAY,
                                 'go_up': PlayerIntention.MOVE_UP,
                                 'go_left': PlayerIntention.MOVE_LEFT,
                                 'go_down': PlayerIntention.MOVE_DOWN,
                                 'go_right': PlayerIntention.MOVE_RIGHT}
        commands = dict()
        for cmd_name, intention in cmd_name_to_intention.items():
            commands[cmd_name] = lambda intention=intention: self._add_intention(intention)
        return commands

    def choose_move(self, _current_model: 'src.model.Model'):
        """ Chooses a move for the player based on the current intentions. """
        move = {PlayerIntention.STAY: (0, 0),
                PlayerIntention.MOVE_UP: (-1, 0),
                PlayerIntention.MOVE_LEFT: (0, -1),
                PlayerIntention.MOVE_DOWN: (1, 0),
                PlayerIntention.MOVE_RIGHT: (0, 1)}

        if len(self.intentions) == 0:
            intention = PlayerIntention.STAY
        else:
            intention = self.intentions[0]
            self.intentions = self.intentions[1:]
        dx, dy = move[intention]
        chosen_position = src.world_map.Position(self.position.x + dx, self.position.y + dy)
        return chosen_position

    def get_additional_attack(self):
        return 0 # TODO


class Mob(Fighter):
    """ Class for storing NPC mobs. """

    def get_attack(self) -> int:
        return MOB_ATTACK

    def __init__(self, initial_position: 'src.model.Position', fighting_strategy):
        """ Initializes a mob with the given initial position and fighting strategy. """
        super(Mob, self).__init__(initial_position)
        self.hp = MOB_HP
        self.fighting_strategy = fighting_strategy

    def choose_move(self, current_model: 'src.model.Model'):
        """ Chooses a move for the mob based on its strategy. """
        return self.fighting_strategy.choose_move(current_model, self)
