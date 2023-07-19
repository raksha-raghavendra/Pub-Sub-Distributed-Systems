from src.main import Server_Node_Class
import argparse
import pyfiglet
import os


def run():
    algorithm_options = argparse.ArgumentParser(
        description='Implementation of distributed election algorithms.\nGeneric node.'
    )

    algorithm_options.add_argument("-v", "--verbose", default=False, help="increase output verbosity",
                                   action="store_true")
    algorithm_options.add_argument("-d", "--delay", default=False,
                                   help="generate a random delay to forwarding messages", action="store_true")
    algorithm_options.add_argument("-c", "--config_file", action='store',
                                   help="needed a config file in json format")

    args = algorithm_options.parse_args()

    if not (args.config_file):
        algorithm_options.error('JSON FILE NOT PROVIDED')

    os.system("clear")
    intro = pyfiglet.figlet_format("NODE", font="slant")
    print(intro)
    print("(Info: Maitreyee)\n")

    node = Server_Node_Class(args.verbose, True, args.config_file, args.delay)
    node.start()


if __name__ == '__main__':
    run()
