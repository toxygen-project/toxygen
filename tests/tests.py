from contacts.profile import *
from network.tox_dns import tox_dns
from db.history import History
from toxygen.smileys import SmileyLoader
from messenger.messages import *
import user_data.toxes as encr
import toxygen.util as util
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


class TestProfileManager:

    def test_creation(self):
        file_name, path = 'test.tox', os.path.dirname(os.path.realpath(__file__)) + '/'
        data = b'test'
        with open(path + file_name, 'wb') as fl:
            fl.write(data)
        ph = ProfileManager(path, file_name[:4])
        assert ProfileManager.get_path() == path
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
            assert lib.is_data_encrypted(new_data)
            new_data = lib.pass_decrypt(new_data)
            assert copy_data == new_data


class TestSmileys:

    def test_loading(self):
        settings = {'smiley_pack': 'default', 'smileys': True}
        sm = SmileyLoader(settings)
        assert sm.get_smileys_path() is not None
        l = sm.get_packs_list()
        assert len(l) == 4


def create_singletons():
    folder = util.curr_directory() + '/abc'
    Settings._instance = Settings.get_default_settings()
    if not os.path.exists(folder):
        os.makedirs(folder)
    ProfileManager(folder, 'test')


def create_friend(name, status_message, number, tox_id):
    friend = Friend(None, number, name, status_message, None, tox_id)
    return friend


def create_random_friend():
    name, status_message, number = 'Friend', 'I am friend!', 0
    tox_id = '76518406F6A9F2217E8DC487CC783C25CC16A15EB36FF32E335A235342C48A39218F515C39A6'
    friend = create_friend(name, status_message, number, tox_id)
    return friend


class TestFriend:

    def test_friend_creation(self):
        create_singletons()
        name, status_message, number = 'Friend', 'I am friend!', 0
        tox_id = '76518406F6A9F2217E8DC487CC783C25CC16A15EB36FF32E335A235342C48A39218F515C39A6'
        friend = create_friend(name, status_message, number, tox_id)
        assert friend.name == name
        assert friend.tox_id == tox_id
        assert friend.status_message == status_message
        assert friend.number == number

    def test_friend_corr(self):
        create_singletons()
        friend = create_random_friend()
        t = time.time()
        friend.append_message(InfoMessage('Info message', t))
        friend.append_message(TextMessage('Hello! It is test!', MESSAGE_OWNER['ME'], t + 0.001, 0))
        friend.append_message(TextMessage('Hello!', MESSAGE_OWNER['FRIEND'], t + 0.002, 0))
        assert friend.get_last_message_text() == 'Hello! It is test!'
        assert len(friend.get_corr()) == 3
        assert len(friend.get_corr_for_saving()) == 2
        friend.append_message(TextMessage('Not sent', MESSAGE_OWNER['NOT_SENT'], t + 0.002, 0))
        arr = friend.get_unsent_messages_for_saving()
        assert len(arr) == 1
        assert arr[0][0] == 'Not sent'
        tm = TransferMessage(MESSAGE_OWNER['FRIEND'],
                             time.time(),
                             TOX_FILE_TRANSFER_STATE['RUNNING'],
                             100, 'file_name', friend.number, 0)
        friend.append_message(tm)
        friend.clear_corr()
        assert len(friend.get_corr()) == 1
        assert len(friend.get_corr_for_saving()) == 0
        friend.append_message(TextMessage('Hello! It is test!', MESSAGE_OWNER['ME'], t, 0))
        assert len(friend.get_corr()) == 2
        assert len(friend.get_corr_for_saving()) == 1

    def test_history_search(self):
        create_singletons()
        friend = create_random_friend()
        message = 'Hello! It is test!'
        friend.append_message(TextMessage(message, MESSAGE_OWNER['ME'], time.time(), 0))
        last_message = friend.get_last_message_text()
        assert last_message == message
        result = friend.search_string('e[m|s]')
        assert result is not None
        result = friend.search_string('tox')
        assert result is None


class TestHistory:

    def test_history(self):
        create_singletons()
        db_name = 'my_name'
        name, status_message, number = 'Friend', 'I am friend!', 0
        tox_id = '76518406F6A9F2217E8DC487CC783C25CC16A15EB36FF32E335A235342C48A39218F515C39A6'
        friend = create_friend(name, status_message, number, tox_id)
        history = History(db_name)
        history.add_friend_to_db(friend.tox_id)
        assert history.friend_exists_in_db(friend.tox_id)
        text_message = 'Test!'
        t = time.time()
        friend.append_message(TextMessage(text_message, MESSAGE_OWNER['ME'], t, 0))
        messages = friend.get_corr_for_saving()
        history.save_messages_to_db(friend.tox_id, messages)
        getter = history.messages_getter(friend.tox_id)
        messages = getter.get_all()
        assert len(messages) == 1
        assert messages[0][0] == text_message
        assert messages[0][1] == MESSAGE_OWNER['ME']
        assert messages[0][-1] == 0
        history.delete_message(friend.tox_id, t)
        getter = history.messages_getter(friend.tox_id)
        messages = getter.get_all()
        assert len(messages) == 0
        history.delete_friend_from_db(friend.tox_id)
        assert not history.friend_exists_in_db(friend.tox_id)
