""" Module containing the main controller logic for the game. """

import queue
import random

import src.fighter
import src.roguelike_pb2
import src.roguelike_pb2_grpc
import src.strategies
from src import model
from src.fighting_system import CoolFightingSystem
from src.world_map import FileWorldMapSource, RandomV1WorldMapSource

SAVE_FILE_NAME = 'save'


class Subscriber():
    def __init__(self, id, room, player):
        self.id = id
        self.room = room
        self.player = player
        self.subscribed = True
        self.queue = queue.Queue()


class RoomManager():
    def __init__(self):
        self.subscribers = {}
        self.rooms = {}
        self.subscribed = 0

    def create_new_room(self, room):
        _DEFAULT_MAP_WIDTH = 30
        _DEFAULT_MAP_HEIGHT = 30
        _MOB_COUNT = 8
        game_map = RandomV1WorldMapSource(_DEFAULT_MAP_HEIGHT,
                                          _DEFAULT_MAP_WIDTH).get()

        positions = game_map.get_random_empty_positions(_MOB_COUNT)
        mobs = [src.fighter.Mob(positions[i], random.choice([
                            src.strategies.AggressiveStrategy(),
                            src.strategies.PassiveStrategy(),
                            src.strategies.CowardlyStrategy()])) for i in range(0, _MOB_COUNT)]
        self.rooms[room] = model.FullModel(game_map, [], mobs)

    def spawn_player(self, model):
        position = model.map.get_random_empty_positions(1)[0]
        player = src.fighter.Player(position)
        model.players.add(position)
        return player

    def subscribe(self, room):
        if room not in self.rooms:
            self.create_new_room(room)

        player = self.spawn_player(self.rooms[room])

        id = len(self.subscribers)
        self.subscribers[id] = Subscriber(id, room, player)
        self.subscribed += 1
        return str(id)

    def get_subscriber(self, subscriber):
        return self.subscribers.get(subscriber, None)

    def get_room(self, room):
        return self.rooms.get(room, None)

    def get_queue(self, id):
        if id in self.subscribers:
            return self.subscribers[id].queue
        return None


class Servicer(src.roguelike_pb2_grpc.GameServicer):
    def __init__(self):
        self.room_manager = RoomManager()
        self.fighting_system = CoolFightingSystem()

    def tick(self, model):
        self.intentions_got = 0

        game_map = model.map
        fighters = model.get_fighters()

        random.shuffle(fighters)

        for fighter in fighters:
            intended_position = fighter.choose_move(model)
            if not game_map.is_empty(intended_position):
                intended_position = fighter.position
            target = model.get_fighter_at(intended_position)
            if target is not None and intended_position != fighter.position:
                self.fighting_system.fight(fighter, target)
            if target is None:
                fighter.position = intended_position

        players = []
        for player in model.mobs:
            if player.hp > 0:
                players.append(player)
        model.players = players

        mobs = []
        for mob in model.mobs:
            if mob.hp > 0:
                mobs.append(mob)
        model.mobs = mobs

    def Join(self, request, context):
        id = self.room_manager.subscribe(request.room)
        yield src.roguelike_pb2.Id(id=id)

        while self.room_manager.get_queue(id).get():
            if self.room_manager.get_subscriber(id).player.hp <= 0:
                yield src.roguelike_pb2.Id(id='dead')
                return
            yield src.roguelike_pb2.Id(id=id)

    def GetMap(self, request, context):
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        game_map = self.room_manager.get_room(subscriber.room).map

        return src.roguelike_pb2.Map(
                data=[src.roguelike_pb2.Cell(isEmpty=game_map.is_empty(src.world_map.Position(i, j))) for j in game_map.width for i in game_map.height],
                height=game_map.height, width=game_map.width)

    def GetPlayer(self, request, context):
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        player = src.roguelike_pb2.Player(
            position=src.roguelike_pb2.Position(x=subscriber.player.position.x, y=subscriber.player.position.y),
            hp=subscriber.player.hp)
        return player

    def GetMobs(self, request, context):
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        model = self.room_manager.get_room(subscriber.room)
        mobs = model.mobs + [player for player in model.players if player != subscriber.player]
        result = src.roguelike_pb2.Mobs(
                 data=[src.roguelike_pb2.Mob(
                     position=src.roguelike_pb2.Position(mob.position.x, mob.position.y),
                     style=mob.get_style(),
                     intensity=mob.get_intensity()
                 ) for mob in mobs]
        )
        return result 

    def SendIntention(self, request, context):
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        player = subscriber.player
        moves = {
            0: 'stay',
            1: 'go_up',
            2: 'go_left',
            3: 'go_down',
            4: 'go_right',
        }
        player.get_commands()[moves[request.moveId]]()
        self.intentions_got += 1

        if self.intentions_got == self.room_manager.subscribed:
            self.tick(self.room_manager.get_room(subscriber.room))
            for subscriber in self.room_manager.subscribers.values():
                subscriber.queue.put('Ping')

        return src.roguelike_pb2.Empty()


