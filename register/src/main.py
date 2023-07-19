import socket
import json
from . import constants as const
from . import helpers as help
import signal
import sys


class Register:
    def __init__(self, verbose: bool, config_path: str):

        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        self.my_ip = config["register"]["ip"]
        self.my_port = config["register"]["port"]

        self.nodes = []
        self.verbose = verbose
        self.logging = help.set_logging()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.my_ip, self.my_port))
        self.connections = []

        signal.signal(signal.SIGINT, self.handler_log_msgs)

    def receive(self):

        self.sock.listen()

        ids = []
        self.sock.settimeout(const.SOCKET_TIMEOUT)
        while True:
            try:

                conn, addr = self.sock.accept()
                data = conn.recv(const.BUFF_SIZE)
                msg = eval(data.decode('utf-8'))
                # print("^^^^^^^^^^\n")
                server_ip = {'ip': addr[0]}
                print(f"A server with {server_ip} has requested to register\n")
                # print(msg)
                # print("\n")
                # print("conn :", conn)
                # print("addr : ", addr)
                # print("^^^^^^^^^^\n")
                if msg["type"] != const.REGISTER:
                    conn.close()
                    continue

                identifier = help.generate(ids)
                # print("#########\n")
                # print("The : ")
                # print(identifier)
                # print("#########\n")

                self.connections.append(conn)
                node = dict(
                    {'ip': addr[0], 'port': msg["port"], 'id': identifier})
                self.nodes.append(node)

                print("The server is assigned an ID and the details are :", {'ip': addr[0], 'port': msg["port"], 'id': identifier})
                print("\n")

            except socket.timeout:
                break

        self.nodes.sort(key=lambda x: x["id"])

    def send(self):

        data = str(self.nodes).encode('utf-8')
        for node in range(len(self.nodes)):

            port = self.nodes[node]["port"]
            try:
                self.connections[node].send(data)
            except socket.timeout:
                print("Error: no ack from node on port {}".format(port))

        self.close()

    def handler_log_msgs(self, signum: int, frame):
        self.logging.debug("[Register]: (ip:{} port:{})\n[Killed]\n".format(
            self.my_ip, self.my_port))
        self.close()

    def close(self):
        self.sock.close()
        sys.exit(1)
