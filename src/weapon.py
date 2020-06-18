""" Module containing the implementation of various in-game weapons. """
from dataclasses import dataclass


@dataclass
class Weapon:
    """ Class for storing various weapons in the game. """
    name: str
    attack: int
    defence: int
    confusion_prob: float


class WeaponBuilder:
    """ Builder class for creating weapons. """
    def __init__(self):
        self.name = None
        self.attack = 0
        self.defence = 0
        self.confusion_prob = 0.0

    def with_name(self, name: str):
        """ Adds a name to the weapon. """
        self.name = name
        return self

    def with_attack(self, attack: int):
        """ Adds an attack strength to the weapon. """
        self.attack = attack
        return self

    def with_defence(self, defence: int):
        """ Adds a defence capability to the weapon. """
        self.defence = defence
        return self

    def with_confusion_prob(self, confusion_prob: float):
        """ Adds a probability with which the weapon has a confusion effect. """
        if confusion_prob < 0 or confusion_prob > 1:
            raise ValueError()
        self.confusion_prob = confusion_prob
        return self

    def build(self):
        """ Returns the built weapon. """
        if self.name is None:
            raise ValueError()
        return Weapon(self.name, self.attack, self.defence, self.confusion_prob)