# class Controller():
#     """ The class responsible for controlling the main game flow. """
#     _DEFAULT_MAP_WIDTH = 30
#     _DEFAULT_MAP_HEIGHT = 30
#     _MOB_COUNT = 8

#     _TILESET_PATH = 'fonts/medium_font.png'
#     _TILESET_OPTIONS = tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE
#     _TILESET_HORIZONTAL = 16
#     _TILESET_VERTICAL = 16

#     def __init__(self):
#         """ Initializes the game controller so it is ready to start a new game. """
#         # game_map = RandomV1WorldMapSource(Controller._DEFAULT_MAP_HEIGHT,
#         #                                   Controller._DEFAULT_MAP_WIDTH).get()

#         # mobs_count = Controller._MOB_COUNT
#         # positions = game_map.get_random_empty_positions(mobs_count)
#         # mobs = [src.fighter.Mob(positions[i], random.choice([
#         #                     src.strategies.AggressiveStrategy(),
#         #                     src.strategies.PassiveStrategy(),
#         #                     src.strategies.CowardlyStrategy()])) for i in range(0, mobs_count)]

#         # self.model = model.Model(game_map, mobs)

#         self.fighting_system = CoolFightingSystem()
#         self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#         src.roguelike_pb2_grpc.add_GameServicer_to_server(
#             src.roguelike_pb2_grpc.GameServicer(), self.server)
#         self.server.add_insecure_port('[::]:50051')
#         self.server.start()

#         while True:
#             time.sleep(1)





#     @staticmethod
#     def _wait_for_any_key():
#         for _ in tcod.event.wait():
#             pass
#         while True:
#             for event in tcod.event.wait():
#                 if event.type in ['QUIT', 'KEYDOWN']:
#                     return

#     def _tick(self):
#         game_map = self.model.map
#         fighters = self.model.get_fighters()

#         random.shuffle(fighters)

#         for fighter in fighters:
#             intended_position = fighter.choose_move(self.model)
#             if not game_map.is_empty(intended_position):
#                 intended_position = fighter.position
#             target = self.model.get_fighter_at(intended_position)
#             if target is not None and intended_position != fighter.position:
#                 self.fighting_system.fight(fighter, target)
#             if target is None:
#                 fighter.position = intended_position

#         if self.model.player.hp <= 0:
#             self.program_is_running = False
#             self.player_died = True
#         mobs = []
#         for mob in self.model.mobs:
#             if mob.hp > 0:
#                 mobs.append(mob)
#         self.model.mobs = mobs

#     @staticmethod
#     def _dispatch(code, _mod, commands):
#         """ Handles the user's key down presses and sets the relevant intentions for a player.

#         :param code: a scancode of the main key pressed.
#         :param _mod: a modifier, a mask of the functional keys pressed with the main one.
#         :param commands: a list of commands to which the key presses match.
#         """
#         code_to_cmd = {tcod.event.SCANCODE_W: commands['go_up'],
#                        tcod.event.SCANCODE_A: commands['go_left'],
#                        tcod.event.SCANCODE_S: commands['go_down'],
#                        tcod.event.SCANCODE_D: commands['go_right'],
#                        tcod.event.SCANCODE_1: commands['select_1'],
#                        tcod.event.SCANCODE_2: commands['select_2'],
#                        tcod.event.SCANCODE_3: commands['select_3']}
#         if code in code_to_cmd:
#             code_to_cmd[code]()
