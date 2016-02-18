from settings import Settings
import os


class Profile(object):

    @staticmethod
    def find_profiles():
        path = Settings.get_default_path()
        result = []
        # check default path
        for fl in os.listdir(path):
            if fl.endswith(".tox"):
                name = fl[:-4]
                result.append((path, name))
        path = os.path.dirname(os.path.abspath(__file__))
        # check current directory
        for fl in os.listdir(path):
            if fl.endswith(".tox"):
                name = fl[:-4]
                result.append((path, name))
        return result

