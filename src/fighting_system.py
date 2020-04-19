from src.fighter import Fighter, Mob


class CoolFightingSystem:
    @staticmethod
    def fight(who: Fighter, whom: Fighter):
        if isinstance(who, Mob) and isinstance(whom, Mob):
            return
        whom.deal_damage(who.get_attack())
