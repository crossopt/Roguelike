import unittest

from src import fighter
from src import world_map
from src.strategies import PassiveStrategy, CowardlyStrategy, ConfusedStrategy, AggressiveStrategy
from src.world_map import Position
from src.model import Model


class TestSnapshots(unittest.TestCase):
    def setUp(self):
        self.default_map = world_map.WorldMap()
        self.default_player = fighter.Player(Position(0, 0))
        self.default_mob = fighter.Mob(Position(2, 2), PassiveStrategy())

    @staticmethod
    def checkMapsMatch(first_map, second_map):
        if not first_map or not second_map:
            return not second_map and not first_map
        if first_map.height != second_map.height or first_map.width != second_map.width:
            return False
        for first_tile, second_tile in zip(sum(first_map.tiles, []), sum(second_map.tiles, [])):
            if first_tile != second_tile:
                return False
        return True

    @staticmethod
    def checkWeaponsMatch(first_weapon, second_weapon):
        return first_weapon.name == second_weapon.name and \
               first_weapon.attack == second_weapon.attack and \
               first_weapon.defence == second_weapon.defence and \
               first_weapon.confusion_prob == second_weapon.confusion_prob

    @staticmethod
    def checkPlayersMatch(first_player, second_player):
        if not first_player or not second_player:
            return not second_player and not first_player
        return first_player.position.x == second_player.position.x and \
            first_player.position.y == second_player.position.y and \
            first_player.hp == second_player.hp and \
            first_player.used_weapon == second_player.used_weapon and \
            len(first_player.inventory) == len(second_player.inventory) and \
            sum(map(lambda x, y: not TestSnapshots.checkWeaponsMatch(x, y),
                    zip(first_player.inventory, second_player.inventory))) == 0

    @staticmethod
    def checkStrategiesMatch(first_strategy, second_strategy):
        if type(first_strategy) != type(second_strategy):
            return False
        return type(first_strategy) != ConfusedStrategy or \
            first_strategy.confusion_time == second_strategy.confusion_time and \
            TestSnapshots.checkStrategiesMatch(first_strategy.original_strategy, second_strategy.original_strategy)

    @staticmethod
    def checkMobsMatch(first_mob, second_mob):
        return first_mob.position.x == second_mob.position.x and \
               first_mob.position.y == second_mob.position.y and \
               first_mob.hp == second_mob.hp and \
               TestSnapshots.checkStrategiesMatch(first_mob.fighting_strategy, second_mob.fighting_strategy)

    @staticmethod
    def checkMobListsMatch(first_mob_list, second_mob_list):
        if not first_mob_list or not second_mob_list:
            return not second_mob_list and not first_mob_list
        if len(first_mob_list) != len(second_mob_list):
            return False
        for first_mob, second_mob in zip(first_mob_list, second_mob_list):
            if not TestSnapshots.checkMobsMatch(first_mob, second_mob):
                return False
        return True

    @staticmethod
    def checkModelsAreEqual(first_model, second_model):
        return TestSnapshots.checkMapsMatch(first_model.map, second_model.map) and \
               TestSnapshots.checkPlayersMatch(first_model.player, second_model.player) and \
               TestSnapshots.checkMobListsMatch(first_model.mobs, second_model.mobs)

    def testSerializing_emptyModel(self):
        model = Model()
        other_model = Model(self.default_map, self.default_player, [self.default_mob])
        self.assertFalse(self.checkModelsAreEqual(model, other_model))
        other_model.set_snapshot(model.get_snapshot())
        self.assertTrue(self.checkModelsAreEqual(model, other_model))

    def testSerializing_modelWithPlayer(self):
        model = Model(player=fighter.Player(Position(2, 0)))
        other_model = Model(self.default_map, self.default_player, [self.default_mob])
        self.assertFalse(self.checkModelsAreEqual(model, other_model))
        other_model.set_snapshot(model.get_snapshot())
        self.assertTrue(self.checkModelsAreEqual(model, other_model))

    def testSerializing_modelWithMap(self):
        model = Model(map=world_map.WorldMap())
        other_model = Model(self.default_map, self.default_player, [self.default_mob])
        self.assertFalse(self.checkModelsAreEqual(model, other_model))
        other_model.set_snapshot(model.get_snapshot())
        self.assertTrue(self.checkModelsAreEqual(model, other_model))

    def testSerializing_modelWithMobsAllStrategies(self):
        model = Model(mobs=[fighter.Mob(Position(2, 2), PassiveStrategy()),
                            fighter.Mob(Position(2, 2), AggressiveStrategy()),
                            fighter.Mob(Position(2, 2), CowardlyStrategy()),
                            fighter.Mob(Position(3, 3), ConfusedStrategy(ConfusedStrategy(PassiveStrategy(), 5), 15))])
        other_model = Model(self.default_map, self.default_player, [self.default_mob])
        self.assertFalse(self.checkModelsAreEqual(model, other_model))
        other_model.set_snapshot(model.get_snapshot())
        self.assertTrue(self.checkModelsAreEqual(model, other_model))


if __name__ == '__main__':
    unittest.main()
