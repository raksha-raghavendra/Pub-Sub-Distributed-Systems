from src.main import Register
import argparse
import os
import pyfiglet


def run():

    parser = argparse.ArgumentParser(
        description='Implementation of distributed election algorithms.\nRegister node.'
    )

    parser.add_argument("-v", "--verbose", default=False, help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-c", "--config_file", action='store', required=True,
                        help="needed a config file in json format")

    args = parser.parse_args()


    os.system("clear")
    intro = pyfiglet.figlet_format("REGISTER SERVICE", font="slant")
    print(intro)
    print("(Info: This service assignes ID to the servers)\n")

    register = Register(args.verbose, args.config_file)
    register.receive()
    register.send()


if __name__ == '__main__':
    run()
