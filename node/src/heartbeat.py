from . import helpers as help
from .constants import TOTAL_DELAY, BUFF_SIZE, HEARTBEAT_TIME, DEFAULT_ID, Type
import time
import socket


def heartbeat(ip, lock, is_part_of_algo, leader, id, nodes, algo, start_election):
    while True:

        hb_sock = help.build_socket(ip)
        address = hb_sock.getsockname()

        time.sleep(HEARTBEAT_TIME)
        lock.acquire()

        # do not heartbeat the leader if current node is running an election
        # or if is the leader
        if is_part_of_algo or (leader in [id, DEFAULT_ID]):
            lock.release()
            continue

        # print("@@@@@@@@ All the server nodes @@@@@@@@@@  :", nodes)
        # print("\n\n")
        # print("@@@@@@ The leader is @@@@@@@@  :", coordinator)
        # print("\n\n")
        index = help.return_index_value_fromList(leader, nodes)
        info = nodes[index]

        msg = help.build_message_helper(
            id, Type['HEARTBEAT'].value, address[1], address[0])

        dest = (info["ip"], info["port"])

        print("Heartbeat message created")
        try:
            hb_sock.connect(dest)
            print(f"sending heartbeat to: {dest}")
            hb_sock.send(msg)
            receive_ack(hb_sock, dest, TOTAL_DELAY, algo, nodes, lock, start_election, leader)
            print(f"received ack from: {dest}\n\n")

        except ConnectionRefusedError:
            hb_sock.close()
            crash(algo, nodes, lock, start_election)


def receive_ack(sock, dest, waiting, algo, nodes, lock, start_election, leader):
    # need to calculate the starting time to provide
    # a residual time to use as timeout when invalid packet is received
    start = round(time.time())
    sock.settimeout(waiting)

    try:
        data = sock.recv(BUFF_SIZE)
    except (socket.timeout, ConnectionResetError):
        sock.close()
        crash(algo, nodes, lock, start_election)
        return

    if not data:
        sock.close()
        crash(algo, nodes, lock, start_election)
        return

    msg = eval(data.decode('utf-8'))

    if (msg["id"] == leader) and (msg["type"] == Type["ACK"].value):
        lock.release()

    else:
        stop = round(time.time())
        waiting -= (stop - start)
        receive_ack(sock, dest, waiting, algo, nodes, lock, start_election, leader)

    addr = (msg["ip"], msg["port"])
    sock.close()

    # method to manage a leaders' crash


def crash(algo, nodes, lock, start_election):
    if algo == False:
        nodes.pop()

    lock.release()
    start_election()
