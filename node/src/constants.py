from enum import Enum

HEARTBEAT_TIME = 5
LISTENING = 10
MAX_TRANSMISSION_DELAY = 5
MAX_PROCESSING_DELAY = 2
TOTAL_DELAY = (2 * MAX_TRANSMISSION_DELAY) + MAX_PROCESSING_DELAY
BUFF_SIZE = 1024
DEFAULT_ID = -1


class Type(Enum):
    ELECTION = 0
    END = 1
    ANSWER = 2
    HEARTBEAT = 3
    REGISTER = 4
    ACK = 5
    SUBSCRIBE = 6
    PING = 7
    CONNECT_TO_CLIENT = 8
    PUBLISH_DATA_TO_SUBSCRIBERS = 9
