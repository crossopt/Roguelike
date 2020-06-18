import unittest

from src import fighter
from src import world_map
from src.strategies import PassiveStrategy
from src.world_map import Position
from src.model import Model


class TestFighters(unittest.TestCase):
    def setUp(self):
        self.player = fighter.Player(Position(0, 0))
        self.mob = fighter.Mob(Position(2, 2), PassiveStrategy())
        self.model = Model(world_map.WorldMap(), self.player, [self.mob])

    def testGetAttack(self):
        self.assertEqual(fighter.MOB_ATTACK, self.mob.get_attack())
        self.assertEqual(fighter.PLAYER_BASE_ATTACK, self.player.get_attack())

    def testTakeDamage(self):
        self.assertEqual(fighter.PLAYER_HP, self.player.hp)
        self.player.take_damage(5)
        self.assertEqual(fighter.PLAYER_HP - 5, self.player.hp)
        self.player.take_damage(500)
        self.assertEqual(0, self.player.hp)
        self.assertEqual(fighter.MOB_HP, self.mob.hp)
        self.mob.take_damage(1)
        self.assertEqual(fighter.MOB_HP - 1, self.mob.hp)
        self.mob.take_damage(10)
        self.assertEqual(0, self.mob.hp)

    def testMove_initial_zero(self):
        self.assertEqual(Position(0, 0), self.player.position)
        self.assertEqual(Position(2, 2), self.mob.position)

    def testMove_move(self):
        self.player.move(Position(1, 2))
        self.assertEqual(Position(1, 2), self.player.position)

        self.mob.move(Position(1, 2))
        self.assertEqual(Position(1, 2), self.mob.position)

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
