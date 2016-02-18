from src.settings import Settings
from src.tox import Tox
import sys
from src.profile import Profile
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


class TestTox():

    def test_public_key(self):
        settings = Settings()
        data = Profile.open_profile(Settings.get_default_path(), 'tox_save')
        try:
            tox = Tox(data, settings)
        except:
            raise
            assert 0
        try:
            key = tox.self_get_public_key()
        except:
            raise
            assert 0
        assert len(key.raw) == 32
        try:
            del tox
        except:
            raise


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
