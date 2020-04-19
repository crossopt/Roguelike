import unittest

from src import fighter
from src import world_map
from src.world_map import Position
from src.model import Model


class TestPlayerMove(unittest.TestCase):
    def setUp(self):
        self.player = fighter.Player(Position(0, 0))
        self.model = Model(world_map.WorldMap(), self.player, [])

    def testMove_initial_zero(self):
        self.assertEqual(Position(0, 0), self.player.position)

    def testMove_move(self):
        self.player.move(Position(1, 2))
        self.assertEqual(Position(1, 2), self.player.position)

    def testMove_intentions(self):
        self.player._add_intention(fighter.PlayerIntention.STAY)
        self.assertTrue(self.player.has_intention())
        self.assertEqual(Position(0, 0), self.player.choose_move(self.model))

        self.player._add_intention(fighter.PlayerIntention.MOVE_UP)
        self.assertTrue(self.player.has_intention())
        self.assertEqual(Position(-1, 0), self.player.choose_move(self.model))

        self.player._add_intention(fighter.PlayerIntention.MOVE_LEFT)
        self.assertTrue(self.player.has_intention())
        self.assertEqual(Position(0, -1), self.player.choose_move(self.model))

        self.player._add_intention(fighter.PlayerIntention.MOVE_DOWN)
        self.assertTrue(self.player.has_intention())
        self.assertEqual(Position(1, 0), self.player.choose_move(self.model))

        self.player._add_intention(fighter.PlayerIntention.MOVE_RIGHT)
        self.assertTrue(self.player.has_intention())
        self.assertEqual(Position(0, 1), self.player.choose_move(self.model))


if __name__ == '__main__':
    unittest.main()
