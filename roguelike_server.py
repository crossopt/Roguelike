#!/usr/bin/env python3
from concurrent import futures

import grpc
import src.roguelike_pb2_grpc
from src.server_controller import Servicer

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
src.roguelike_pb2_grpc.add_GameServicer_to_server(
    Servicer(), server)
server.add_insecure_port('[::]:50051')
server.start()
server.wait_for_termination()
