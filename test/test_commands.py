import unittest

from src import controller
from src.world_map import Position, WorldMap, MapTile

UP_KEY = 26
DOWN_KEY = 22
LEFT_KEY = 4
RIGHT_KEY = 7
ONE_KEY = 30
TWO_KEY = 31
THREE_KEY = 32


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.controller = controller.Controller(_test_args=[])
        self.controller.model.map = WorldMap.from_tiles([[MapTile.EMPTY for _ in range(3)] for _ in range(3)])
        self.controller.model.player.position = Position(1, 1)
        self.commands = self.controller.model.player.get_commands()

    def tearDown(self):
        self.controller._remove_saved_game()

    def testPlayerMovesUp(self):
        self.controller._dispatch(UP_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.choose_move(None), Position(0, 1))

    def testPlayerMovesDown(self):
        self.controller._dispatch(DOWN_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.choose_move(None), Position(2, 1))

    def testPlayerMovesLeft(self):
        self.controller._dispatch(LEFT_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.choose_move(None), Position(1, 0))

    def testPlayerMovesRight(self):
        self.controller._dispatch(RIGHT_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.choose_move(None), Position(1, 2))

    def testPlayerTakesWeapon(self):
        self.assertIsNone(self.controller.model.player.used_weapon)
        self.controller._dispatch(ONE_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.used_weapon, 0)
        self.controller._dispatch(ONE_KEY, 0, self.commands)
        self.assertIsNone(self.controller.model.player.used_weapon)
        self.controller._dispatch(TWO_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.used_weapon, 1)
        self.controller._dispatch(THREE_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.used_weapon, 2)
        self.controller._dispatch(TWO_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.used_weapon, 1)
        self.controller._dispatch(TWO_KEY, 0, self.commands)
        self.assertIsNone(self.controller.model.player.used_weapon)
        self.controller._dispatch(THREE_KEY, 0, self.commands)
        self.assertEqual(self.controller.model.player.used_weapon, 2)
        self.controller._dispatch(THREE_KEY, 0, self.commands)
        self.assertIsNone(self.controller.model.player.used_weapon)


if __name__ == '__main__':
    unittest.main()
