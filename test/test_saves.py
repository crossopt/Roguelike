import unittest

from src import fighter
from src import world_map
from src.controller import Controller
from src.strategies import PassiveStrategy
from src.world_map import Position
from src.model import Model


class TestSaves(unittest.TestCase):
    def setUp(self):
        self.controller = Controller(_test_args=[])

    def testSaveActuallySaves(self):
        pass

    def testSaveSavesOnlyOnce(self):
        pass

    def testPlayerDeathForbidsSaves(self):
        pass


if __name__ == '__main__':
    unittest.main()
