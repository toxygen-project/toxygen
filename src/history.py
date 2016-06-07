# coding=utf-8
from sqlite3 import connect
import settings
from os import chdir
import os.path
from toxencryptsave import LibToxEncryptSave


PAGE_SIZE = 42

MESSAGE_OWNER = {
    'ME': 0,
    'FRIEND': 1,
    'NOT_SENT': 2
}


class History(object):

    def __init__(self, name):
        self._name = name
        chdir(settings.ProfileHelper.get_path())
        path = settings.ProfileHelper.get_path() + self._name + '.hstr'
        if os.path.exists(path):
            decr = LibToxEncryptSave.get_instance()
            try:
                with open(path, 'rb') as fin:
                    data = fin.read()
                if decr.is_data_encrypted(data):
                    data = decr.pass_decrypt(data)
                    with open(path, 'wb') as fout:
                        fout.write(data)
            except:
                os.remove(path)
        db = connect(name + '.hstr')
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS friends('
                       '    tox_id TEXT PRIMARY KEY'
                       ')')
        db.close()

    def save(self):
        encr = LibToxEncryptSave.get_instance()
        if encr.has_password():
            path = settings.ProfileHelper.get_path() + self._name + '.hstr'
            with open(path, 'rb') as fin:
                data = fin.read()
            data = encr.pass_encrypt(data)
            with open(path, 'wb') as fout:
                fout.write(data)

    def export(self, directory):
        path = settings.ProfileHelper.get_path() + self._name + '.hstr'
        new_path = directory + self._name + '.hstr'
        with open(path, 'rb') as fin:
            data = fin.read()
        with open(new_path, 'wb') as fout:
            fout.write(data)

    def add_friend_to_db(self, tox_id):
        chdir(settings.ProfileHelper.get_path())
        db = connect(self._name + '.hstr')
        try:
            cursor = db.cursor()
            cursor.execute('INSERT INTO friends VALUES (?);', (tox_id, ))
            cursor.execute('CREATE TABLE id' + tox_id + '('
                           '    id INTEGER PRIMARY KEY,'
                           '    message TEXT,'
                           '    owner INTEGER,'
                           '    unix_time REAL,'
                           '    message_type INTEGER'
                           ')')
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_friend_from_db(self, tox_id):
        chdir(settings.ProfileHelper.get_path())
        db = connect(self._name + '.hstr')
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM friends WHERE tox_id=?;', (tox_id, ))
            cursor.execute('DROP TABLE id' + tox_id + ';')
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def friend_exists_in_db(self, tox_id):
        chdir(settings.ProfileHelper.get_path())
        db = connect(self._name + '.hstr')
        cursor = db.cursor()
        cursor.execute('SELECT 0 FROM friends WHERE tox_id=?', (tox_id, ))
        result = cursor.fetchone()
        db.close()
        return result is not None

    def save_messages_to_db(self, tox_id, messages_iter):
        chdir(settings.ProfileHelper.get_path())
        db = connect(self._name + '.hstr')
        try:
            cursor = db.cursor()
            cursor.executemany('INSERT INTO id' + tox_id + '(message, owner, unix_time, message_type) '
                               'VALUES (?, ?, ?, ?);', messages_iter)
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def update_messages(self, tox_id, count):
        # TODO: mark all unsent messages to friend with specified public key :tox_id (except last :count) as sent
        pass

    def delete_messages(self, tox_id):
        chdir(settings.ProfileHelper.get_path())
        db = connect(self._name + '.hstr')
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM id' + tox_id + ';')
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

    def messages_getter(self, tox_id):
        return History.MessageGetter(self._name, tox_id)

    class MessageGetter(object):
        def __init__(self, name, tox_id):
            chdir(settings.ProfileHelper.get_path())
            self._db = connect(name + '.hstr')
            self._cursor = self._db.cursor()
            self._cursor.execute('SELECT message, owner, unix_time, message_type FROM id' + tox_id +
                                 ' ORDER BY unix_time DESC;')

        def get_one(self):
            return self._cursor.fetchone()

        def get_all(self):
            return self._cursor.fetchall()

        def get(self, count):
            return self._cursor.fetchmany(count)

        def __del__(self):
            self._db.close()
