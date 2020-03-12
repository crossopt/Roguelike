import unittest

from src.world_map import MapTile, WorldMap


class TestMapTile(unittest.TestCase):
    def testCharParsing_correctChars(self):
        self.assertEqual(MapTile.EMPTY, MapTile.parse('.'))
        self.assertEqual(MapTile.BLOCKED, MapTile.parse('X'))

    def testCharParsing_invalidChars(self):
        self.assertEqual(MapTile.INVALID, MapTile.parse(''))
        self.assertEqual(MapTile.INVALID, MapTile.parse('..'))
        self.assertEqual(MapTile.INVALID, MapTile.parse('@'))


class TestWorldMap(unittest.TestCase):
    def setUp(self):
        self.no_block_map = [[MapTile.EMPTY for i in range(1)] for j in range(2)]
        self.all_block_map = [[MapTile.BLOCKED for i in range(3)] for j in range(5)]
        self.almost_all_block_map = [[MapTile.EMPTY if i == j == 1 else MapTile.BLOCKED for i in range(5)] for j in range(2)]
        self.disconnected_map = [[MapTile.EMPTY if i != j else MapTile.BLOCKED for i in range(3)] for j in range(4)]
        self.valid_map = [[MapTile.EMPTY if abs(i - j) < 2 else MapTile.BLOCKED for i in range(3)] for j in range(3)]

    def testTrimLines_empty(self):
        self.assertListEqual([], WorldMap._trim_lines(['\n']))

    def testTrimLines_valid(self):
        self.assertListEqual(['..', 'X.'], WorldMap._trim_lines([' ..\n', '', 'X.\n\n\n']))

    def testConvertLines(self):
        pass

    def testComponentChecking_oneComponent(self):
        self.assertTrue(WorldMap._is_one_component(self.no_block_map))
        self.assertTrue(WorldMap._is_one_component(self.valid_map))
        self.assertTrue(WorldMap._is_one_component(self.almost_all_block_map))

    def testComponentChecking_notOneComponent(self):
        self.assertFalse(WorldMap._is_one_component(self.disconnected_map))
        self.assertFalse(WorldMap._is_one_component(self.all_block_map))

    def testGenerate(self):
        pass

    def testLoad(self):
        pass


if __name__ == '__main__':
    unittest.main()
