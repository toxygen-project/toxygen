import sys
import app
from user_data.settings import *
from util.util import curr_directory, program_version, remove
import argparse


def clean():
    """Removes all windows libs from libs folder"""
    d = curr_directory() + '/libs/'
    remove(d)


def reset():
    Settings.reset_auto_profile()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version')
    parser.add_argument('--clean')
    parser.add_argument('--reset')
    args = parser.parse_args()
    if not len(args):
        toxygen = app.App()
    else:  # started with argument(s)
        arg = sys.argv[1]
        if arg == '--version':
            print('Toxygen v' + program_version)
            return
        elif arg == '--help':
            print('Usage:\ntoxygen path_to_profile\ntoxygen tox_id\ntoxygen --version\ntoxygen --reset')
            return
        elif arg == '--clean':
            clean()
            return
        elif arg == '--reset':
            reset()
            return
        else:
            toxygen = app.App(arg)
    toxygen.main()


if __name__ == '__main__':
    main()
