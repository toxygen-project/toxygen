from sqlite3 import connect
from user_data import settings
from os import chdir
import os.path


PAGE_SIZE = 42

TIMEOUT = 11

SAVE_MESSAGES = 500

MESSAGE_OWNER = {
    'ME': 0,
    'FRIEND': 1,
    'NOT_SENT': 2,
    'GC_PEER': 3
}

# TODO: unique message id and ngc support, profile name as db name


class Database:

    def __init__(self, name, toxes):
        self._name = name
        self._toxes = toxes
        chdir(settings.ProfileManager.get_path())
        path = settings.ProfileManager.get_path() + self._name + '.hstr'
        if os.path.exists(path):
            try:
                with open(path, 'rb') as fin:
                    data = fin.read()
                if toxes.is_data_encrypted(data):
                    data = toxes.pass_decrypt(data)
                    with open(path, 'wb') as fout:
                        fout.write(data)
            except:
                os.remove(path)
        db = connect(name + '.hstr', timeout=TIMEOUT)
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS friends('
                       '    tox_id TEXT PRIMARY KEY'
                       ')')
        db.close()

    def save(self):
        if self._toxes.has_password():
            path = settings.ProfileManager.get_path() + self._name + '.hstr'
            with open(path, 'rb') as fin:
                data = fin.read()
            data = self._toxes.pass_encrypt(bytes(data))
            with open(path, 'wb') as fout:
                fout.write(data)

    def export(self, directory):
        path = settings.ProfileManager.get_path() + self._name + '.hstr'
        new_path = directory + self._name + '.hstr'
        with open(path, 'rb') as fin:
            data = fin.read()
        if self._toxes.has_password():
            data = self._toxes.pass_encrypt(data)
        with open(new_path, 'wb') as fout:
            fout.write(data)

    def add_friend_to_db(self, tox_id):
        chdir(settings.ProfileManager.get_path())
        db = connect(self._name + '.hstr', timeout=TIMEOUT)
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
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def delete_friend_from_db(self, tox_id):
        chdir(settings.ProfileManager.get_path())
        db = connect(self._name + '.hstr', timeout=TIMEOUT)
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM friends WHERE tox_id=?;', (tox_id, ))
            cursor.execute('DROP TABLE id' + tox_id + ';')
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def friend_exists_in_db(self, tox_id):
        chdir(settings.ProfileManager.get_path())
        db = connect(self._name + '.hstr', timeout=TIMEOUT)
        cursor = db.cursor()
        cursor.execute('SELECT 0 FROM friends WHERE tox_id=?', (tox_id, ))
        result = cursor.fetchone()
        db.close()
        return result is not None

    def save_messages_to_db(self, tox_id, messages_iter):
        chdir(settings.ProfileManager.get_path())
        db = connect(self._name + '.hstr', timeout=TIMEOUT)
        try:
            cursor = db.cursor()
            cursor.executemany('INSERT INTO id' + tox_id + '(message, owner, unix_time, message_type) '
                               'VALUES (?, ?, ?, ?);', messages_iter)
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def update_messages(self, tox_id, unsent_time):
        chdir(settings.ProfileManager.get_path())
        db = connect(self._name + '.hstr', timeout=TIMEOUT)
        try:
            cursor = db.cursor()
            cursor.execute('UPDATE id' + tox_id + ' SET owner = 0 '
                           'WHERE unix_time < ' + str(unsent_time) + ' AND owner = 2;')
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def delete_message(self, tox_id, message_id):
        chdir(settings.ProfileManager.get_path())
        db = connect(self._name + '.hstr', timeout=TIMEOUT)
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM id' + tox_id + ' WHERE unix_time < ' + end + ' AND unix_time > ' +
                           start + ';')
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def delete_messages(self, tox_id):
        chdir(settings.ProfileManager.get_path())
        db = connect(self._name + '.hstr', timeout=TIMEOUT)
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM id' + tox_id + ';')
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def messages_getter(self, tox_id):
        return Database.MessageGetter(self._name, tox_id)

    class MessageGetter:

        def __init__(self, name, tox_id):
            self._count = 0
            self._name = name
            self._tox_id = tox_id
            self._db = self._cursor = None

        def connect(self):
            chdir(settings.ProfileManager.get_path())
            self._db = connect(self._name + '.hstr', timeout=TIMEOUT)
            self._cursor = self._db.cursor()
            self._cursor.execute('SELECT message, owner, unix_time, message_type FROM id' + self._tox_id +
                                 ' ORDER BY unix_time DESC;')

        def disconnect(self):
            self._db.close()

        def get_one(self):
            self.connect()
            self.skip()
            data = self._cursor.fetchone()
            self._count += 1
            self.disconnect()
            return data

        def get_all(self):
            self.connect()
            data = self._cursor.fetchall()
            self.disconnect()
            self._count = len(data)
            return data

        def get(self, count):
            self.connect()
            self.skip()
            data = self._cursor.fetchmany(count)
            self.disconnect()
            self._count += len(data)
            return data

        def skip(self):
            if self._count:
                self._cursor.fetchmany(self._count)

        def delete_one(self):
            if self._count:
                self._count -= 1
