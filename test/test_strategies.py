import unittest

from src import fighter
from src import world_map
from src import model
from src import strategies


class TestStrategies(unittest.TestCase):

    def setUp(self):
        self.map = world_map.WorldMap.from_tiles([[world_map.MapTile.EMPTY for _ in range(10)] for _ in range(10)])
        self.player = fighter.Player(world_map.Position(0, 0))

    def testPassive(self):
        self.mobs = [fighter.Mob(world_map.Position(5, 5), strategies.PassiveStrategy())]
        self.model = model.FullModel(self.map, [self.player], self.mobs)

        self.assertEqual(5, self.mobs[0].choose_move(self.model).x)
        self.assertEqual(5, self.mobs[0].choose_move(self.model).y)

    def testAggressive(self):
        self.mobs = [fighter.Mob(world_map.Position(5, 5), strategies.AggressiveStrategy())]
        self.model = model.FullModel(self.map, [self.player], self.mobs)

        self.assertEqual(4, self.mobs[0].choose_move(self.model).x)
        self.assertEqual(5, self.mobs[0].choose_move(self.model).y)

    def testCowardly(self):
        self.mobs = [fighter.Mob(world_map.Position(5, 5), strategies.CowardlyStrategy())]
        self.model = model.FullModel(self.map, [self.player], self.mobs)

        self.assertEqual(5, self.mobs[0].choose_move(self.model).x)
        self.assertEqual(6, self.mobs[0].choose_move(self.model).y)

    def testConfusedThenPassive(self):
        self.mobs = [fighter.Mob(world_map.Position(5, 5), strategies.ConfusedStrategy(strategies.PassiveStrategy(), 1))]
        self.model = model.FullModel(self.map, [self.player], self.mobs)

        first_move = self.mobs[0].choose_move(self.model)
        neighbours = self.model.map.get_empty_neighbors(self.mobs[0].position)
        self.assertTrue(first_move in neighbours)
        self.assertEqual(5, self.mobs[0].choose_move(self.model).x)
        self.assertEqual(5, self.mobs[0].choose_move(self.model).y)

    def testConfusedRanIntoTrap(self):
        self.mobs = [fighter.Mob(world_map.Position(5, 5), strategies.ConfusedStrategy(strategies.PassiveStrategy(), 1))]
        self.model = model.FullModel(self.map, [self.player], self.mobs)
        self.map.tiles[5][4] = world_map.MapTile.BLOCKED
        self.map.tiles[6][5] = world_map.MapTile.BLOCKED
        self.map.tiles[5][6] = world_map.MapTile.BLOCKED

        first_move = self.mobs[0].choose_move(self.model)
        self.assertEqual(4, first_move.x)
        self.assertEqual(5, first_move.y)