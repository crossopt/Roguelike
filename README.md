# Roguelike
A simple console-based rogue-like game.

Requirements: python 3.7+, [tcod](https://pypi.org/project/tcod/ "tcod") library, grpc.

## Server

To run server `./roguelike_server.py` should be used.

## Client

To run client `./roguelike.py` should be used.

Possible arguments are:

In single player mode:
* `--map_path path` -- path to map file to load
* `--new_game` -- in case you want to delete savegame and start new

When connecting to a server:
* `--address` -- server adress (default `localhost`)
* `--port` -- server port (default `50051` )
* `--connect` -- pass this to play multiplayer mode
* `--room` -- room name to join on the server (default empty)
