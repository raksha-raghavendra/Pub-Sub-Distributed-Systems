import argparse
import pyfiglet
import os
import sys

# sys.path.insert(0, '/Users/maitreyeegadwe/Desktop/subscriber')
from src.main import Publisher


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
    intro = pyfiglet.figlet_format("PUBLISHER", font="slant")
    print(intro)

    publisher_node = Publisher(args.verbose, args.config_file)
    publisher_node.start()


if __name__ == '__main__':
    run()
