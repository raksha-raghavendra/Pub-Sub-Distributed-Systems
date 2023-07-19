import json
import socket
from random import randint
import time
from math import floor


def build_socket(node_ip: str) -> socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (node_ip, 0)
    sock.bind(address)
    return sock


def return_index_value_fromList(id: int, nodes: list) -> int:
    i = 0
    for j in nodes:
        if j.get('id') == id:
            return i
        i += 1
    return 0


def create_server_msg(id: int, type: int, data: dict) -> bytes:
    data['type'] = type
    data['id'] = id
    msg = json.dumps(data)
    msg = str(msg).encode('utf-8')
    return msg


def build_message_helper(node_id: int, type_of_msg: int, port_details: int, ip_value: str) -> bytes:
    msg = {'type': type_of_msg, 'id': node_id, 'port': port_details, 'ip': ip_value}
    msg = json.dumps(msg)
    msg = str(msg).encode('utf-8')
    return msg


def return_id_from_list(port_value: int, li: list) -> int:
    for i in li:
        if i.get('port') == port_value:
            return i.get('id')
    return 0


def delay(is_needed: bool, upper_limit: int):
    if is_needed:
        time_delay = randint(0, floor(upper_limit * 1.5))
        time.sleep(time_delay)
