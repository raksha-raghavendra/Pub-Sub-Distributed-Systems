import argparse
import pyfiglet
import os
import sys

from src.main import Subscriber


def run():
    parser = argparse.ArgumentParser(
        description='Implementation of distributed election algorithms.\nGeneric node.'
    )

    parser.add_argument("-v", "--verbose", default=False, help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-c", "--config_file", action='store', required=True,
                        help="needed a config file in json format")

    args = parser.parse_args()


    os.system("clear")
    intro = pyfiglet.figlet_format("SUBSCRIBER", font="slant")
    print(intro)

    subscriber_node = Subscriber(args.verbose, args.config_file)
    subscriber_node.start()


if __name__ == '__main__':
    run()
