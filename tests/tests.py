from toxygen.middleware.tox_factory import *


# TODO: add new tests

class TestTox:

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
