import socket
import json

from . import helpers as help
from .constants import BUFF_SIZE, Type
from threading import Thread

topics_subscribers_dict = {}


class PubSub:

    def __init__(self, leader, id, ip_leader, nodes, ip, port_leader):

        self.leader = leader
        self.id = id
        self.ip_leader = ip_leader
        self.nodes = nodes
        self.ip = ip
        self.port_leader = port_leader
        self.count_of_clients = 0

    def set_leader_id(self, leader):
        self.leader = leader

    def listen_to_client(self):
        accept_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        accept_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        accept_client_socket.settimeout(None)
        address = (self.ip_leader, self.port_leader)
        print(f"Leader : {address} accepting publisher/subscriber requests\n")

        try:
            accept_client_socket.bind(address)
            accept_client_socket.listen()

            while True:
                conn, addr = accept_client_socket.accept()
                print(f"Connection received: conn={conn}, addr={addr}\n")

                data = eval(conn.recv(BUFF_SIZE).decode('utf-8'))
                print(f"Data received from client: {data}")

                self.count_of_clients += 1
                index = self.count_of_clients % len(self.nodes)
                print(f"clients_count = {self.count_of_clients}. "
                      f"Server with id {self.nodes[index]['id']} will handle the client")

                if self.nodes[index]["id"] == self.id:
                    # leader itself will handle the client
                    self.handle_client(data)
                else:
                    # leader will send the client data to the
                    # server that needs to handle it
                    self.send_client_data_to_server(data, self.nodes[index])

                conn.close()
        except BaseException as e:
            # print("Error:", e)
            print("")

        accept_client_socket.close()
        self.close_all_subscribers()

    def close_all_subscribers(self):
        for topic, subscribers in topics_subscribers_dict.items():
            for subscriber_socket in subscribers:
                subscriber_socket.close()

    def send_client_data_to_server(self, data, info):
        leader_ephemeral_socket = help.build_socket(self.ip)
        msg = help.create_server_msg(self.id, Type['CONNECT_TO_CLIENT'].value, data)

        client_handler_address = (info["ip"], info["port"])

        try:
            print(f"Sending client data to server {info}\n\n")
            leader_ephemeral_socket.connect(client_handler_address)
            leader_ephemeral_socket.send(msg)
            leader_ephemeral_socket.close()
        except BaseException as e:
            print("Error in sending data to server: ", e)
            leader_ephemeral_socket.close()

    def handle_client(self, data):
        if data["client_type"] == "subscriber":
            print("The client recognized as subscriber\n")
            print("This subscriber has subscribed to : ", data["topics"])
            print("\n")
            self.process_subscriber(data)
        elif data["client_type"] == "publisher":
            print("The client recognized as publisher\n")
            self.process_publisher(data)
        else:
            print("Client type not recognized.")

    def process_subscriber(self, data):
        print("Processing subscriber\n")
        for topic in data["topics"]:
            subscriber_address = (data["ip"], data["port"])
            subscriber_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            subscriber_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            subscriber_socket.settimeout(None)

            try:
                subscriber_socket.connect(subscriber_address)

                subscribers = topics_subscribers_dict.get(topic, set())
                subscribers.add(subscriber_socket)
                topics_subscribers_dict[topic] = subscribers
            except BaseException as e:
                print("Could not connect to the subscriber", e)

        print(f"Subscriber list = {topics_subscribers_dict}")

    def process_publisher(self, data):
        thread = Thread(target=self.listen_to_publisher, args=(data,))
        thread.daemon = True
        thread.start()

    def listen_to_publisher(self, publisher):
        publisher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        publisher_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        publisher_socket.settimeout(None)
        address = (publisher["ip"], publisher["port"])
        print(f"Server listening for data published by publisher\n")

        try:
            publisher_socket.bind(address)
            publisher_socket.listen()

            conn, addr = publisher_socket.accept()
            print(f"Connection received at publisher socket!\n")

            while True:
                data = eval(conn.recv(BUFF_SIZE).decode('utf-8'))
                print(f"Data received from publisher: {data}")

                self.publish_message_to_subscribers(data["topic"], data["job"])
                self.broadcast(data)
        except BaseException as e:
            print("Error:", e)

        publisher_socket.close()

    def publish_message_to_subscribers(self, topic, job):
        print("BP1")
        subscribers = topics_subscribers_dict.get(topic, set())
        print(f"Subscribers for topic {topic} = {subscribers}")

        msg = {"topic": topic, "job": job}
        for subscriber_socket in subscribers:
            print(f"subscriber_socket = {subscriber_socket}")
            # print(f"msg = {msg}, type = {type(msg)}, {type(msg['topic'])}, {type(msg['job'])}")
            subscriber_socket.send(json.dumps(msg).encode('utf-8'))
            print("Data sent to subscriber.")

    def broadcast(self, data):
        for info in self.nodes:
            if info["id"] == self.id:
                continue

            leader_ephemeral_socket = help.build_socket(self.ip)
            msg = help.create_server_msg(self.id, Type['PUBLISH_DATA_TO_SUBSCRIBERS'].value, data)

            client_handler_address = (info["ip"], info["port"])

            try:
                print(f"Sending client data to server {info}\n\n")
                leader_ephemeral_socket.connect(client_handler_address)
                leader_ephemeral_socket.send(msg)
                leader_ephemeral_socket.close()
            except BaseException as e:
                print("Error in sending data to server: ", e)
                leader_ephemeral_socket.close()
