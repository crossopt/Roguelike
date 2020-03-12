import unittest

from src.world_map import MapTile, WorldMap, MapParsingException, Position


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
        self.one_tile_map = [[MapTile.EMPTY if i == j == 1 else MapTile.BLOCKED for i in range(5)] for j in range(2)]
        self.disconnected_map = [[MapTile.EMPTY if i != j else MapTile.BLOCKED for i in range(3)] for j in range(4)]
        self.valid_map = [[MapTile.EMPTY if abs(i - j) < 2 else MapTile.BLOCKED for i in range(3)] for j in range(3)]

    def testTrimLines_empty(self):
        self.assertListEqual([], WorldMap._trim_lines(['\n']))

    def testTrimLines_valid(self):
        self.assertListEqual(['..', 'X.'], WorldMap._trim_lines([' ..\n', '', 'X.\n\n\n']))

    def testConvertLines_invalidHeight(self):
        with self.assertRaises(MapParsingException) as raised:
            WorldMap._convert_to_tiles([])
        self.assertEqual('Invalid map height', str(raised.exception))

    def testConvertLines_invalidWidth(self):
        with self.assertRaises(MapParsingException) as raised:
            WorldMap._convert_to_tiles(['..', '.', 'X.'])
        self.assertEqual('Line does not match width: .', str(raised.exception))

    def testConvertLines_severalComponents(self):
        with self.assertRaises(MapParsingException) as raised:
            WorldMap._convert_to_tiles(['XX'])
        self.assertEqual('Map is not a connected component', str(raised.exception))

    def testConvertLines_badSymbol(self):
        with self.assertRaises(MapParsingException) as raised:
            WorldMap._convert_to_tiles(['.', '.', '.', '@', '.'])
        self.assertEqual('Invalid symbol @ in line @', str(raised.exception))

    def testConvertLines_correctBoard(self):
        self.assertListEqual(self.no_block_map, WorldMap._convert_to_tiles(['.', '.']))
        self.assertListEqual(self.one_tile_map, WorldMap._convert_to_tiles(['XXXXX', 'X.XXX']))
        self.assertListEqual(self.valid_map, WorldMap._convert_to_tiles(['..X', '...', 'X..']))

    def testComponentChecking_oneComponent(self):
        self.assertTrue(WorldMap._is_one_component(self.no_block_map))
        self.assertTrue(WorldMap._is_one_component(self.valid_map))
        self.assertTrue(WorldMap._is_one_component(self.one_tile_map))

    def testComponentChecking_notOneComponent(self):
        self.assertFalse(WorldMap._is_one_component(self.disconnected_map))
        self.assertFalse(WorldMap._is_one_component(self.all_block_map))

    def testGenerate_invalidParameters(self):
        with self.assertRaises(ValueError) as raised:
            WorldMap().generate(-1, 2)
        self.assertEqual('Invalid map height', str(raised.exception))

        with self.assertRaises(ValueError) as raised:
            WorldMap().generate(3, 0)
        self.assertEqual('Invalid map width', str(raised.exception))

    def testGenerate_smallParameters(self):
        world_map = WorldMap()
        world_map.generate(1, 1)
        self.assertEqual(world_map.tiles, [[MapTile.EMPTY]])

    def testGenerate_normalParameters(self):
        world_map = WorldMap()
        world_map.generate(10, 10)
        self.assertTrue(WorldMap._is_one_component(world_map.tiles))

    def testLoad_nonexistentFile(self):
        with self.assertRaises(MapParsingException) as raised:
            WorldMap().load('not_a_file')

    def testLoad_badBoard(self):
        with self.assertRaises(MapParsingException) as raised:
            WorldMap().load('test/resources/invalid_board')
        self.assertEqual('Line does not match width: ..', str(raised.exception))

    def testLoad_correctBoard(self):
        world_map = WorldMap()
        world_map.load('test/resources/valid_board')
        self.assertListEqual(self.valid_map, world_map.tiles)

    def testIsOnMap(self):
        world_map = WorldMap()
        self.assertTrue(world_map.is_on_map(Position(5, 5)))
        self.assertFalse(world_map.is_on_map(Position(-1, 0)))
        self.assertTrue(world_map.is_on_map(Position(10, 0)))
        world_map.generate(4, 6)
        self.assertFalse(world_map.is_on_map(Position(5, 5)))
        self.assertTrue(world_map.is_on_map(Position(3, 5)))
        self.assertFalse(world_map.is_on_map(Position(5, 3)))

    def testGetPlayerStart_startInZero(self):
        mocked_map = WorldMap()
        mocked_map.generate(2, 1)
        mocked_map.tiles = self.no_block_map
        self.assertEqual(0, mocked_map.get_player_start().x)
        self.assertEqual(0, mocked_map.get_player_start().y)

    def testGetPlayerStart_startNotInZero(self):
        mocked_map = WorldMap()
        mocked_map.generate(2, 5)
        mocked_map.tiles = self.one_tile_map
        self.assertEqual(1, mocked_map.get_player_start().x)
        self.assertEqual(1, mocked_map.get_player_start().y)

    def testGetPlayerStart_nonexistentStart(self):
        mocked_map = WorldMap()
        mocked_map.generate(5, 3)
        mocked_map.tiles = self.all_block_map
        self.assertIsNone(mocked_map.get_player_start())


if __name__ == '__main__':
    unittest.main()
