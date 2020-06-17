#!/usr/bin/env python3
from argparse import ArgumentParser

from src.client_controller import OfflineController, ClientController

parser = ArgumentParser(description='A simple console-based rogue-like game.')
parser.add_argument('--map_path', type=str, help='path to map file to load')
parser.add_argument('--new_game', dest='new_game_demanded', action='store_true')
parser.add_argument('--address', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=50051)
parser.add_argument('--connect', action='store_true')
parser.add_argument('--room', type=str, default='')
args = parser.parse_args()

if args.connect:
    ClientController(args).run_loop()
else:
    OfflineController(args).run_loop()
