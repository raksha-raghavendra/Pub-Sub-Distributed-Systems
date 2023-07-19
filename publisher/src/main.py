import json
import string
import sys
import time

from src.constants import BUFF_SIZE, DEFAULT_ID, Type
import socket


class Publisher:

    def __init__(self, verbose: bool, config_path: str):

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.port_leader = config["leader"]["port"]
        self.ip_leader = config["leader"]["ip"]
        self.ip = config["publisher"]["ip"]
        self.port = config["publisher"]["port"]
        self.verbose = verbose

    def start(self):

        # send a message to the leader about the port
        # that the publisher is publishing to and the
        # topics that it is interested in
        msg = {
            "client_type": "publisher",
            "ip": self.ip,
            "port": self.port
        }

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(None)
        address = (self.ip_leader, self.port_leader)

        try:
            server_socket.connect(address)
            server_socket.send(json.dumps(msg).encode('utf-8'))
            server_socket.close()

            self.publish_data()
        except BaseException as e:
            print("Server node not available", e)

    def publish_data(self):

        # wait for server to listen to the publisher socket
        time.sleep(2)

        publisher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        publisher_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        publisher_socket.settimeout(None)
        address = (self.ip, self.port)

        try:
            publisher_socket.connect(address)
            while True:
                user_input = input("Enter job posting : ")

                # Display the user input
                print("You entered:", user_input)

                encoded_data = str(user_input).encode('utf-8')
                publisher_socket.send(encoded_data)
                print(f"{encoded_data} data sent!")

        except BaseException as e:
            print("Publisher node not available", e)