import unittest

from src import fighter
from src import world_map
from src.world_map import Position


class TestMove(unittest.TestCase):
    def setUp(self):
        self.fighter = fighter.Fighter(Position(0, 0))
        self.map = world_map.WorldMap()

    def testMove_initial_zero(self):
        self.assertEqual(Position(0, 0), self.fighter.position)

    def testMove_move(self):
        self.fighter.move(Position(1, 2))

        self.assertEqual(Position(1, 2), self.fighter.position)

    def testMove_intentions(self):
        self.fighter.add_intention(fighter.FighterIntention.STAY)
        self.assertEqual(Position(0, 0), self.fighter.choose_move(self.map))

        self.fighter.add_intention(fighter.FighterIntention.MOVE_UP)
        self.assertEqual(Position(-1, 0), self.fighter.choose_move(self.map))

        self.fighter.add_intention(fighter.FighterIntention.MOVE_LEFT)
        self.assertEqual(Position(0, -1), self.fighter.choose_move(self.map))

        self.fighter.add_intention(fighter.FighterIntention.MOVE_DOWN)
        self.assertEqual(Position(1, 0), self.fighter.choose_move(self.map))

        self.fighter.add_intention(fighter.FighterIntention.MOVE_RIGHT)
        self.assertEqual(Position(0, 1), self.fighter.choose_move(self.map))


if __name__ == '__main__':
    unittest.main()
