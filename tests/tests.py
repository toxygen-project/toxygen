from src.settings import Settings
from src.util import bin_to_string, string_to_bin
import sys
from src.bootstrap import node_generator
from src.profile import Profile, tox_factory
import os


class TestSettings():

    def test_creation(self):
        s = Settings()
        assert s['ipv6_enabled'] is not None
        assert s['notifications'] is not None

    def test_with_delete(self):
        path = Settings.get_default_path() + 'toxygen.json'
        os.remove(path)
        Settings()
        assert os.path.exists(path)


class TestProfile():

    def test_search(self):
        arr = Profile.find_profiles()
        assert arr

    def test_open(self):
        data = Profile.open_profile(Settings.get_default_path(), 'tox_save')
        assert data

    def test_open_save(self):
        data = Profile.open_profile(Settings.get_default_path(), 'tox_save')
        Profile.save_profile(data)
        new_data = Profile.open_profile(Settings.get_default_path(), 'tox_save')
        assert new_data == data


class TestUtils():

    def test_convert(self):
        id = 'C4CEB8C7AC607C6B374E2E782B3C00EA3A63B80D4910B8649CCACDD19F260819'
        data = string_to_bin(id)
        new_id = bin_to_string(data)
        assert id == new_id


class TestNodeGen():

    def test_generator(self):
        for elem in node_generator():
            assert len(elem) == 3

    def test_ports(self):
        for elem in node_generator():
            assert elem[1] in [33445, 443, 5190, 2306, 1813]


class TestTox():

    def test_creation(self):
        data = Profile.open_profile(Settings.get_default_path(), 'tox_save')
        settings = Settings.get_default_settings()
        tox = tox_factory(data, settings)
        for data in node_generator():
            tox.bootstrap(*data)
        del tox
