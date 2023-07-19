import logging
from random import randint
from . import constants as const


def generate(list: list):
    identifier = randint(const.MIN, const.MAX)
    if identifier not in list:
        return identifier
    else:
        generate(list)


def set_logging() -> logging:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] %(asctime)s\n%(message)s",
        datefmt='%b-%d-%y %I:%M:%S'
    )
    return logging
