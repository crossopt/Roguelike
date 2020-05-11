""" Module containing the main controller logic for the game. """

import os
import random
from argparse import ArgumentParser

import tcod
import tcod.event

import time
import threading, queue

import src.fighter
import src.strategies
from src import model
from src import view
from src.fighting_system import CoolFightingSystem
from src.view import TOTAL_WIDTH, TOTAL_HEIGHT
from src.weapon import WeaponBuilder
from src.world_map import FileWorldMapSource, RandomV1WorldMapSource

from concurrent import futures
import grpc
import src.roguelike_pb2
import src.roguelike_pb2_grpc

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
        self.rooms[room] = model.Model(game_map, [], mobs)

    def spawn_player(self, model):
        position = model.map.get_random_empty_positions(1)[0]
        player = src.fighter.Player(position)
        model.players.add(position)
        return player

    def subscribe(self, room):
        if room not in self.rooms:
            self.create_new_room(room)

        player = self.spawn_player(self.rooms[room])

        id = len(subscribers) - 1
        self.subcribers[id] = Subscriber(id, room, player)
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
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        src.roguelike_pb2_grpc.add_GameServicer_to_server(
            src.roguelike_pb2_grpc.GameServicer(), self.server)
        self.server.add_insecure_port('[::]:50051')


        

    def start(self):
        self.server.start()
        while True:
            time.sleep(1)

    def tick(self):
        self.intentions_got = 0
        pass

    def Join(self, request, context):
        self.room_manager.subscribe(request.room)

        while self.room_manager.get_queue(id).get():
            yield src.roguelike_pb2.Id(id)

    def GetMap(self, request, context):
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        game_map = self.room_manager.get_room(subscriber.room).map

        return src.roguelike_pb2.Map(
                [src.roguelike_pb2.Cell(game_map.is_empty(world_map.Position(i, j))) for j in game_map.width for i in game_map.height],
                game_map.height, game_map.width)

    def GetPlayer(self, request, context):
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        player = src.roguelike_pb2.Player(
            src.roguelike_pb2.Position(subscriber.player.position.x, subscriber.player.position.y),
            subscriber.player.hp)
        return player

    def GetMobs(self, request, context):
        id = request.id
        subscriber = self.room_manager.get_subscriber(id)
        model = self.room_manager.get_room(subscriber.room)
        mobs = model.mobs + [player for player in model.players if player != subscriber.player]
        result = src.roguelike_pb2.Mobs(
                 [src.roguelike_pb2.Mob(
                     src.roguelike_pb2.Position(mob.position.x, mob.position.y),
                     mob.get_style(),
                     mob.get_intensity()
                 )]
        )
        return result 

    def SendIntention(self, request, context):
        id = request.id
        player = self.room_manager.get_subscriber(id).player
        moves = {
            0: "stay",
            1: "go_left",
            2: "go_down",
            3: "go_right",
            4: "go_up",
        }
        player.get_commands()[moves[request.moveId]]()
        self.intentions_got += 1

        if self.intentions_got == self.subscribed:
            self.tick()

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
