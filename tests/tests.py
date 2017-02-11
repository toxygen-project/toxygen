from toxygen.profile import *
from toxygen.tox_dns import tox_dns
import toxygen.toxes as encr
import toxygen.messages as m
import time


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


class TestProfileHelper:

    def test_creation(self):
        file_name, path = 'test.tox', os.path.dirname(os.path.realpath(__file__)) + '/'
        data = b'test'
        with open(path + file_name, 'wb') as fl:
            fl.write(data)
        ph = ProfileHelper(path, file_name[:4])
        assert ProfileHelper.get_path() == path
        assert ph.open_profile() == data
        assert os.path.exists(path + 'avatars/')


class TestDNS:

    def test_dns(self):
        Settings._instance = Settings.get_default_settings()
        bot_id = '56A1ADE4B65B86BCD51CC73E2CD4E542179F47959FE3E0E21B4B0ACDADE51855D34D34D37CB5'
        tox_id = tox_dns('groupbot@toxme.io')
        assert tox_id == bot_id

    def test_dns2(self):
        Settings._instance = Settings.get_default_settings()
        bot_id = '76518406F6A9F2217E8DC487CC783C25CC16A15EB36FF32E335A235342C48A39218F515C39A6'
        tox_id = tox_dns('echobot@toxme.io')
        assert tox_id == bot_id


class TestEncryption:

    def test_encr_decr(self):
        tox = tox_factory()
        data = tox.get_savedata()
        lib = encr.ToxES()
        for password in ('easypassword', 'njvnFjfn7vaGGV6', 'toxygen'):
            lib.set_password(password)
            copy_data = data[:]
            new_data = lib.pass_encrypt(data)
            new_data = lib.pass_decrypt(new_data)
            assert copy_data == new_data


class TestFriend:

    def create_singletons(self):
        Settings._instance = Settings.get_default_settings()
        ProfileHelper('abc', 'test')

    def create_friend(self, name, status_message, number, tox_id):
        friend = Friend(None, number, name, status_message, None, tox_id)
        return friend

    def test_friend_creation(self):
        self.create_singletons()
        name, status_message, number = 'Friend', 'I am friend!', 0
        tox_id = '76518406F6A9F2217E8DC487CC783C25CC16A15EB36FF32E335A235342C48A39218F515C39A6'
        friend = self.create_friend(name, status_message, number, tox_id)
        assert friend.name == name
        assert friend.tox_id == tox_id
        assert friend.status_message == status_message
        assert friend.number == number

    def test_friend_corr(self):
        self.create_singletons()
        name, status_message, number = 'Friend', 'I am friend!', 0
        tox_id = '76518406F6A9F2217E8DC487CC783C25CC16A15EB36FF32E335A235342C48A39218F515C39A6'
        friend = self.create_friend(name, status_message, number, tox_id)
        t = time.time()
        friend.append_message(m.InfoMessage('Info message', t))
        friend.append_message(m.TextMessage('Hello! It is test!', MESSAGE_OWNER['ME'], t + 0.001, 0))
        friend.append_message(m.TextMessage('Hello!', MESSAGE_OWNER['FRIEND'], t + 0.002, 0))
        assert friend.get_last_message_text() == 'Hello! It is test!'
        assert len(friend.get_corr()) == 3
        assert len(friend.get_corr_for_saving()) == 2
        friend.append_message(m.TextMessage('Not sent', MESSAGE_OWNER['NOT_SENT'], t + 0.002, 0))
        arr = friend.get_unsent_messages_for_saving()
        assert len(arr) == 1
        assert arr[0][0] == 'Not sent'
        tm = m.TransferMessage(MESSAGE_OWNER['FRIEND'],
                               time.time(),
                               TOX_FILE_TRANSFER_STATE['RUNNING'],
                               100, 'file_name', friend.number, 0)
        friend.append_message(tm)
        friend.clear_corr()
        assert len(friend.get_corr()) == 1
        assert len(friend.get_corr_for_saving()) == 0
        friend.append_message(m.TextMessage('Hello! It is test!', MESSAGE_OWNER['ME'], t, 0))
        assert len(friend.get_corr()) == 2
        assert len(friend.get_corr_for_saving()) == 1

# TODO: more friend tests and history test
