from src.settings import Settings
import sys
from src.bootstrap import node_generator
from src.profile import *
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
        arr = ProfileHelper.find_profiles()
        assert arr

    def test_open(self):
        data = ProfileHelper.open_profile(Settings.get_default_path(), 'tox_save')
        assert data

    def test_open_save(self):
        data = ProfileHelper.open_profile(Settings.get_default_path(), 'tox_save')
        ProfileHelper.save_profile(data)
        new_data = ProfileHelper.open_profile(Settings.get_default_path(), 'tox_save')
        assert new_data == data


class TestNodeGen():

    def test_generator(self):
        for elem in node_generator():
            assert len(elem) == 3

    def test_ports(self):
        for elem in node_generator():
            assert elem[1] in [33445, 443, 5190, 2306, 1813]


class TestTox():

    def test_loading(self):
        data = ProfileHelper.open_profile(Settings.get_default_path(), 'alice')
        settings = Settings.get_default_settings()
        tox = tox_factory(data, settings)
        for data in node_generator():
            tox.bootstrap(*data)
        del tox

    def test_friend_list(self):
        data = ProfileHelper.open_profile(Settings.get_default_path(), 'bob')
        settings = Settings.get_default_settings()
        tox = tox_factory(data, settings)
        s = tox.self_get_friend_list()
        size = tox.self_get_friend_list_size()
        assert size == 2
        assert len(s) == 2
        del tox
