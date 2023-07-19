import json
import string
import sys
from threading import Thread
from src.constants import BUFF_SIZE, DEFAULT_ID, Type
import socket


class Subscriber:
    def __init__(self, verbose: bool, config_path: str):

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port_leader = config["leader"]["port"]
        self.ip_leader = config["leader"]["ip"]
        self.ip = config["subscriber"]["ip"]
        self.port = config["subscriber"]["port"]
        self.topics = config["subscriber"]["topics"]
        self.verbose = verbose

    def start(self):

        # listen to own port
        thread = Thread(target=self.connect_with_server)
        thread.daemon = True
        thread.start()

        self.listen_to_port()

    def connect_with_server(self):
        # send a message to the leader about the port
        # that the subscriber is listening to and the
        # topics that it is interested in
        msg = {
            "client_type": "subscriber",
            "ip": self.ip,
            "port": self.port,
            "topics": self.topics
        }

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(None)
        address = (self.ip_leader, self.port_leader)

        try:
            server_socket.connect(address)
            server_socket.send(json.dumps(msg).encode('utf-8'))
            print("Connection request sent to the leader")
        except BaseException as e:
            print("Server node not available", e)

        server_socket.close()
        print("Connection with the leader established")

    def listen_to_port(self):
        subscriber_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        subscriber_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        address = (self.ip, self.port)
        print("Creating subscriber socket.")
        try:
            subscriber_socket.bind(address)
            subscriber_socket.listen(5)
            # print(f"Listening to address {address}")
            print(f"This subscriber is now Listening to address")

            conn, addr = subscriber_socket.accept()
            print("Received connection.")

            while True:
                data = conn.recv(BUFF_SIZE)
                if data != '':
                    msg = data.decode('utf-8')
                    print(f"\nReceived data: {msg}\n")

        except BaseException as e:
            print("Subscriber node not available", e)
            sys.exit(1)
