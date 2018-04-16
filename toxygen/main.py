import sys
import app
from user_data.settings import *
from util.util import curr_directory, remove
import argparse

__maintainer__ = 'Ingvar'
__version__ = '0.5.0'


def clean():
    """Removes all windows libs from libs folder"""
    d = curr_directory() + '/libs/'
    remove(d)


def reset():
    Settings.reset_auto_profile()


def print_toxygen_version():
    print('Toxygen v' + __version__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', help='Prints Toxygen version')
    parser.add_argument('--clean', help='Deletes toxcore libs from libs folder')
    parser.add_argument('--reset', help='Resets default profile')
    parser.add_argument('profile_path', nargs='?', default=None, help='Resets default profile')
    args = parser.parse_args()

    if args.version:
        print_toxygen_version()
        return

    if args.clean:
        clean()
        return

    if args.reset:
        reset()
        return

    toxygen = app.App(__version__, path_to_profile=args.profile_path)
    toxygen.main()


if __name__ == '__main__':
    main()
