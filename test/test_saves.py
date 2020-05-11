import os
import unittest

from src import controller
from src.model import Model


class TestSaves(unittest.TestCase):
    def setUp(self):
        self.controller = controller.Controller(_test_args=[])
        self.controller._remove_saved_game()

    def testSaveActuallySaves(self):
        self.assertFalse(os.path.isfile(controller.SAVE_FILE_NAME))
        self.controller._save_game()
        self.assertTrue(os.path.isfile(controller.SAVE_FILE_NAME))

    def testSaveSavesOnlyOnce(self):
        self.controller._save_game()
        with open(controller.SAVE_FILE_NAME, 'r') as file:
            old_save = file.read()
        self.controller.model = Model()
        self.controller._save_game()
        with open(controller.SAVE_FILE_NAME, 'r') as file:
            new_save = file.read()
        self.assertNotEqual(old_save, new_save)

    def testPlayerDeathForbidsSaves(self):
        self.assertFalse(os.path.isfile(controller.SAVE_FILE_NAME))
        self.controller._save_game()
        self.assertTrue(os.path.isfile(controller.SAVE_FILE_NAME))
        self.controller._remove_saved_game()
        self.controller.player_died = True
        self.assertFalse(os.path.isfile(controller.SAVE_FILE_NAME))
        self.controller._save_game()
        self.assertFalse(os.path.isfile(controller.SAVE_FILE_NAME))


if __name__ == '__main__':
    unittest.main()
