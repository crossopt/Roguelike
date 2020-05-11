""" Module containing the implementation of various in-game fighters. """
from abc import abstractmethod, ABC
from enum import Enum
from typing import List

import src.model
import src.strategies
import src.world_map
from src.weapon import Weapon

PLAYER_HP = 20
MOB_HP = 10
PLAYER_BASE_ATTACK = 2
MOB_ATTACK = 4
ITEM_COUNT = 3


class PlayerIntention(Enum):
    """ Enum encapsulating the preferred action for a fighter. """
    STAY = 0
    MOVE_UP = 1
    MOVE_LEFT = 2
    MOVE_DOWN = 3
    MOVE_RIGHT = 4


class Fighter(ABC):
    """ Class for storing the various in-game fighter characters. """

    def __init__(self, position: 'src.model.Position'):
        """ Initializes a fighter with the given initial position. """
        self.position = position
        self.hp = None

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

    @abstractmethod
    def choose_move(self, current_model: 'src.model.FullModel'):
        """ Selects a move based on the state of the model world. """
        raise NotImplementedError()

    def get_position(self) -> 'src.world_map.Position':
        return self.position


class DrawableFighter(ABC):
    """ Class containing all of the necessary information to draw a fighter. """
    @abstractmethod
    def get_intensity(self) -> float:
        """ Returns the intensity of the fighter's color, which corresponds to its health. """

    @abstractmethod
    def get_style(self) -> str:
        """ Returns the name of the style that should be used for the fighter's drawing. """

    @abstractmethod
    def get_position(self) -> 'src.world_map.Position':
        """ Returns the position that the fighter should be drawn in. """


class Player(Fighter, DrawableFighter):
    """ Class for storing the player-controlled fighter character. """

    def __init__(self, position: 'src.model.Position', inventory: List[Weapon] = None,
                 used_weapon=None, hp: int = PLAYER_HP):
        """ Initializes a player character with the given initial position. """
        super(Player, self).__init__(position)
        self.hp = hp
        if inventory is None:
            inventory = []
        self.inventory = inventory
        self.used_weapon = used_weapon
        self._intentions = []

    def _add_intention(self, new_intention: PlayerIntention):
        """ Sets the fighter's move intention to a new one. """
        self._intentions.append(new_intention)

    def has_intention(self):
        """ Checks whether the player wants to move. """
        return len(self._intentions) > 0

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
        for i in range(ITEM_COUNT+1):
            commands['select_' + str(i)] = lambda i=i: self._select_weapon(i)
        return commands

    def _select_weapon(self, num):
        """ Sets the weapon being used to the chosen weapon. """
        if self.used_weapon == num:
            self.used_weapon = 0
        else:
            self.used_weapon = num

    def choose_move(self, _current_model: 'src.model.FullModel'):
        """ Chooses a move for the player based on the current intentions. """
        move = {PlayerIntention.STAY: (0, 0),
                PlayerIntention.MOVE_UP: (-1, 0),
                PlayerIntention.MOVE_LEFT: (0, -1),
                PlayerIntention.MOVE_DOWN: (1, 0),
                PlayerIntention.MOVE_RIGHT: (0, 1)}

        if len(self._intentions) == 0:
            intention = PlayerIntention.STAY
        else:
            intention = self._intentions[0]
            self._intentions = self._intentions[1:]
        dx, dy = move[intention]
        chosen_position = src.world_map.Position(self.position.x + dx, self.position.y + dy)
        return chosen_position

    def get_attack(self) -> int:
        return self.get_base_attack() + self.get_additional_attack()

    def get_base_attack(self) -> int:
        """ Returns the player's base attack strength. """
        return PLAYER_BASE_ATTACK

    def take_damage(self, damage: int) -> None:
        super(Player, self).take_damage(max(0, damage - self.get_defence()))

    def get_additional_attack(self):
        """ Returns the delta added to the player's attack strength from their weapons. """
        if self.used_weapon is not None:
            return self.inventory[self.used_weapon].attack
        return 0

    def get_defence(self):
        """ Returns the delta added to the player's defence from their weapons. """
        if self.used_weapon is not None:
            return self.inventory[self.used_weapon].defence
        return 0

    def get_confusion_prob(self):
        """ Returns the probability with which the player's attack confuses the defendant. """
        if self.used_weapon is not None:
            return self.inventory[self.used_weapon].confusion_prob
        return 0

    def get_intensity(self) -> float:
        return self.hp / PLAYER_HP

    def get_style(self) -> str:
        return 'player'


class RemoteFighter(DrawableFighter):
    """ Class for storing the fighter characters of remote players. """
    def __init__(self, intensity: float, style: str, position: 'src.world_map.Position'):
        self.intensity = intensity
        self.style = style
        self.position = position

    def get_intensity(self) -> float:
        return self.intensity

    def get_style(self) -> str:
        return self.style

    def get_position(self) -> 'src.world_map.Position':
        return self.position


class Mob(Fighter, DrawableFighter):
    """ Class for storing NPC mobs. """

    def __init__(self, position: 'src.model.Position',
                 fighting_strategy: 'src.strategies.FightingStrategy', hp: int = MOB_HP):
        """ Initializes a mob with the given initial position and fighting strategy. """
        super(Mob, self).__init__(position)
        self.hp = hp
        self.fighting_strategy = fighting_strategy

    def get_attack(self) -> int:
        return MOB_ATTACK

    def become_confused(self, time: int):
        """ The mob becomes confused for a chosen amount of ticks. """
        self.fighting_strategy = src.strategies.ConfusedStrategy(self.fighting_strategy, time)

    def choose_move(self, current_model: 'src.model.FullModel'):
        """ Chooses a move for the mob based on its strategy. """
        chosen_move = self.fighting_strategy.choose_move(current_model, self)
        self.fighting_strategy = self.fighting_strategy.update_strategy()
        return chosen_move

    def get_intensity(self) -> float:
        return self.hp / MOB_HP

    def get_style(self) -> str:
        if isinstance(self.fighting_strategy, src.strategies.ConfusedStrategy):
            return 'confused'
        elif isinstance(self.fighting_strategy, src.strategies.AggressiveStrategy):
            return 'aggressive'
        elif isinstance(self.fighting_strategy, src.strategies.PassiveStrategy):
            return 'passive'
        elif isinstance(self.fighting_strategy, src.strategies.ConfusedStrategy):
            return 'cowardly'
        return 'unknown'

