""" Module containing the details of the fighting system used by in-game characters. """
import random

from src.fighter import Fighter, Mob, Player

CONFUSION_TIME = 5


class CoolFightingSystem:
    """ The fighting system used by the game, where one fighter attacks another
    non-simultaneously. """

    @staticmethod
    def fight(attacker: Fighter, defender: Fighter):
        """ Deal damage from the attacker to the defender. Mobs do not attack mobs. """
        if isinstance(attacker, Mob) and isinstance(defender, Mob):
            return
        defender.take_damage(attacker.get_attack())
        if (isinstance(attacker, Player) and
                isinstance(defender, Mob) and
                random.random() < attacker.get_confusion_prob()):
            defender.become_confused(CONFUSION_TIME)
