""" Module containing the details of the fighting system used by in-game characters. """
from src.fighter import Fighter, Mob


class CoolFightingSystem:
    """ The fighting system used by the game, where one fighter attacks another non-simultaneously. """
    @staticmethod
    def fight(attacker: Fighter, defender: Fighter):
        """ Deal damage from the attacker to the defender. Mobs do not attack mobs. """
        if isinstance(attacker, Mob) and isinstance(defender, Mob):
            return
        defender.take_damage(attacker.get_attack())
