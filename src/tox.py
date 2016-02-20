# -*- coding: utf-8 -*-
from ctypes import *
from platform import system
from toxcore_enums_and_consts import *
import os


class ToxOptions(Structure):
    _fields_ = [
        ('ipv6_enabled', c_bool),
        ('udp_enabled', c_bool),
        ('proxy_type', c_int),
        ('proxy_host', c_char_p),
        ('proxy_port', c_uint16),
        ('start_port', c_uint16),
        ('end_port', c_uint16),
        ('tcp_port', c_uint16),
        ('savedata_type', c_int),
        ('savedata_data', c_char_p),
        ('savedata_length', c_size_t)
    ]


class LibToxCore(object):
    def __init__(self):
        if system() == 'Linux':
            temp = os.path.dirname(os.path.abspath(__file__)) + '/libs/'
            os.chdir(temp)
            self._libtoxcore = CDLL(temp + 'libtoxcore.so')
        elif system() == 'Windows':
            self._libtoxcore = CDLL('libs/libtox.dll')
        else:
            raise OSError('Unknown system.')
        
    def __getattr__(self, item):
        return self._libtoxcore.__getattr__(item)
        

class Tox(object):
    libtoxcore = LibToxCore()
    
    def __init__(self, tox_options=None, tox_pointer=None):
        """
        Creates and initialises a new Tox instance with the options passed.

        This function will bring the instance into a valid state. Running the event loop with a new instance will
        operate correctly.

        :param tox_options: An options object. If this parameter is None, the default options are used.
        :param tox_pointer: Tox instance pointer (c_void_p). If this parameter is not None, tox_options will be ignored.
        """
        if tox_pointer is not None:
            self._tox_pointer = tox_pointer
        else:
            tox_err_new = c_int()
            Tox.libtoxcore.tox_new.restype = POINTER(c_void_p)
            self._tox_pointer = Tox.libtoxcore.tox_new(tox_options, addressof(tox_err_new))
            tox_err_new = tox_err_new.value
            if tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_NULL']:
                raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
            elif tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_MALLOC']:
                raise MemoryError('The function was unable to allocate enough '
                                  'memory to store the internal structures for the Tox object.')
            elif tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_PORT_ALLOC']:
                raise MemoryError('The function was unable to bind to a port. This may mean that all ports have already'
                                  ' been bound, e.g. by other Tox instances, or it may mean a permission error. You may'
                                  ' be able to gather more information from errno.')
            elif tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_PROXY_BAD_TYPE']:
                raise ArgumentError('proxy_type was invalid.')
            elif tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_PROXY_BAD_HOST']:
                raise ArgumentError('proxy_type was valid but the proxy_host passed had an invalid format or was NULL.')
            elif tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_PROXY_BAD_PORT']:
                raise ArgumentError('proxy_type was valid, but the proxy_port was invalid.')
            elif tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_PROXY_NOT_FOUND']:
                raise ArgumentError('The proxy address passed could not be resolved.')
            elif tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_LOAD_ENCRYPTED']:
                raise ArgumentError('The byte array to be loaded contained an encrypted save.')
            elif tox_err_new == TOX_ERR_NEW['TOX_ERR_NEW_LOAD_BAD_FORMAT']:
                raise ArgumentError('The data format was invalid. This can happen when loading data that was saved by'
                                    ' an older version of Tox, or when the data has been corrupted. When loading from'
                                    ' badly formatted data, some data may have been loaded, and the rest is discarded.'
                                    ' Passing an invalid length parameter also causes this error.')

    # -----------------------------------------------------------------------------------------------------------------
    # Startup options
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def options_default(tox_options):
        """
        Initialises a Tox_Options object with the default options.

        The result of this function is independent of the original options. All values will be overwritten, no values
        will be read (so it is permissible to pass an uninitialised object).

        If options is NULL, this function has no effect.

        :param tox_options: A POINTER(ToxOptions) to options object to be filled with default options.
        """
        Tox.libtoxcore.tox_options_default(tox_options)

    @staticmethod
    def options_new():
        """
        Allocates a new Tox_Options object and initialises it with the default options. This function can be used to
        preserve long term ABI compatibility by giving the responsibility of allocation and deallocation to the Tox
        library.

        Objects returned from this function must be freed using the tox_options_free function.

        :return: A POINTER(ToxOptions) to new ToxOptions object with default options or NULL on failure.
        """
        tox_err_options_new = c_int()
        Tox.libtoxcore.tox_options_new.restype = POINTER(ToxOptions)
        result = Tox.libtoxcore.tox_options_new(addressof(tox_err_options_new))
        tox_err_options_new = tox_err_options_new.value
        if tox_err_options_new == TOX_ERR_OPTIONS_NEW['TOX_ERR_OPTIONS_NEW_OK']:
            return result
        elif tox_err_options_new == TOX_ERR_OPTIONS_NEW['TOX_ERR_OPTIONS_NEW_MALLOC']:
            raise MemoryError('The function failed to allocate enough memory for the options struct.')

    @staticmethod
    def options_free(tox_options):
        """
        Releases all resources associated with an options objects.

        Passing a pointer that was not returned by tox_options_new results in undefined behaviour.

        :param tox_options: A POINTER(ToxOptions) to new ToxOptions object
        """
        Tox.libtoxcore.tox_options_free(tox_options)

    # -----------------------------------------------------------------------------------------------------------------
    # Creation and destruction
    # -----------------------------------------------------------------------------------------------------------------

    def get_savedata_size(self):
        """
        Calculates the number of bytes required to store the tox instance with tox_get_savedata.
        This function cannot fail. The result is always greater than 0.

        :return: number of bytes
        """
        return Tox.libtoxcore.tox_get_savedata_size(self._tox_pointer)

    def get_savedata(self, savedata=None):
        """
        Store all information associated with the tox instance to a byte array.

        :param savedata: pointer (c_char_p) to a memory region large enough to store the tox instance data.
        Call tox_get_savedata_size to find the number of bytes required. If this parameter is None, this function
        allocates memory for the tox instance data.
        :return: pointer (c_char_p) to a memory region with the tox instance data
        """
        if savedata is None:
            savedata_size = self.get_savedata_size()
            savedata = create_string_buffer(savedata_size)
        Tox.libtoxcore.tox_get_savedata(self._tox_pointer, savedata)
        return savedata

    # -----------------------------------------------------------------------------------------------------------------
    # Connection lifecycle and event loop
    # -----------------------------------------------------------------------------------------------------------------

    def bootstrap(self, address, port, public_key):
        """
        Sends a "get nodes" request to the given bootstrap node with IP, port, and public key to setup connections.

        This function will attempt to connect to the node using UDP. You must use this function even if
        Tox_Options.udp_enabled was set to false.

        :param address: The hostname or IP address (IPv4 or IPv6) of the node.
        :param port: The port on the host on which the bootstrap Tox instance is listening.
        :param public_key: The long term public key of the bootstrap node (TOX_PUBLIC_KEY_SIZE bytes).
        :return: True on success.
        """
        tox_err_bootstrap = c_int()
        result = Tox.libtoxcore.tox_bootstrap(self._tox_pointer, c_char_p(address), c_uint16(port),
                                              c_char_p(public_key), addressof(tox_err_bootstrap))
        tox_err_bootstrap = tox_err_bootstrap.value
        if tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_OK']:
            return bool(result)
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_BAD_HOST']:
            raise ArgumentError('The address could not be resolved to an IP '
                                'address, or the IP address passed was invalid.')
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_BAD_PORT']:
            raise ArgumentError('The port passed was invalid. The valid port range is (1, 65535).')

    def add_tcp_relay(self, address, port, public_key):
        """
        Adds additional host:port pair as TCP relay.

        This function can be used to initiate TCP connections to different ports on the same bootstrap node, or to add
         TCP relays without using them as bootstrap nodes.

        :param address: The hostname or IP address (IPv4 or IPv6) of the TCP relay.
        :param port: The port on the host on which the TCP relay is listening.
        :param public_key: The long term public key of the TCP relay (TOX_PUBLIC_KEY_SIZE bytes).
        :return: True on success.
        """
        tox_err_bootstrap = c_int()
        result = Tox.libtoxcore.tox_add_tcp_relay(self._tox_pointer, c_char_p(address), c_uint16(port),
                                                  c_char_p(public_key), addressof(tox_err_bootstrap))
        tox_err_bootstrap = tox_err_bootstrap.value
        if tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_OK']:
            return bool(result)
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_BAD_HOST']:
            raise ArgumentError('The address could not be resolved to an IP '
                                'address, or the IP address passed was invalid.')
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_BAD_PORT']:
            raise ArgumentError('The port passed was invalid. The valid port range is (1, 65535).')

    def self_get_connection_status(self):
        """
        Return whether we are connected to the DHT. The return value is equal to the last value received through the
        `self_connection_status` callback.

        :return: TOX_CONNECTION
        """
        return Tox.libtoxcore.tox_self_get_connection_status(self._tox_pointer)

    def callback_self_connection_status(self, callback, user_data):
        """
        Set the callback for the `self_connection_status` event. Pass None to unset.

        This event is triggered whenever there is a change in the DHT connection state. When disconnected, a client may
        choose to call tox_bootstrap again, to reconnect to the DHT. Note that this state may frequently change for
        short amounts of time. Clients should therefore not immediately bootstrap on receiving a disconnect.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        TOX_CONNECTION (c_int),
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        tox_self_connection_status_cb = CFUNCTYPE(None, c_void_p, c_int, c_void_p)
        c_callback = tox_self_connection_status_cb(callback)
        Tox.libtoxcore.tox_callback_self_connection_status(self._tox_pointer, c_callback, user_data)

    def iteration_interval(self):
        """
        Return the time in milliseconds before tox_iterate() should be called again for optimal performance.
        :return: time in milliseconds
        """
        return Tox.libtoxcore.tox_iteration_interval(self._tox_pointer)

    def iterate(self):
        """
        The main loop that needs to be run in intervals of tox_iteration_interval() milliseconds.
        """
        Tox.libtoxcore.tox_iterate(self._tox_pointer)

    # -----------------------------------------------------------------------------------------------------------------
    # Internal client information (Tox address/id)
    # -----------------------------------------------------------------------------------------------------------------

    def self_get_address(self, address=None):
        """
        Writes the Tox friend address of the client to a byte array. The address is not in human-readable format. If a
         client wants to display the address, formatting is required.

        :param address: pointer (c_char_p) to a memory region of at least TOX_ADDRESS_SIZE bytes. If this parameter is
        None, this function allocates memory for address.
        :return: pointer (c_char_p) to a memory region with the Tox friend address
        """
        if address is None:
            address = create_string_buffer(TOX_ADDRESS_SIZE)
        Tox.libtoxcore.tox_self_get_address(self._tox_pointer, address)
        return address

    def self_set_nospam(self, nospam):
        """
        Set the 4-byte nospam part of the address.

        :param nospam: Any 32 bit unsigned integer.
        """
        Tox.libtoxcore.tox_self_set_nospam(self._tox_pointer, c_uint32(nospam))

    def self_get_nospam(self):
        """
        Get the 4-byte nospam part of the address.

        :return: nospam part of the address
        """
        return Tox.libtoxcore.tox_self_get_nospam(self._tox_pointer)

    def self_get_public_key(self, public_key=None):
        """
        Copy the Tox Public Key (long term) from the Tox object.

        :param public_key: A memory region of at least TOX_PUBLIC_KEY_SIZE bytes. If this parameter is NULL, this
        function allocates memory for Tox Public Key.
        :return: pointer (c_char_p) to a memory region with the Tox Public Key
        """
        if public_key is None:
            public_key = create_string_buffer(TOX_PUBLIC_KEY_SIZE)
        Tox.libtoxcore.tox_self_get_address(self._tox_pointer, public_key)
        return public_key

    def self_get_secret_key(self, secret_key=None):
        """
        Copy the Tox Secret Key from the Tox object.

        :param secret_key: pointer (c_char_p) to a memory region of at least TOX_SECRET_KEY_SIZE bytes. If this parameter is NULL, this
        function allocates memory for Tox Secret Key.
        :return: pointer (c_char_p) to a memory region with the Tox Secret Key
        """
        if secret_key is None:
            secret_key = create_string_buffer(TOX_PUBLIC_KEY_SIZE)
        Tox.libtoxcore.tox_self_get_secret_key(self._tox_pointer, secret_key)
        return secret_key

    # -----------------------------------------------------------------------------------------------------------------
    # User-visible client information (nickname/status)
    # -----------------------------------------------------------------------------------------------------------------

    def self_set_name(self, name):
        """
        Set the nickname for the Tox client.

        Nickname length cannot exceed TOX_MAX_NAME_LENGTH. If length is 0, the name parameter is ignored
        (it can be None), and the nickname is set back to empty.
        :param name: New nickname.
        :return: True on success.
        """
        tox_err_set_info = c_int()
        result = Tox.libtoxcore.tox_self_set_name(self._tox_pointer, c_char_p(name),
                                                  c_size_t(len(name)), addressof(tox_err_set_info))
        tox_err_set_info = tox_err_set_info.value
        if tox_err_set_info == TOX_ERR_SET_INFO['TOX_ERR_SET_INFO_OK']:
            return bool(result)
        elif tox_err_set_info == TOX_ERR_SET_INFO['TOX_ERR_SET_INFO_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_set_info == TOX_ERR_SET_INFO['TOX_ERR_SET_INFO_TOO_LONG']:
            raise ArgumentError('Information length exceeded maximum permissible size.')

    def self_get_name_size(self):
        """
        Return the length of the current nickname as passed to tox_self_set_name.

        If no nickname was set before calling this function, the name is empty, and this function returns 0.

        :return: length of the current nickname
        """
        return Tox.libtoxcore.tox_self_get_name_size(self._tox_pointer)

    def self_get_name(self, name=None):
        """
        Write the nickname set by tox_self_set_name to a byte array.

        If no nickname was set before calling this function, the name is empty, and this function has no effect.

        Call tox_self_get_name_size to find out how much memory to allocate for the result.

        :param name: pointer (c_char_p) to a memory region location large enough to hold the nickname. If this parameter
        is NULL, the function allocates memory for the nickname.
        :return: pointer (c_char_p) to a memory region with the nickname
        """
        if name is None:
            name = create_string_buffer(self.self_get_name_size())
        Tox.libtoxcore.tox_self_get_name(self._tox_pointer, name)
        return name

    def self_set_status_message(self, status_message):
        """
        Set the client's status message.

        Status message length cannot exceed TOX_MAX_STATUS_MESSAGE_LENGTH. If length is 0, the status parameter is
        ignored, and the user status is set back to empty.

        :param status_message: new status message
        :return: True on success.
        """
        tox_err_set_info = c_int()
        result = Tox.libtoxcore.tox_self_set_status_message(self._tox_pointer, c_char_p(status_message),
                                                            c_size_t(len(status_message)), addressof(tox_err_set_info))
        tox_err_set_info = tox_err_set_info.value
        if tox_err_set_info == TOX_ERR_SET_INFO['TOX_ERR_SET_INFO_OK']:
            return bool(result)
        elif tox_err_set_info == TOX_ERR_SET_INFO['TOX_ERR_SET_INFO_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_set_info == TOX_ERR_SET_INFO['TOX_ERR_SET_INFO_TOO_LONG']:
            raise ArgumentError('Information length exceeded maximum permissible size.')

    def self_get_status_message_size(self):
        """
        Return the length of the current status message as passed to tox_self_set_status_message.

        If no status message was set before calling this function, the status is empty, and this function returns 0.

        :return: length of the current status message
        """
        return Tox.libtoxcore.tox_self_get_status_message_size(self._tox_pointer)

    def self_get_status_message(self, status_message=None):
        """
        Write the status message set by tox_self_set_status_message to a byte array.

        If no status message was set before calling this function, the status is empty, and this function has no effect.

        Call tox_self_get_status_message_size to find out how much memory to allocate for the result.

        :param status_message: pointer (c_char_p) to a valid memory location large enough to hold the status message.
        If this parameter is None, the function allocates memory for the status message.
        :return: pointer (c_char_p) to a memory region with the status message
        """
        if status_message is None:
            status_message = create_string_buffer(self.self_get_status_message_size())
        Tox.libtoxcore.tox_self_get_status_message(self._tox_pointer, status_message)
        return status_message

    def self_set_status(self, status):
        """
        Set the client's user status.

        :param status: One of the user statuses listed in the enumeration TOX_USER_STATUS.
        """
        Tox.libtoxcore.tox_self_set_status(self._tox_pointer, c_int(status))

    def self_get_status(self):
        """
        Returns the client's user status.

        :return: client's user status
        """
        return Tox.libtoxcore.tox_self_get_status(self._tox_pointer)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend list management
    # -----------------------------------------------------------------------------------------------------------------

    def friend_add(self, address, message):
        """
        Add a friend to the friend list and send a friend request.

        A friend request message must be at least 1 byte long and at most TOX_MAX_FRIEND_REQUEST_LENGTH.

        Friend numbers are unique identifiers used in all functions that operate on friends. Once added, a friend number
        is stable for the lifetime of the Tox object. After saving the state and reloading it, the friend numbers may
        not be the same as before. Deleting a friend creates a gap in the friend number set, which is filled by the next
        adding of a friend. Any pattern in friend numbers should not be relied on.

        If more than INT32_MAX friends are added, this function causes undefined behaviour.

        :param address: The address of the friend (returned by tox_self_get_address of the friend you wish to add) it
        must be TOX_ADDRESS_SIZE bytes.
        :param message: The message that will be sent along with the friend request.
        :return: the friend number on success, UINT32_MAX on failure.
        """
        tox_err_friend_add = c_int()
        result = Tox.libtoxcore.tox_friend_add(self._tox_pointer, c_char_p(address), c_char_p(message),
                                               c_size_t(len(message)), addressof(tox_err_friend_add))
        tox_err_friend_add = tox_err_friend_add.value
        if tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_OK']:
            return result
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_TOO_LONG']:
            raise ArgumentError('The length of the friend request message exceeded TOX_MAX_FRIEND_REQUEST_LENGTH.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_NO_MESSAGE']:
            raise ArgumentError('The friend request message was empty. This, and the TOO_LONG code will never be'
                                ' returned from tox_friend_add_norequest.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_OWN_KEY']:
            raise ArgumentError('The friend address belongs to the sending client.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_ALREADY_SENT']:
            raise ArgumentError('A friend request has already been sent, or the address belongs to a friend that is'
                                ' already on the friend list.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_BAD_CHECKSUM']:
            raise ArgumentError('The friend address checksum failed.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_SET_NEW_NOSPAM']:
            raise ArgumentError('The friend was already there, but the nospam value was different.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_MALLOC']:
            raise MemoryError('A memory allocation failed when trying to increase the friend list size.')

    def friend_add_norequest(self, public_key):
        """
        Add a friend without sending a friend request.

        This function is used to add a friend in response to a friend request. If the client receives a friend request,
        it can be reasonably sure that the other client added this client as a friend, eliminating the need for a friend
        request.

        This function is also useful in a situation where both instances are controlled by the same entity, so that this
        entity can perform the mutual friend adding. In this case, there is no need for a friend request, either.

        :param public_key: A byte array of length TOX_PUBLIC_KEY_SIZE containing the Public Key (not the Address) of the
        friend to add.
        :return: the friend number on success, UINT32_MAX on failure.
        """
        tox_err_friend_add = c_int()
        result = Tox.libtoxcore.tox_friend_add(self._tox_pointer, c_char_p(public_key), addressof(tox_err_friend_add))
        tox_err_friend_add = tox_err_friend_add.value
        if tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_OK']:
            return result
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_TOO_LONG']:
            raise ArgumentError('The length of the friend request message exceeded TOX_MAX_FRIEND_REQUEST_LENGTH.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_NO_MESSAGE']:
            raise ArgumentError('The friend request message was empty. This, and the TOO_LONG code will never be'
                                ' returned from tox_friend_add_norequest.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_OWN_KEY']:
            raise ArgumentError('The friend address belongs to the sending client.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_ALREADY_SENT']:
            raise ArgumentError('A friend request has already been sent, or the address belongs to a friend that is'
                                ' already on the friend list.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_BAD_CHECKSUM']:
            raise ArgumentError('The friend address checksum failed.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_SET_NEW_NOSPAM']:
            raise ArgumentError('The friend was already there, but the nospam value was different.')
        elif tox_err_friend_add == TOX_ERR_FRIEND_ADD['TOX_ERR_FRIEND_ADD_MALLOC']:
            raise MemoryError('A memory allocation failed when trying to increase the friend list size.')

    def friend_delete(self, friend_number):
        """
        Remove a friend from the friend list.

        This does not notify the friend of their deletion. After calling this function, this client will appear offline
        to the friend and no communication can occur between the two.

        :param friend_number: Friend number for the friend to be deleted.
        :return: True on success.
        """
        tox_err_friend_delete = c_int()
        result = Tox.libtoxcore.tox_friend_delete(self._tox_pointer, c_uint32(friend_number),
                                                  addressof(tox_err_friend_delete))
        tox_err_friend_delete = tox_err_friend_delete.value
        if tox_err_friend_delete == TOX_ERR_FRIEND_DELETE['TOX_ERR_FRIEND_DELETE_OK']:
            return bool(result)
        elif tox_err_friend_delete == TOX_ERR_FRIEND_DELETE['TOX_ERR_FRIEND_DELETE_FRIEND_NOT_FOUND']:
            raise ArgumentError('There was no friend with the given friend number. No friends were deleted.')

    # -----------------------------------------------------------------------------------------------------------------
    # Friend list queries
    # -----------------------------------------------------------------------------------------------------------------

    def friend_by_public_key(self, public_key):
        """
        Return the friend number associated with that Public Key.

        :param public_key: A byte array containing the Public Key.
        :return: friend number
        """
        tox_err_friend_by_public_key = c_int()
        result = Tox.libtoxcore.tox_friend_by_public_key(self._tox_pointer, c_char_p(public_key),
                                                         addressof(tox_err_friend_by_public_key))
        tox_err_friend_by_public_key = tox_err_friend_by_public_key.value
        if tox_err_friend_by_public_key == TOX_ERR_FRIEND_BY_PUBLIC_KEY['TOX_ERR_FRIEND_BY_PUBLIC_KEY_OK']:
            return result
        elif tox_err_friend_by_public_key == TOX_ERR_FRIEND_BY_PUBLIC_KEY['TOX_ERR_FRIEND_BY_PUBLIC_KEY_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_friend_by_public_key == TOX_ERR_FRIEND_BY_PUBLIC_KEY['TOX_ERR_FRIEND_BY_PUBLIC_KEY_NOT_FOUND']:
            raise ArgumentError('No friend with the given Public Key exists on the friend list.')

    def friend_exists(self, friend_number):
        """
        Checks if a friend with the given friend number exists and returns true if it does.
        """
        return bool(Tox.libtoxcore.tox_friend_by_public_key(self._tox_pointer, c_uint32(friend_number)))

    def self_get_friend_list_size(self):
        """
        Return the number of friends on the friend list.

        This function can be used to determine how much memory to allocate for tox_self_get_friend_list.

        :return: number of friends
        """
        return Tox.libtoxcore.tox_self_get_friend_list_size(self._tox_pointer)

    def self_get_friend_list(self, friend_list=None):
        """
        Copy a list of valid friend numbers into an array.

        Call tox_self_get_friend_list_size to determine the number of elements to allocate.

        :param friend_list: pointer (c_char_p) to a memory region with enough space to hold the friend list. If this
        parameter is None, this function allocates memory for the friend list.
        :return: pointer (c_char_p) to a memory region with the friend list
        """
        if friend_list is None:
            friend_list = create_string_buffer(sizeof(c_uint32) * self.self_get_friend_list_size())
            friend_list = POINTER(c_uint32)(friend_list)
        Tox.libtoxcore.tox_self_get_friend_list(self._tox_pointer, friend_list)
        return friend_list

    def friend_get_public_key(self, friend_number, public_key):
        """
        Copies the Public Key associated with a given friend number to a byte array.

        :param friend_number: The friend number you want the Public Key of.
        :param public_key: pointer (c_char_p) to a memory region of at least TOX_PUBLIC_KEY_SIZE bytes. If this
        parameter is None, this function has no effect.
        :return: True on success.
        """
        tox_err_friend_get_public_key = c_int()
        result = Tox.libtoxcore.tox_friend_get_public_key(self._tox_pointer, c_uint32(friend_number),
                                                          c_char_p(public_key),
                                                          addressof(tox_err_friend_get_public_key))
        tox_err_friend_get_public_key = tox_err_friend_get_public_key.value
        if tox_err_friend_get_public_key == TOX_ERR_FRIEND_GET_PUBLIC_KEY['TOX_ERR_FRIEND_GET_PUBLIC_KEY_OK']:
            return bool(result)
        elif tox_err_friend_get_public_key == TOX_ERR_FRIEND_GET_PUBLIC_KEY['TOX_ERR_FRIEND_GET_PUBLIC_KEY_FRIEND_NOT_FOUND']:
            raise ArgumentError('No friend with the given number exists on the friend list.')

    def friend_get_last_online(self, friend_number):
        """
        Return a unix-time timestamp of the last time the friend associated with a given friend number was seen online.
        This function will return UINT64_MAX on error.

        :param friend_number: The friend number you want to query.
        :return: unix-time timestamp
        """
        tox_err_last_online = c_int()
        result = Tox.libtoxcore.tox_friend_get_last_online(self._tox_pointer, c_uint32(friend_number),
                                                           addressof(tox_err_last_online))
        tox_err_last_online = tox_err_last_online.value
        if tox_err_last_online == TOX_ERR_FRIEND_GET_LAST_ONLINE['TOX_ERR_FRIEND_GET_LAST_ONLINE_OK']:
            return result
        elif tox_err_last_online == TOX_ERR_FRIEND_GET_LAST_ONLINE['TOX_ERR_FRIEND_GET_LAST_ONLINE_FRIEND_NOT_FOUND']:
            raise ArgumentError('No friend with the given number exists on the friend list.')

    # -----------------------------------------------------------------------------------------------------------------
    # Friend-specific state queries (can also be received through callbacks)
    # -----------------------------------------------------------------------------------------------------------------

    def friend_get_name_size(self, friend_number):
        """
        Return the length of the friend's name. If the friend number is invalid, the return value is unspecified.

        The return value is equal to the `length` argument received by the last `friend_name` callback.
        """
        tox_err_friend_query = c_int()
        result = Tox.libtoxcore.tox_friend_get_name_size(self._tox_pointer, c_uint32(friend_number),
                                                         addressof(tox_err_friend_query))
        tox_err_friend_query = tox_err_friend_query.value
        if tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_OK']:
            return result
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_NULL']:
            raise ArgumentError('The pointer parameter for storing the query result (name, message) was NULL. Unlike'
                                ' the `_self_` variants of these functions, which have no effect when a parameter is'
                                ' NULL, these functions return an error in that case.')
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number did not designate a valid friend.')

    def friend_get_name(self, friend_number, name):
        """
        Write the name of the friend designated by the given friend number to a byte array.

        Call tox_friend_get_name_size to determine the allocation size for the `name` parameter.

        The data written to `name` is equal to the data received by the last `friend_name` callback.

        :param name: pointer (c_char_p) to a valid memory region large enough to store the friend's name.
        :return: True on success.
        """
        tox_err_friend_query = c_int()
        result = Tox.libtoxcore.tox_friend_get_name(self._tox_pointer, c_uint32(friend_number), name,
                                                    addressof(tox_err_friend_query))
        tox_err_friend_query = tox_err_friend_query.value
        if tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_OK']:
            return bool(result)
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_NULL']:
            raise ArgumentError('The pointer parameter for storing the query result (name, message) was NULL. Unlike'
                                ' the `_self_` variants of these functions, which have no effect when a parameter is'
                                ' NULL, these functions return an error in that case.')
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number did not designate a valid friend.')

    def callback_friend_name(self, callback, user_data):
        """
        Set the callback for the `friend_name` event. Pass None to unset.

        This event is triggered when a friend changes their name.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        The friend number (c_uint32) of the friend whose name changed,
        A byte array (c_char_p) containing the same data as tox_friend_get_name would write to its `name` parameter,
        A value (c_size_t) equal to the return value of tox_friend_get_name_size,
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        tox_friend_name_cb = CFUNCTYPE(None, c_void_p, c_uint32, c_char_p, c_size_t, c_void_p)
        c_callback = tox_friend_name_cb(callback)
        Tox.libtoxcore.tox_callback_friend_name(self._tox_pointer, c_callback, user_data)

    def friend_get_status_message_size(self, friend_number):
        """
        Return the length of the friend's status message. If the friend number is invalid, the return value is SIZE_MAX.

        :return: length of the friend's status message
        """
        tox_err_friend_query = c_int()
        result = Tox.libtoxcore.tox_friend_get_status_message_size(self._tox_pointer, c_uint32(friend_number),
                                                                   addressof(tox_err_friend_query))
        tox_err_friend_query = tox_err_friend_query.value
        if tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_OK']:
            return result
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_NULL']:
            raise ArgumentError('The pointer parameter for storing the query result (name, message) was NULL. Unlike'
                                ' the `_self_` variants of these functions, which have no effect when a parameter is'
                                ' NULL, these functions return an error in that case.')
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number did not designate a valid friend.')

    def friend_get_status_message(self, friend_number, status_message):
        """
        Write the status message of the friend designated by the given friend number to a byte array.

        Call tox_friend_get_status_message_size to determine the allocation size for the `status_name` parameter.

        The data written to `status_message` is equal to the data received by the last `friend_status_message` callback.

        :param friend_number:
        :param status_message: pointer (c_char_p) to a valid memory region large enough to store the friend's status
        message.
        :return: True on success.
        """
        tox_err_friend_query = c_int()
        result = Tox.libtoxcore.tox_friend_get_status_message(self._tox_pointer, c_uint32(friend_number),
                                                              status_message, addressof(tox_err_friend_query))
        tox_err_friend_query = tox_err_friend_query.value
        if tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_OK']:
            return bool(result)
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_NULL']:
            raise ArgumentError('The pointer parameter for storing the query result (name, message) was NULL. Unlike'
                                ' the `_self_` variants of these functions, which have no effect when a parameter is'
                                ' NULL, these functions return an error in that case.')
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number did not designate a valid friend.')

    def callback_friend_status_message(self, callback, user_data):
        """
        Set the callback for the `friend_status_message` event. Pass NULL to unset.

        This event is triggered when a friend changes their status message.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        The friend number (c_uint32) of the friend whose status message changed,
        A byte array (c_char_p) containing the same data as tox_friend_get_status_message would write to its
        `status_message` parameter,
        A value (c_size_t) equal to the return value of tox_friend_get_status_message_size,
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        friend_status_message_cb = CFUNCTYPE(None, c_void_p, c_uint32, c_char_p, c_size_t, c_void_p)
        c_callback = friend_status_message_cb(callback)
        Tox.libtoxcore.tox_callback_friend_status_message(self._tox_pointer, c_callback, c_void_p(user_data))

    def friend_get_status(self, friend_number):
        """
        Return the friend's user status (away/busy/...). If the friend number is invalid, the return value is
        unspecified.

        The status returned is equal to the last status received through the `friend_status` callback.

        :return: TOX_USER_STATUS
        """
        tox_err_friend_query = c_int()
        result = Tox.libtoxcore.tox_friend_get_status(self._tox_pointer, c_uint32(friend_number),
                                                      addressof(tox_err_friend_query))
        tox_err_friend_query = tox_err_friend_query.value
        if tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_OK']:
            return result
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_NULL']:
            raise ArgumentError('The pointer parameter for storing the query result (name, message) was NULL. Unlike'
                                ' the `_self_` variants of these functions, which have no effect when a parameter is'
                                ' NULL, these functions return an error in that case.')
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number did not designate a valid friend.')

    def callback_friend_status(self, callback, user_data):
        """
        Set the callback for the `friend_status` event. Pass None to unset.

        This event is triggered when a friend changes their user status.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        The friend number (c_uint32) of the friend whose user status changed,
        The new user status (TOX_USER_STATUS),
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        tox_friend_status_cb = CFUNCTYPE(None, c_void_p, c_uint32, c_int, c_void_p)
        c_callback = tox_friend_status_cb(callback)
        Tox.libtoxcore.tox_callback_friend_status(self._tox_pointer, c_callback, c_void_p(user_data))

    def friend_get_connection_status(self, friend_number):
        """
        Check whether a friend is currently connected to this client.

        The result of this function is equal to the last value received by the `friend_connection_status` callback.

        :param friend_number: The friend number for which to query the connection status.
        :return: the friend's connection status (TOX_CONNECTION) as it was received through the
        `friend_connection_status` event.
        """
        tox_err_friend_query = c_int()
        result = Tox.libtoxcore.tox_friend_get_connection_status(self._tox_pointer, c_uint32(friend_number),
                                                                 addressof(tox_err_friend_query))
        tox_err_friend_query = tox_err_friend_query.value
        if tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_OK']:
            return result
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_NULL']:
            raise ArgumentError('The pointer parameter for storing the query result (name, message) was NULL. Unlike'
                                ' the `_self_` variants of these functions, which have no effect when a parameter is'
                                ' NULL, these functions return an error in that case.')
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number did not designate a valid friend.')

    def callback_friend_connection_status(self, callback, user_data):
        """
        Set the callback for the `friend_connection_status` event. Pass NULL to unset.

        This event is triggered when a friend goes offline after having been online, or when a friend goes online.

        This callback is not called when adding friends. It is assumed that when adding friends, their connection status
        is initially offline.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        The friend number (c_uint32) of the friend whose connection status changed,
        The result of calling tox_friend_get_connection_status (TOX_CONNECTION) on the passed friend_number,
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        tox_friend_connection_status_cb = CFUNCTYPE(None, c_void_p, c_uint32, c_int, c_void_p)
        c_callback = tox_friend_connection_status_cb(callback)
        Tox.libtoxcore.tox_callback_friend_connection_status(self._tox_pointer, c_callback, c_void_p(user_data))

    def friend_get_typing(self, friend_number):
        """
        Check whether a friend is currently typing a message.

        :param friend_number: The friend number for which to query the typing status.
        :return: true if the friend is typing.
        """
        tox_err_friend_query = c_int()
        result = Tox.libtoxcore.tox_friend_get_typing(self._tox_pointer, c_uint32(friend_number),
                                                      addressof(tox_err_friend_query))
        tox_err_friend_query = tox_err_friend_query.value
        if tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_OK']:
            return bool(result)
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_NULL']:
            raise ArgumentError('The pointer parameter for storing the query result (name, message) was NULL. Unlike'
                                ' the `_self_` variants of these functions, which have no effect when a parameter is'
                                ' NULL, these functions return an error in that case.')
        elif tox_err_friend_query == TOX_ERR_FRIEND_QUERY['TOX_ERR_FRIEND_QUERY_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number did not designate a valid friend.')

    def callback_friend_typing(self, callback, user_data):
        """
        Set the callback for the `friend_typing` event. Pass NULL to unset.

        This event is triggered when a friend starts or stops typing.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        The friend number (c_uint32) of the friend who started or stopped typing,
        The result of calling tox_friend_get_typing (c_bool) on the passed friend_number,
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        tox_friend_typing_cb = CFUNCTYPE(None, c_void_p, c_uint32, c_bool, c_void_p)
        c_callback = tox_friend_typing_cb(callback)
        Tox.libtoxcore.tox_callback_friend_typing(self._tox_pointer, c_callback, c_void_p(user_data))

    # -----------------------------------------------------------------------------------------------------------------
    # Sending private messages
    # -----------------------------------------------------------------------------------------------------------------

    def self_set_typing(self, friend_number, typing):
        """
        Set the client's typing status for a friend.

        The client is responsible for turning it on or off.

        :param friend_number: The friend to which the client is typing a message.
        :param typing: The typing status. True means the client is typing.
        :return: True on success.
        """
        tox_err_set_typing = c_int()
        result = Tox.libtoxcore.tox_friend_delete(self._tox_pointer, c_uint32(friend_number),
                                                  c_bool(typing), addressof(tox_err_set_typing))
        tox_err_set_typing = tox_err_set_typing.value
        if tox_err_set_typing == TOX_ERR_SET_TYPING['TOX_ERR_SET_TYPING_OK']:
            return bool(result)
        elif tox_err_set_typing == TOX_ERR_SET_TYPING['TOX_ERR_SET_TYPING_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend number did not designate a valid friend.')

    def friend_send_message(self, friend_number, message_type, message):
        """
        Send a text chat message to an online friend.

        This function creates a chat message packet and pushes it into the send queue.

        The message length may not exceed TOX_MAX_MESSAGE_LENGTH. Larger messages must be split by the client and sent
        as separate messages. Other clients can then reassemble the fragments. Messages may not be empty.

        The return value of this function is the message ID. If a read receipt is received, the triggered
        `friend_read_receipt` event will be passed this message ID.

        Message IDs are unique per friend. The first message ID is 0. Message IDs are incremented by 1 each time a
        message is sent. If UINT32_MAX messages were sent, the next message ID is 0.

        :param friend_number: The friend number of the friend to send the message to.
        :param message_type: Message type (TOX_MESSAGE_TYPE).
        :param message: A non-None message text.
        :return: message ID
        """
        tox_err_friend_send_message = c_int()
        result = Tox.libtoxcore.tox_friend_send_message(self._tox_pointer, c_uint32(friend_number),
                                                        c_int(message_type), c_char_p(message), c_size_t(len(message)),
                                                        addressof(tox_err_friend_send_message))
        tox_err_friend_send_message = tox_err_friend_send_message.value
        if tox_err_friend_send_message == TOX_ERR_FRIEND_SEND_MESSAGE['TOX_ERR_FRIEND_SEND_MESSAGE_OK']:
            return result
        elif tox_err_friend_send_message == TOX_ERR_FRIEND_SEND_MESSAGE['TOX_ERR_FRIEND_SEND_MESSAGE_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_friend_send_message == TOX_ERR_FRIEND_SEND_MESSAGE['TOX_ERR_FRIEND_SEND_MESSAGE_FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend number did not designate a valid friend.')
        elif tox_err_friend_send_message == TOX_ERR_FRIEND_SEND_MESSAGE['TOX_ERR_FRIEND_SEND_MESSAGE_FRIEND_NOT_CONNECTED']:
            raise ArgumentError('This client is currently not connected to the friend.')
        elif tox_err_friend_send_message == TOX_ERR_FRIEND_SEND_MESSAGE['TOX_ERR_FRIEND_SEND_MESSAGE_SENDQ']:
            raise ArgumentError('An allocation error occurred while increasing the send queue size.')
        elif tox_err_friend_send_message == TOX_ERR_FRIEND_SEND_MESSAGE['TOX_ERR_FRIEND_SEND_MESSAGE_TOO_LONG']:
            raise ArgumentError('Message length exceeded TOX_MAX_MESSAGE_LENGTH.')
        elif tox_err_friend_send_message == TOX_ERR_FRIEND_SEND_MESSAGE['TOX_ERR_FRIEND_SEND_MESSAGE_EMPTY']:
            raise ArgumentError('Attempted to send a zero-length message.')

    def callback_friend_read_receipt(self, callback, user_data):
        """
        Set the callback for the `friend_read_receipt` event. Pass None to unset.

        This event is triggered when the friend receives the message sent with tox_friend_send_message with the
        corresponding message ID.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        The friend number (c_uint32) of the friend who received the message,
        The message ID (c_uint32) as returned from tox_friend_send_message corresponding to the message sent,
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        tox_friend_read_receipt_cb = CFUNCTYPE(None, c_void_p, c_uint32, c_uint32, c_void_p)
        c_callback = tox_friend_read_receipt_cb(callback)
        Tox.libtoxcore.tox_callback_friend_read_receipt(self._tox_pointer, c_callback, c_void_p(user_data))

    # -----------------------------------------------------------------------------------------------------------------
    # Receiving private messages and friend requests
    # -----------------------------------------------------------------------------------------------------------------

    def callback_friend_request(self, callback, user_data):
        """
        Set the callback for the `friend_request` event. Pass None to unset.

        This event is triggered when a friend request is received.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        The Public Key (c_char_p) of the user who sent the friend request,
        The message (c_char_p) they sent along with the request,
        The size (c_size_t) of the message byte array,
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        tox_friend_request_cb = CFUNCTYPE(None, c_void_p, c_char_p, c_char_p, c_size_t, c_void_p)
        c_callback = tox_friend_request_cb(callback)
        Tox.libtoxcore.tox_callback_friend_request(self._tox_pointer, c_callback, c_void_p(user_data))

    def callback_friend_message(self, callback, user_data):
        """
        Set the callback for the `friend_message` event. Pass None to unset.

        This event is triggered when a message from a friend is received.

        :param callback: Python function. Should take pointer (c_void_p) to Tox object,
        The friend number (c_uint32) of the friend who sent the message,
        Message type (TOX_MESSAGE_TYPE),
        The message data (c_char_p) they sent,
        The size (c_size_t) of the message byte array.
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        tox_friend_message_cb = CFUNCTYPE(None, c_void_p, c_uint32, c_int, c_char_p, c_size_t, c_void_p)
        c_callback = tox_friend_message_cb(callback)
        Tox.libtoxcore.tox_callback_friend_message(self._tox_pointer, c_callback, c_void_p(user_data))

    # TODO File transmission: common between sending and receiving

    # TODO File transmission: sending

    # TODO File transmission: receiving

    # TODO Group chat management

    # TODO Group chat message sending and receiving

    # TODO Low-level custom packet sending and receiving

    # TODO Low-level network information

    def __del__(self):
        Tox.libtoxcore.tox_kill(self._tox_pointer)


if __name__ == '__main__':
    options = Tox.options_new()

    print type(options)
    print(options)
