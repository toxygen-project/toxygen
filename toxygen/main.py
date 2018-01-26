import sys
from user_data.settings import *
from callbacks import init_callbacks, stop, start
from util import curr_directory, program_version, remove
import updater
import argparse



    class Login:

        def __init__(self, arr):
            self.arr = arr

        def login_screen_close(self, t, number=-1, default=False, name=None):
            """ Function which processes data from login screen
            :param t: 0 - window was closed, 1 - new profile was created, 2 - profile loaded
            :param number: num of chosen profile in list (-1 by default)
            :param default: was or not chosen profile marked as default
            :param name: name of new profile
            """
            self.t = t
            self.num = number
            self.default = default
            self.name = name

        def get_data(self):
            return self.arr[self.num]


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
        toxygen = Toxygen()
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
            toxygen = Toxygen(arg)
    toxygen.main()


if __name__ == '__main__':
    main()
