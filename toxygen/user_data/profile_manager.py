class ProfileManager:
    """
    Class with methods for search, load and save profiles
    """
    def __init__(self, path, name):
        path = append_slash(path)
        self._path = path + name + '.tox'
        self._directory = path
        # create /avatars if not exists:
        directory = path + 'avatars'
        if not os.path.exists(directory):
            os.makedirs(directory)

    def open_profile(self):
        with open(self._path, 'rb') as fl:
            data = fl.read()
        if data:
            return data
        else:
            raise IOError('Save file has zero size!')

    def get_dir(self):
        return self._directory

    def save_profile(self, data):
        inst = ToxES.get_instance()
        if inst.has_password():
            data = inst.pass_encrypt(data)
        with open(self._path, 'wb') as fl:
            fl.write(data)
        print('Profile saved successfully')

    def export_profile(self, new_path, use_new_path):
        path = new_path + os.path.basename(self._path)
        with open(self._path, 'rb') as fin:
            data = fin.read()
        with open(path, 'wb') as fout:
            fout.write(data)
        print('Profile exported successfully')
        copy(self._directory + 'avatars', new_path + 'avatars')
        if use_new_path:
            self._path = new_path + os.path.basename(self._path)
            self._directory = new_path
            Settings.get_instance().update_path()

    @staticmethod
    def find_profiles():
        """
        Find available tox profiles
        """
        path = Settings.get_default_path()
        result = []
        # check default path
        if not os.path.exists(path):
            os.makedirs(path)
        for fl in os.listdir(path):
            if fl.endswith('.tox'):
                name = fl[:-4]
                result.append((path, name))
        path = curr_directory()
        # check current directory
        for fl in os.listdir(path):
            if fl.endswith('.tox'):
                name = fl[:-4]
                result.append((path + '/', name))
        return result

    @staticmethod
    def get_path():
        return ProfileManager.get_instance().get_dir()
