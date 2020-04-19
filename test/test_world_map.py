import unittest

from src.world_map import MapTile, WorldMap, MapParsingException, Position, \
    FileWorldMapSource, RandomV1WorldMapSource


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
        self.no_block_map = [[MapTile.EMPTY for _ in range(1)] for _ in range(2)]
        self.all_block_map = [[MapTile.BLOCKED for _ in range(3)] for _ in range(5)]
        self.one_tile_map = [[MapTile.EMPTY if i == j == 1 else MapTile.BLOCKED for i in range(5)] for j in range(2)]
        self.disconnected_map = [[MapTile.EMPTY if i != j else MapTile.BLOCKED for i in range(3)] for j in range(4)]
        self.valid_map = [[MapTile.EMPTY if abs(i - j) < 2 else MapTile.BLOCKED for i in range(3)] for j in range(3)]

    def testComponentChecking_oneComponent(self):
        self.assertTrue(WorldMap.from_tiles(self.no_block_map).is_one_component())
        self.assertTrue(WorldMap.from_tiles(self.valid_map).is_one_component())
        self.assertTrue(WorldMap.from_tiles(self.one_tile_map).is_one_component())

    def testComponentChecking_notOneComponent(self):
        self.assertFalse(WorldMap.from_tiles(self.disconnected_map).is_one_component())
        self.assertFalse(WorldMap.from_tiles(self.all_block_map).is_one_component())

    def testIsOnMap(self):
        world_map = WorldMap()
        self.assertTrue(world_map.is_on_map(Position(5, 5)))
        self.assertFalse(world_map.is_on_map(Position(-1, 0)))
        self.assertFalse(world_map.is_on_map(Position(10, 0)))

    def testRandomEmptyPositions(self):
        world_map = WorldMap.from_tiles(self.one_tile_map)
        positions = world_map.get_random_empty_positions(5)
        self.assertEqual(5, len(positions))
        for position in positions:
            self.assertEqual(position, Position(1, 1))

    def testIsEmpty(self):
        world_map = WorldMap.from_tiles(self.valid_map)
        self.assertFalse(world_map.is_empty(Position(-1, 0)))
        self.assertFalse(world_map.is_empty(Position(2, 0)))
        self.assertFalse(world_map.is_empty(Position(0, 2)))
        self.assertTrue(world_map.is_empty(Position(1, 0)))
        self.assertTrue(world_map.is_empty(Position(1, 1)))

    def testGetDistance(self):
        self.assertEqual(0, WorldMap.get_distance(Position(3, 3), Position(3, 3)))
        self.assertEqual(27, WorldMap.get_distance(Position(3, 3), Position(3, 30)))
        self.assertEqual(10, WorldMap.get_distance(Position(3, 3), Position(10, 0)))

    def testGetEmptyNeighbors(self):
        world_map = WorldMap.from_tiles(self.valid_map)
        self.assertEqual(world_map.get_empty_neighbors(Position(0, 0)),
                         [Position(0, 1), Position(1, 0)])
        self.assertEqual(world_map.get_empty_neighbors(Position(1, 0)),
                         [Position(1, 1), Position(0, 0)])


class TestRandomV1WorldMapSource(unittest.TestCase):
    def testGenerate_invalidParameters(self):
        with self.assertRaises(ValueError) as raised:
            RandomV1WorldMapSource(-1, 2).get()
        self.assertEqual('Invalid map height', str(raised.exception))

        with self.assertRaises(ValueError) as raised:
            RandomV1WorldMapSource(3, 0).get()
        self.assertEqual('Invalid map width', str(raised.exception))

    def testGenerate_smallParameters(self):
        world_map = RandomV1WorldMapSource(1, 1).get()
        self.assertEqual(world_map.tiles, [[MapTile.EMPTY]])

    def testGenerate_normalParameters(self):
        world_map = RandomV1WorldMapSource(10, 10).get()
        self.assertTrue(world_map.is_one_component())


class TestFileWorldMapSource(unittest.TestCase):
    def setUp(self):
        self.no_block_map = [[MapTile.EMPTY for _ in range(1)] for _ in range(2)]
        self.all_block_map = [[MapTile.BLOCKED for _ in range(3)] for _ in range(5)]
        self.one_tile_map = [[MapTile.EMPTY if i == j == 1 else MapTile.BLOCKED for i in range(5)] for j in range(2)]
        self.disconnected_map = [[MapTile.EMPTY if i != j else MapTile.BLOCKED for i in range(3)] for j in range(4)]
        self.valid_map = [[MapTile.EMPTY if abs(i - j) < 2 else MapTile.BLOCKED for i in range(3)] for j in range(3)]

    def testTrimLines_empty(self):
        self.assertListEqual([], FileWorldMapSource._trim_lines(['\n']))

    def testTrimLines_valid(self):
        self.assertListEqual(['..', 'X.'], FileWorldMapSource._trim_lines([' ..\n', '', 'X.\n\n\n']))

    def testConvertLines_invalidHeight(self):
        with self.assertRaises(MapParsingException) as raised:
            FileWorldMapSource._convert_to_tiles([])
        self.assertEqual('Invalid map height', str(raised.exception))

    def testConvertLines_invalidWidth(self):
        with self.assertRaises(MapParsingException) as raised:
            FileWorldMapSource._convert_to_tiles(['..', '.', 'X.'])
        self.assertEqual('Line does not match width: .', str(raised.exception))

    def testConvertLines_severalComponents(self):
        with self.assertRaises(MapParsingException) as raised:
            FileWorldMapSource('test/resources/disconnected_board').get()
        self.assertEqual('Map is not a connected component', str(raised.exception))

    def testConvertLines_badSymbol(self):
        with self.assertRaises(MapParsingException) as raised:
            FileWorldMapSource._convert_to_tiles(['.', '.', '.', '@', '.'])
        self.assertEqual('Invalid symbol @ in line @', str(raised.exception))

    def testConvertLines_correctBoard(self):
        self.assertListEqual(self.no_block_map, FileWorldMapSource._convert_to_tiles(['.', '.']))
        self.assertListEqual(self.one_tile_map, FileWorldMapSource._convert_to_tiles(['XXXXX', 'X.XXX']))
        self.assertListEqual(self.valid_map, FileWorldMapSource._convert_to_tiles(['..X', '...', 'X..']))

    def testLoad_nonexistentFile(self):
        with self.assertRaises(MapParsingException):
            FileWorldMapSource('not_a_file').get()

    def testLoad_badBoard(self):
        with self.assertRaises(MapParsingException) as raised:
            FileWorldMapSource('test/resources/invalid_board').get()
        self.assertEqual('Line does not match width: ..', str(raised.exception))

    def testLoad_correctBoard(self):
        world_map = FileWorldMapSource('test/resources/valid_board').get()
        self.assertListEqual(self.valid_map, world_map.tiles)


if __name__ == '__main__':
    unittest.main()
