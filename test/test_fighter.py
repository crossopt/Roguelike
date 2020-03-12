import unittest

from src import fighter
from src import world_map

class TestMove(unittest.TestCase):
    def setUp(self):
        self.fighter = fighter.Fighter(world_map.Position(0, 0))
        self.map = world_map.WorldMap()

    def testMove_initial_zero(self):
        self.assertEqual(0, self.fighter.position.x)
        self.assertEqual(0, self.fighter.position.y)

    def testMove_move(self):
        self.fighter.move(world_map.Position(1, 2))

        self.assertEqual(1, self.fighter.position.x)
        self.assertEqual(2, self.fighter.position.y)

    def testMove_intentions(self):
        self.fighter.set_intention(fighter.Will.STAY)
        self.assertEqual(0, self.fighter.choose_move(self.map).x)
        self.assertEqual(0, self.fighter.choose_move(self.map).y)

        self.fighter.set_intention(fighter.Will.MOVE_UP)
        self.assertEqual(-1, self.fighter.choose_move(self.map).x)
        self.assertEqual(0, self.fighter.choose_move(self.map).y)

        self.fighter.set_intention(fighter.Will.MOVE_LEFT)
        self.assertEqual(0, self.fighter.choose_move(self.map).x)
        self.assertEqual(-1, self.fighter.choose_move(self.map).y)

        self.fighter.set_intention(fighter.Will.MOVE_DOWN)
        self.assertEqual(1, self.fighter.choose_move(self.map).x)
        self.assertEqual(0, self.fighter.choose_move(self.map).y)

        self.fighter.set_intention(fighter.Will.MOVE_RIGHT)
        self.assertEqual(0, self.fighter.choose_move(self.map).x)
        self.assertEqual(1, self.fighter.choose_move(self.map).y)

    def testMove_wrong_intention(self):
        self.fighter.set_intention("Hello, Dear! Move up, s'il vous plait")
        runnable = lambda : self.fighter.choose_move(self.map)
        self.assertRaises(ValueError, runnable)


if __name__ == '__main__':
    unittest.main()
