""" Module containing the main controller logic for the server-based version of the game. """

import queue
import random
import secrets

import src.fighter
import src.roguelike_pb2
import src.roguelike_pb2_grpc
import src.strategies
import src.model
from src.fighting_system import CoolFightingSystem
from src.weapon import WeaponBuilder
from src.world_map import FileWorldMapSource, RandomV1WorldMapSource


class Subscriber:
    """ Class that stores players that have subscribed to the current game. """

    def __init__(self, subscriber_id, room, player):
        """ Creates a new subscriber from the given player in the given room. """
        self.id = subscriber_id
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
        player = src.fighter.Player(position, [
            WeaponBuilder()
            .with_name('SABER')
            .with_attack(2)
            .with_defence(2)
            .with_confusion_prob(0.2),
            WeaponBuilder()
            .with_name('SPEAR')
            .with_attack(4)
            .with_defence(1)
            .with_confusion_prob(0.1),
            WeaponBuilder()
            .with_name('SWORD')
            .with_attack(1)
            .with_defence(3)
            .with_confusion_prob(0.7)])
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
        for player in model.players:
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
        self.rooms[room_name] = Room(src.model.FullModel(game_map, [], mobs), CoolFightingSystem())

    def generate_id(self):
        return secrets.token_hex(16)

    def subscribe(self, room_name):
        """ Creates a player in the given room, subscribes them to the game, returns an unique player id. """
        if room_name not in self.rooms:
            self.create_new_room(room_name)

        room = self.get_room(room_name)
        player = room.spawn_player()

        subscriber_id = self.generate_id()  # str(len(self.subscribers))
        subscriber = Subscriber(subscriber_id, room_name, player)
        room.subscribers[subscriber_id] = subscriber
        self.subscribers_rooms[subscriber_id] = room_name
        return subscriber_id

    def unsubscribe(self, subscriber_id):
        room = self.get_room_by_id(subscriber_id)
        if subscriber_id in room.room.subscribers:
            del room.subscribers[subscriber_id]

    def get_room_by_id(self, subscriber_id):
        return self.rooms[self.subscribers_rooms[subscriber_id]]

    def get_room(self, room_name):
        return self.rooms[room_name]

    def get_subscriber(self, subscriber_id):
        """ Returns the subscriber with the given id or None if none exists. """
        room = self.get_room_by_id(subscriber_id)
        return room.subscribers[subscriber_id]

    def get_model(self, room_name):
        """ Returns the room with the given name or None if none exists. """
        room = self.get_room(room_name)
        return room.model

    def get_queue(self, subscriber_id):
        """ Returns the queue for the subscriber with the given id or None if the subscriber does
        not exist. """
        return self.get_subscriber(subscriber_id).queue


class Servicer(src.roguelike_pb2_grpc.GameServicer):
    """ Class that implements the interface of the Game service. """

    def __init__(self):
        """ Creates a Servicer with an empty RoomManager. """
        self.room_manager = RoomManager()

    def Join(self, request, context):
        """ Processes the joining of a player to the game. """
        subscriber_id = self.room_manager.subscribe(request.room)
        yield src.roguelike_pb2.Id(id=subscriber_id)

        while self.room_manager.get_queue(subscriber_id).get():
            if self.room_manager.get_subscriber(subscriber_id).player.hp <= 0:
                self.room_manager.unsubscribe(subscriber_id)
                yield src.roguelike_pb2.Id(id='dead')
                return
            yield src.roguelike_pb2.Id(id=subscriber_id)

    def _check_intentions(self, room):
        if room.intentions_got == len(room.subscribers):
            room._tick()
            for subscriber in room.subscribers.values():
                subscriber.queue.put('Ping')

    def Disconnect(self, request, context):
        subscriber_id = request.id
        room = self.room_manager.get_room_by_id(subscriber_id)
        self.room_manager.unsubscribe(subscriber_id)
        self._check_intentions(room)

    def GetMap(self, request, context):
        """ Returns the game map for the game of the subscriber issuing the request. """
        subscriber_id = request.id
        subscriber = self.room_manager.get_subscriber(subscriber_id)
        game_map = self.room_manager.get_model(subscriber.room).map

        return src.roguelike_pb2.Map(
            data=[src.roguelike_pb2.Cell(isEmpty=game_map.is_empty(src.world_map.Position(i, j)))
                  for i in range(game_map.height)
                  for j in range(game_map.width)],
            height=game_map.height, width=game_map.width)

    def GetPlayer(self, request, context):
        """ Returns the player character for the game of the subscriber issuing the request. """
        subscriber_id = request.id
        subscriber = self.room_manager.get_subscriber(subscriber_id)
        player = src.roguelike_pb2.Player(
            position=src.roguelike_pb2.Position(x=subscriber.player.position.x,
                                                y=subscriber.player.position.y),
            hp=subscriber.player.hp)
        return player

    def GetMobs(self, request, context):
        """ Returns the mob list for the game of the subscriber issuing the request. """
        subscriber_id = request.id
        subscriber = self.room_manager.get_subscriber(subscriber_id)
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
        subscriber_id = request.id.id
        subscriber = self.room_manager.get_subscriber(subscriber_id)
        player = subscriber.player
        moves = {
            0: 'stay',
            1: 'go_up',
            2: 'go_left',
            3: 'go_down',
            4: 'go_right',
        }
        player.get_commands()[moves[request.moveId]]()
        weapons = {
            0: 'select_0',
            1: 'select_1',
            2: 'select_2',
            3: 'select_3',
        }
        player.get_commands()[weapons[0]]()
        player.get_commands()[weapons[request.weaponId]]()

        room = self.room_manager.get_room_by_id(subscriber_id)
        room.intentions_got += 1

        self._check_intentions(room)

        return src.roguelike_pb2.Empty()
