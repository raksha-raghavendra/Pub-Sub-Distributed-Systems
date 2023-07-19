import os
import signal as sign
import socket
import sys
import time
from threading import Thread, Lock

from . import helpers as help
from . import log_helper as verb
from .constants import TOTAL_DELAY, BUFF_SIZE, DEFAULT_ID, Type
from .heartbeat import heartbeat
from .pub_sub import PubSub


class Bully_leader_election:

    def __init__(self, current_node_ip: str, current_node_port: int, id: int, nodes_topology_entities: list,
                 socket: socket, log_data: bool, delay_time_interval: bool,
                 is_bully_algorithm: bool, leader_node_ip: str, leader_node_port: int):

        self.length_of_checked_nodes = 0

        self.message_from_coordinator = False

        self.ip = current_node_ip
        self.port = current_node_port
        self.id = id
        self.nodes = nodes_topology_entities
        self.socket = socket
        self.algo = is_bully_algorithm
        self.ip_leader = leader_node_ip
        self.port_leader = leader_node_port

        self.leader = DEFAULT_ID
        self.coordinatorport = DEFAULT_ID
        self.lock = Lock()

        self.delay = delay_time_interval
        self.verbose = log_data

        sign.signal(sign.SIGINT, self.handler)

        self.logging = verb.log_data_details()

        self.is_part_of_algo = False

        self.pub_sub = PubSub(self.leader, self.id, self.ip_leader, self.nodes, self.ip, self.port_leader)

        thread = Thread(target=self.listening)
        thread.daemon = True
        thread.start()

        # threadmsg = Thread(target=self.listeningmsg)
        # threadmsg.daemon = True
        # threadmsg.start()

        self.start_election()
        heartbeat(self.ip, self.lock, self.is_part_of_algo, self.leader, self.id, self.nodes, self.algo, self.start_election)

    def start_election(self):

        self.lock.acquire()
        current_position = help.return_index_value_fromList(self.id, self.nodes) + 1
        self.is_part_of_algo = True
        self.message_from_coordinator = False

        if (current_position != len(self.nodes)) and (self.low_id_node(current_position) == 0):
            return

        self.leader = self.id
        self.is_part_of_algo = False

        print(f"Node with id = {self.id} and port = {self.port} selected as leader.")

        close = False
        for node in range(len(self.nodes) - 1):
            sock = help.build_socket(self.ip)
            if node == (current_position - 1):
                continue
            try:
                sock.connect(
                    (self.nodes[node]["ip"], self.nodes[node]["port"]))
                close = True
                self.forwarding(self.nodes[node], self.id, Type['END'], sock)
                sock.close()
            except ConnectionRefusedError:
                sock.close()
                continue

        if not close:
            self.socket.close()
            os._exit(1)

        self.pub_sub.set_leader_id(self.leader)

        client_thread = Thread(target=self.pub_sub.listen_to_client)
        client_thread.daemon = True
        client_thread.start()

        self.lock.release()

    def forwarding(self, node: dict, id: int, type: Type, conn: socket):

        help.delay(self.delay, TOTAL_DELAY)
        dest = (node["ip"], node["port"])
        msg = help.build_message_helper(id, type.value, self.port, self.ip)
        try:
            conn.send(msg)
        except ConnectionResetError:
            return

    def wait_more_time(self):
        timeout_value = time.time() + TOTAL_DELAY
        while (time.time() < timeout_value):
            self.lock.acquire()
            if self.message_from_coordinator == True:
                self.is_part_of_algo = False
                self.message_from_coordinator = False
                self.lock.release()
                return 0
            self.lock.release()

        self.lock.acquire()
        self.is_part_of_algo = False
        return 1

    def answer_msg(self):
        self.lock.acquire()
        self.length_of_checked_nodes -= 1
        self.lock.release()

    def end_msg(self, msg: dict):
        self.lock.acquire()
        self.coordinatorport = msg["port"]
        self.leader = msg["id"]
        self.message_from_coordinator = True
        self.lock.release()

    def election_msg(self, msg: dict):

        self.lock.acquire()
        sock = help.build_socket(self.ip)
        try:
            sock.connect((msg["ip"], msg["port"]))
            self.forwarding(msg, self.id, Type['ANSWER'], sock)
        except ConnectionRefusedError:
            pass

        sock.close()

        if self.is_part_of_algo == False:
            self.lock.release()
            self.start_election()
            return

        self.lock.release()

    def low_id_node(self, index: int) -> int:

        self.leader = DEFAULT_ID
        self.length_of_checked_nodes = len(self.nodes) - index
        ack_nodes = self.length_of_checked_nodes
        exit = False
        for node in range(index, len(self.nodes)):
            sock = help.build_socket(self.ip)
            try:
                sock.connect(
                    (self.nodes[node]["ip"], self.nodes[node]["port"]))
                self.forwarding(self.nodes[node],
                                self.id, Type['ELECTION'], sock)
                sock.close()
                exit = True
            except ConnectionRefusedError:
                sock.close()
                continue

        if exit == False: return 1
        self.lock.release()
        timeout_interval = time.time() + TOTAL_DELAY
        while (time.time() < timeout_interval):
            self.lock.acquire()
            if self.length_of_checked_nodes != ack_nodes:
                self.lock.release()
                if self.wait_more_time() == 0:
                    return 0
                else:
                    return 1
            self.lock.release()

        self.lock.acquire()
        return 1

    def listening(self):
        while True:

            self.lock.acquire()

            self.socket.settimeout(None)
            self.lock.release()

            try:
                connection, addr = self.socket.accept()
            except socket.timeout:
                self.logging.debug("[Node]: (ip:{} port:{} id:{})\n[Terminates]\n".format(
                    self.ip, self.port, self.id))
                self.socket.close()
                os._exit(1)

            data = connection.recv(BUFF_SIZE)

            if not data:
                continue

            data = eval(data.decode('utf-8'))

            if self.leader == self.id and data["type"] == Type['HEARTBEAT'].value:
                print(f"Received heartbeat and sending ack back to the node : {addr}\n\n")
                help.delay(self.delay, TOTAL_DELAY)

                msg = help.build_message_helper(
                    self.id, Type['ACK'].value, self.port, self.ip)

                connection.send(msg)
                connection.close()
                continue

            elif data["type"] == Type['ANSWER'].value:
                self.answer_msg()
                connection.close()
                continue

            elif data["type"] == Type['CONNECT_TO_CLIENT'].value:
                print(f"Data received from leader: {data}")
                connection.close()

                self.pub_sub.handle_client(data)
                continue

            elif data["type"] == Type['PUBLISH_DATA_TO_SUBSCRIBERS'].value:
                print(f"Data received from server: {data}")
                connection.close()

                self.pub_sub.publish_message_to_subscribers(data["topic"], data["job"])
                continue

            elif data["type"] == Type["SUBSCRIBE"].value:
                # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                if data["topic"] == "PING":
                    data = {'response': "ACK"};
                    str(data).encode('utf-8')
                    print(data)
                    connection.send(str(data).encode('utf-8'))
                else:
                    print(data, "\n\n")
                    # data = random.choice(myDict[data["topic"]])
                    str(data).encode('utf-8')
                    # eval(data)
                    print(data)
                    msg = help.build_message_helper(
                        self.id, Type['SUBSCRIBE'].value, self.port, self.ip)

                    connection.send(str(data).encode('utf-8'))
                # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n")
                connection.close()
                continue

            func = {Type['ELECTION'].value: self.election_msg,
                    Type['END'].value: self.end_msg
                    }

            func[data["type"]](data)
            connection.close()



    def handler(self, signum: int, frame):
        self.logging.debug("[Node]: (ip:{} port:{} id:{})\n[Killed]\n".format(
            self.ip, self.port, self.id))
        self.socket.close()
        sys.exit(1)
