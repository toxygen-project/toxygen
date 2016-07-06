from toxygen.bootstrap import node_generator
from toxygen.profile import *
from toxygen.settings import ProfileHelper
from toxygen.tox_dns import tox_dns
import toxygen.toxencryptsave as encr


class TestProfile:

    def test_search(self):
        arr = ProfileHelper.find_profiles()
        assert len(arr) >= 2

    def test_open(self):
        data = ProfileHelper(Settings.get_default_path(), 'alice').open_profile()
        assert data


class TestTox:

    def test_loading(self):
        data = ProfileHelper(Settings.get_default_path(), 'alice').open_profile()
        settings = Settings.get_default_settings()
        tox = tox_factory(data, settings)
        for data in node_generator():
            tox.bootstrap(*data)
        del tox

    def test_creation(self):
        name = b'Toxygen User'
        status_message = b'Toxing on Toxygen'
        tox = tox_factory()
        tox.self_set_name(name)
        tox.self_set_status_message(status_message)
        data = tox.get_savedata()
        del tox
        tox = tox_factory(data)
        assert tox.self_get_name() == str(name, 'utf-8')
        assert tox.self_get_status_message() == str(status_message, 'utf-8')

    def test_friend_list(self):
        data = ProfileHelper(Settings.get_default_path(), 'bob').open_profile()
        settings = Settings.get_default_settings()
        tox = tox_factory(data, settings)
        s = tox.self_get_friend_list()
        size = tox.self_get_friend_list_size()
        assert size <= 2
        assert len(s) <= 2
        del tox


class TestDNS:

    def test_dns(self):
        bot_id = '56A1ADE4B65B86BCD51CC73E2CD4E542179F47959FE3E0E21B4B0ACDADE51855D34D34D37CB5'
        tox_id = tox_dns('groupbot@toxme.io')
        assert tox_id == bot_id


class TestEncryption:

    def test_encr_decr(self):
        with open(settings.Settings.get_default_path() + '/alice.tox', 'rb') as fl:
            data = fl.read()
        lib = encr.ToxEncryptSave()
        lib.set_password('easypassword')
        copy_data = data[:]
        data = lib.pass_encrypt(data)
        data = lib.pass_decrypt(data)
        assert copy_data == data
