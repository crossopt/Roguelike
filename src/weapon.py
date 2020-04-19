from dataclasses import dataclass


@dataclass
class Weapon:
    name: str
    attack: int
    defence: int
    confusion_prob: float


class WeaponBuilder:
    def __init__(self):
        self.name = None
        self.attack = 0
        self.defence = 0
        self.confusion_prob = 0.0

    def with_name(self, name: str):
        self.name = name
        return self

    def with_attack(self, attack: int):
        self.attack = attack
        return self

    def with_defence(self, defence: int):
        self.defence = defence
        return self

    def with_confusion_prob(self, confusion_prob: float):
        if confusion_prob < 0 or confusion_prob > 1:
            raise ValueError()
        self.confusion_prob = confusion_prob
        return self

    def build(self):
        if self.name is None:
            raise ValueError()
        return Weapon(self.name, self.attack, self.defence, self.confusion_prob)