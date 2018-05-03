from sqlite3 import connect
import os.path
import util.util as util


TIMEOUT = 11

SAVE_MESSAGES = 500

MESSAGE_AUTHOR = {
    'ME': 0,
    'FRIEND': 1,
    'NOT_SENT': 2,
    'GC_PEER': 3
}

CONTACT_TYPE = {
    'FRIEND': 0,
    'GC_PEER': 1,
    'GC_PEER_PRIVATE': 2
}


class Database:

    def __init__(self, path, toxes):
        self._path, self._toxes = path, toxes
        self._name = os.path.basename(path)
        if os.path.exists(path):
            try:
                with open(path, 'rb') as fin:
                    data = fin.read()
                if toxes.is_data_encrypted(data):
                    data = toxes.pass_decrypt(data)
                    with open(path, 'wb') as fout:
                        fout.write(data)
            except Exception as ex:
                util.log('Db reading error: ' + str(ex))
                os.remove(path)
        db = self._connect()
        cursor = db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS contacts ('
                       '    tox_id TEXT PRIMARY KEY,'
                       '    contact_type INTEGER'
                       ')')
        db.close()

    def _connect(self):
        return connect(self._path, timeout=TIMEOUT)

    # -----------------------------------------------------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------------------------------------------------

    def save(self):
        if self._toxes.has_password():
            with open(self._path, 'rb') as fin:
                data = fin.read()
            data = self._toxes.pass_encrypt(bytes(data))
            with open(self._path, 'wb') as fout:
                fout.write(data)

    def export(self, directory):
        new_path = util.join_path(directory, self._name)
        with open(self._path, 'rb') as fin:
            data = fin.read()
        if self._toxes.has_password():
            data = self._toxes.pass_encrypt(data)
        with open(new_path, 'wb') as fout:
            fout.write(data)

    def add_friend_to_db(self, tox_id):
        db = self._connect()
        try:
            cursor = db.cursor()
            cursor.execute('INSERT INTO contacts VALUES (?);', (tox_id, ))
            cursor.execute('CREATE TABLE id' + tox_id + '('
                           '    id INTEGER PRIMARY KEY,'
                           '    message_id INTEGER,'
                           '    author_name TEXT,'
                           '    message TEXT,'
                           '    author INTEGER,'
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
        db = self._connect()
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM contacts WHERE tox_id=?;', (tox_id, ))
            cursor.execute('DROP TABLE id' + tox_id + ';')
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def friend_exists_in_db(self, tox_id):
        db = self._connect()
        cursor = db.cursor()
        cursor.execute('SELECT 1 FROM contacts WHERE tox_id=?', (tox_id, ))
        result = cursor.fetchone()
        db.close()
        return result is not None

    def save_messages_to_db(self, tox_id, messages_iter):
        db = self._connect()
        try:
            cursor = db.cursor()
            cursor.executemany('INSERT INTO id' + tox_id +
                               '(message, message_id, author_name, author, unix_time, message_type) ' +
                               'VALUES (?, ?, ?, ?, ?, ?);', messages_iter)
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def update_messages(self, tox_id, message_id):
        db = self._connect()
        try:
            cursor = db.cursor()
            cursor.execute('UPDATE id' + tox_id + ' SET author = 0 '
                           'WHERE message_id = ' + str(message_id) + ' AND author = 2;')
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def delete_message(self, tox_id, unique_id):
        db = self._connect()
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM id' + tox_id + ' WHERE id = ' + str(unique_id) + ';')
            db.commit()
        except:
            print('Database is locked!')
            db.rollback()
        finally:
            db.close()

    def delete_messages(self, tox_id):
        db = self._connect()
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
        if not self.friend_exists_in_db(tox_id):
            self.add_friend_to_db(tox_id)

        return Database.MessageGetter(self._path, tox_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Messages loading
    # -----------------------------------------------------------------------------------------------------------------

    class MessageGetter:

        def __init__(self, path, tox_id):
            self._count = 0
            self._path = path
            self._tox_id = tox_id
            self._db = self._cursor = None

        def _connect(self):
            self._db = connect(self._path, timeout=TIMEOUT)
            self._cursor = self._db.cursor()
            self._cursor.execute('SELECT id, message_id, message, author, unix_time, message_type FROM id' +
                                 self._tox_id + ' ORDER BY unix_time DESC;')

        def _disconnect(self):
            self._db.close()

        def get_one(self):
            return self.get(1)

        def get_all(self):
            self._connect()
            data = self._cursor.fetchall()
            self._disconnect()
            self._count = len(data)
            return data

        def get(self, count):
            self._connect()
            self.skip()
            data = self._cursor.fetchmany(count)
            self._disconnect()
            self._count += len(data)
            return data

        def skip(self):
            if self._count:
                self._cursor.fetchmany(self._count)

        def delete_one(self):
            if self._count:
                self._count -= 1
