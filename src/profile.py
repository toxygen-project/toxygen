from settings import Settings
import os


class Profile(object):

    @staticmethod
    def find_profiles():
        path = Settings.get_default_path()
        result = []
        # check default path
        for fl in os.listdir(path):
            if fl.endswith('.tox'):
                name = fl[:-4]
                result.append((path, name))
        path = os.path.dirname(os.path.abspath(__file__))
        # check current directory
        for fl in os.listdir(path):
            if fl.endswith('.tox'):
                name = fl[:-4]
                result.append((path, name))
        return result

    @staticmethod
    def open_profile(path, name):
        Profile._path = path + name + '.tox'
        with open(Profile._path, 'rb') as fl:
            data = fl.read()
        if data:
            print 'Data loaded from: {}'.format(Profile._path)
            return data
        else:
            raise IOError('Save file not found. Path: {}'.format(Profile._path))

    @staticmethod
    def save_profile(data):
        with open(Profile._path, 'wb') as fl:
            fl.write(data)
        print 'Data saved to: {}'.format(Profile._path)

