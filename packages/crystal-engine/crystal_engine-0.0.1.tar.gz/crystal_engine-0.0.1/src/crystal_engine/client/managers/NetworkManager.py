import pickle
from crystal_engine.client.managers.Manager import Manager

import socket

from crystal_engine.client.util.GameNetworkingObject import GameNetworkingObject

class NetworkManager(Manager):
    def __init__(self, game) -> None:
        super().__init__(game)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected_to_server = False

        self.network_id = -1

        self.connections = []

        setattr(self, "GameNetworkingObject", GameNetworkingObject())

    def connect_to_server(self, server_ip, server_port):
        try:
            self.client.connect((server_ip, server_port))

            self.connected_to_server = True
        except ConnectionRefusedError as e:
            self.connected_to_server = False
            
            print("couldn't connect to server")

    def loop(self, screen, *args):
        try:
            if self.connected_to_server:
                self.client.send(pickle.dumps(self.GameNetworkingObject))
                self.connections = pickle.loads(self.client.recv(1024))
        except OSError as e:
            str(e)