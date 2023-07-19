import json
import sys
from socket import socket

from .log_helper import log_data_details
from .bully_leader_election import Bully_leader_election, Type
from .constants import BUFF_SIZE, DEFAULT_ID
from .helpers import build_message_helper, return_id_from_list, build_socket


class Server_Node_Class:

    def __init__(self, log_data: bool, is_bully: bool, configuration_path_value: str, delay_time_interval: bool):

        with open(configuration_path_value, "r") as configuration_file:
            user_provided_config_values = json.load(configuration_file)

        self.algorithm = is_bully
        self.registery_service_port = user_provided_config_values["register"]["port"]
        self.registery_service_ip = user_provided_config_values["register"]["ip"]
        self.delay = delay_time_interval
        self.leader_node_ip = user_provided_config_values["leader"]["ip"]
        self.leader_node_port = user_provided_config_values["leader"]["port"]
        self.current_node_ip = user_provided_config_values["node"]["ip"]
        self.verbose = log_data

    def start(self):

        socket_registry_service = build_socket(self.current_node_ip)

        sock_temp = build_socket(self.current_node_ip)
        sock_temp.listen()


        # socket used in listening phase
        sock = build_socket(self.current_node_ip)
        sock.listen()

        logging = log_data_details()

        msg = build_message_helper(DEFAULT_ID, Type['REGISTER'].value,
                                   sock.getsockname()[1], sock.getsockname()[0])
        destnation = (self.registery_service_ip, self.registery_service_port)

        try:
            socket_registry_service.connect(destnation)
        except ConnectionRefusedError:
            print("Register node not available")
            sock.close()
            sys.exit(1)

        socket_registry_service.send(msg)

        # waits to receive the complete list of network members
        data = socket_registry_service.recv(BUFF_SIZE)
        # print("@@@@@@@@@@\n")
        # print(f"This server with ip = {sock.getsockname()[0]} has been assigned id by the Register service\n")
        # print("there data received from register service is :")
        # print(data)
        # print("@@@@@@@@@@\n")
        if not data:
            sock.close()
            print("Register node is crashed")
            sys.exit(1)

        msg = eval(data.decode('utf-8'))
        identifier = return_id_from_list(sock.getsockname()[1], msg)

        # print("########## 12345 ########", msg)
        print(f"This server with ip = {sock.getsockname()[0]} has been assigned id by the Register service\n")
        print(f"The list of all the nodes is : {msg}")

        socket_registry_service.close()

        # check if current node is the only one
        if (len(msg) == 1):
            sock.close()
            print("Not enough nodes generated!")
            sys.exit(1)

        if self.algorithm:
            Bully_leader_election(sock.getsockname()[0], sock.getsockname()[1], identifier,
                                  msg, sock, self.verbose, self.delay, self.algorithm,
                                  self.leader_node_ip, self.leader_node_port)
