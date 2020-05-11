""" Module containing the main controller logic for the server-based version of the game. """

import queue
import random
import secrets

import src.fighter
import src.roguelike_pb2
import src.roguelike_pb2_grpc
import src.strategies
from src import model
from src.fighting_system import CoolFightingSystem
from src.world_map import FileWorldMapSource, RandomV1WorldMapSource

class Subscriber:
    """ Class that stores players that have subscribed to the current game. """
    def __init__(self, id, room, player):
        """ Creates a new subscriber from the given player in the given room. """
        self.id = id
        self.room = room
        self.player = player
        self.subscribed = True
        self.queue = queue.Queue()


class Room:

    def __init__(self, model, fighting_system):
        self.model = model
        self.intentions_got = 0
        self.fighting_system = fighting_system
        self.subscribers = {}


    def spawn_player(self):
        """ Creates a new player in a random position in the room. """
        model = self.model
        position = model.map.get_random_empty_positions(1)[0]
        player = src.fighter.Player(position)
        model.players.append(player)
        return player

    def _tick(self):
        self.intentions_got = 0

        model = self.model
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


class RoomManager:
    """ Class responsible for managing various rooms containing the players. """
    def __init__(self):
        """ Creates an RoomManager without any rooms. """
        self.subscribers_rooms = {}
        self.rooms = {}

    def create_new_room(self, room_name):
        """ Creates a new room with the given name to manage. """
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
        self.rooms[room_name] = Room(model.FullModel(game_map, [], mobs), CoolFightingSystem())

    def generate_id(self):
        return secrets.token_hex(16)

    def subscribe(self, room_name):
        """ Creates a player in the given room, subscribes them to the game, returns an unique player id. """
        if room_name not in self.rooms:
            self.create_new_room(room_name)

        room = self.get_room(room_name)
        player = room.spawn_player()

        id = self.generate_id() # str(len(self.subscribers))
        subscriber = Subscriber(id, room_name, player)
        room.subscribers[id] = subscriber
        self.subscribers_rooms[id] = room_name
        return id

    def get_room_by_id(self, id):
        return self.rooms[self.subscribers_rooms[id]]

    def get_room(self, room_name):
        return self.rooms[room_name]

    def get_subscriber(self, id):
        """ Returns the subscriber with the given id or None if none exists. """
        room = self.get_room_by_id(id)
        return room.subscribers[id]

    def get_model(self, room_name):
        """ Returns the room with the given name or None if none exists. """
        room = self.get_room(room_name)
        return room.model

    def get_queue(self, id):
        """ Returns the queue for the subscriber with the given id or None if the subscriber does not exist. """
        return self.get_subscriber(id).queue


class Servicer(src.roguelike_pb2_grpc.GameServicer):
    """ Class that implements the interface of the Game service. """
    def __init__(self):
        """ Creates a Servicer with an empty RoomManager. """
        self.room_manager = RoomManager()

    def Join(self, request, context):
        """ Processes the joining of a player to the game. """
        id = self.room_manager.subscribe(request.room)
        yield src.roguelike_pb2.Id(id=id)

        while self.room_manager.get_queue(id).get():
            if self.room_manager.get_subscriber(id).player.hp <= 0:
                yield src.roguelike_pb2.Id(id='dead')
                return
            yield src.roguelike_pb2.Id(id=id)

    def GetMap(self, request, context):
        """ Returns the game map for the game of the subscriber issuing the request. """
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        game_map = self.room_manager.get_model(subscriber.room).map

        return src.roguelike_pb2.Map(
                data=[src.roguelike_pb2.Cell(isEmpty=game_map.is_empty(src.world_map.Position(i, j)))
                for j in range(game_map.width)
                for i in range(game_map.height)],
                height=game_map.height, width=game_map.width)

    def GetPlayer(self, request, context):
        """ Returns the player character for the game of the subscriber issuing the request. """
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        player = src.roguelike_pb2.Player(
            position=src.roguelike_pb2.Position(x=subscriber.player.position.x, y=subscriber.player.position.y),
            hp=subscriber.player.hp)
        return player

    def GetMobs(self, request, context):
        """ Returns the mob list for the game of the subscriber issuing the request. """
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        model = self.room_manager.get_model(subscriber.room)
        mobs = model.mobs + [player for player in model.players if player != subscriber.player]
        result = src.roguelike_pb2.Mobs(
                 data=[src.roguelike_pb2.Mob(
                     position=src.roguelike_pb2.Position(x=mob.position.x, y=mob.position.y),
                     style=mob.get_style(),
                     intensity=mob.get_intensity()
                 ) for mob in mobs]
        )
        return result 

    def SendIntention(self, request, context):
        """ Sends a move that the subscriber issuing the request wants his player to do. """
        id = request.id.id
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

        room = self.room_manager.get_room_by_id(id)
        room.intentions_got += 1

        if room.intentions_got == len(room.subscribers):
            room._tick()
            for subscriber in room.subscribers.values():
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
