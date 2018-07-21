from toxygen.middleware.tox_factory import *


# TODO: add new tests

class TestTox:

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
