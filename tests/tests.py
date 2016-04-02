from src.bootstrap import node_generator
from src.profile import *
from src.tox_dns import tox_dns


class TestProfile():

    def test_search(self):
        arr = ProfileHelper.find_profiles()
        assert arr
        assert len(arr) >= 2

    def test_open(self):
        data = ProfileHelper.open_profile(Settings.get_default_path(), 'alice')
        assert data

    def test_open_save(self):
        data = ProfileHelper.open_profile(Settings.get_default_path(), 'alice')
        ProfileHelper.save_profile(data)
        new_data = ProfileHelper.open_profile(Settings.get_default_path(), 'alice')
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

    def test_creation(self):
        name = 'Toxygen User'
        status_message = 'Toxing on Toxygen'
        tox = tox_factory()
        tox.self_set_name(name)
        tox.self_set_status_message(status_message)
        data = tox.get_savedata()
        del tox
        tox = tox_factory(data)
        assert tox.self_get_name() == name
        assert tox.self_get_status_message() == status_message

    def test_friend_list(self):
        data = ProfileHelper.open_profile(Settings.get_default_path(), 'bob')
        settings = Settings.get_default_settings()
        tox = tox_factory(data, settings)
        s = tox.self_get_friend_list()
        size = tox.self_get_friend_list_size()
        assert size == 2
        assert len(s) == 2
        del tox


class TestDNS():

    def test_dns(self):
        bot_id = '56A1ADE4B65B86BCD51CC73E2CD4E542179F47959FE3E0E21B4B0ACDADE51855D34D34D37CB5'
        tox_id = tox_dns('groupbot@toxme.io')
        assert tox_id == bot_id
