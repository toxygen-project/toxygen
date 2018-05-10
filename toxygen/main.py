import app
from user_data.settings import *
import utils.util as util
import argparse


__maintainer__ = 'Ingvar'
__version__ = '0.5.0'


def clean():
    """Removes all windows libs from libs folder"""
    directory = util.get_libs_directory()
    util.remove(directory)


def reset():
    Settings.reset_auto_profile()


def print_toxygen_version():
    print('Toxygen v' + __version__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', help='Prints Toxygen version')
    parser.add_argument('--clean', action='store_true', help='Deletes toxcore libs from libs folder')
    parser.add_argument('--reset', action='store_true', help='Resets default profile')
    parser.add_argument('--uri', help='Adds specified TOX ID to friends')
    parser.add_argument('profile', nargs='?', default=None, help='Path to TOX profile')
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

    toxygen = app.App(__version__, args.profile, args.uri)
    toxygen.main()


if __name__ == '__main__':
    main()
