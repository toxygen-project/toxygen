TOX_USER_STATUS = {
    'NONE': 0,
    'AWAY': 1,
    'BUSY': 2,
}

TOX_MESSAGE_TYPE = {
    'NORMAL': 0,
    'ACTION': 1,
}

TOX_PROXY_TYPE = {
    'NONE': 0,
    'HTTP': 1,
    'SOCKS5': 2,
}

TOX_SAVEDATA_TYPE = {
    'NONE': 0,
    'TOX_SAVE': 1,
    'SECRET_KEY': 2,
}

TOX_ERR_OPTIONS_NEW = {
    'OK': 0,
    'MALLOC': 1,
}

TOX_ERR_NEW = {
    'OK': 0,
    'NULL': 1,
    'MALLOC': 2,
    'PORT_ALLOC': 3,
    'PROXY_BAD_TYPE': 4,
    'PROXY_BAD_HOST': 5,
    'PROXY_BAD_PORT': 6,
    'PROXY_NOT_FOUND': 7,
    'LOAD_ENCRYPTED': 8,
    'LOAD_BAD_FORMAT': 9,
}

TOX_ERR_BOOTSTRAP = {
    'OK': 0,
    'NULL': 1,
    'BAD_HOST': 2,
    'BAD_PORT': 3,
}

TOX_CONNECTION = {
    'NONE': 0,
    'TCP': 1,
    'UDP': 2,
}

TOX_ERR_SET_INFO = {
    'OK': 0,
    'NULL': 1,
    'TOO_LONG': 2,
}

TOX_ERR_FRIEND_ADD = {
    'OK': 0,
    'NULL': 1,
    'TOO_LONG': 2,
    'NO_MESSAGE': 3,
    'OWN_KEY': 4,
    'ALREADY_SENT': 5,
    'BAD_CHECKSUM': 6,
    'SET_NEW_NOSPAM': 7,
    'MALLOC': 8,
}

TOX_ERR_FRIEND_DELETE = {
    'OK': 0,
    'FRIEND_NOT_FOUND': 1,
}

TOX_ERR_FRIEND_BY_PUBLIC_KEY = {
    'OK': 0,
    'NULL': 1,
    'NOT_FOUND': 2,
}

TOX_ERR_FRIEND_GET_PUBLIC_KEY = {
    'OK': 0,
    'FRIEND_NOT_FOUND': 1,
}

TOX_ERR_FRIEND_GET_LAST_ONLINE = {
    'OK': 0,
    'FRIEND_NOT_FOUND': 1,
}

TOX_ERR_FRIEND_QUERY = {
    'OK': 0,
    'NULL': 1,
    'FRIEND_NOT_FOUND': 2,
}

TOX_ERR_SET_TYPING = {
    'OK': 0,
    'FRIEND_NOT_FOUND': 1,
}

TOX_ERR_FRIEND_SEND_MESSAGE = {
    'OK': 0,
    'NULL': 1,
    'FRIEND_NOT_FOUND': 2,
    'FRIEND_NOT_CONNECTED': 3,
    'SENDQ': 4,
    'TOO_LONG': 5,
    'EMPTY': 6,
}

TOX_FILE_KIND = {
    'DATA': 0,
    'AVATAR': 1,
}

TOX_FILE_CONTROL = {
    'RESUME': 0,
    'PAUSE': 1,
    'CANCEL': 2,
}

TOX_ERR_FILE_CONTROL = {
    'OK': 0,
    'FRIEND_NOT_FOUND': 1,
    'FRIEND_NOT_CONNECTED': 2,
    'NOT_FOUND': 3,
    'NOT_PAUSED': 4,
    'DENIED': 5,
    'ALREADY_PAUSED': 6,
    'SENDQ': 7,
}

TOX_ERR_FILE_SEEK = {
    'OK': 0,
    'FRIEND_NOT_FOUND': 1,
    'FRIEND_NOT_CONNECTED': 2,
    'NOT_FOUND': 3,
    'DENIED': 4,
    'INVALID_POSITION': 5,
    'SENDQ': 6,
}

TOX_ERR_FILE_GET = {
    'OK': 0,
    'NULL': 1,
    'FRIEND_NOT_FOUND': 2,
    'NOT_FOUND': 3,
}

TOX_ERR_FILE_SEND = {
    'OK': 0,
    'NULL': 1,
    'FRIEND_NOT_FOUND': 2,
    'FRIEND_NOT_CONNECTED': 3,
    'NAME_TOO_LONG': 4,
    'TOO_MANY': 5,
}

TOX_ERR_FILE_SEND_CHUNK = {
    'OK': 0,
    'NULL': 1,
    'FRIEND_NOT_FOUND': 2,
    'FRIEND_NOT_CONNECTED': 3,
    'NOT_FOUND': 4,
    'NOT_TRANSFERRING': 5,
    'INVALID_LENGTH': 6,
    'SENDQ': 7,
    'WRONG_POSITION': 8,
}

TOX_ERR_FRIEND_CUSTOM_PACKET = {
    'OK': 0,
    'NULL': 1,
    'FRIEND_NOT_FOUND': 2,
    'FRIEND_NOT_CONNECTED': 3,
    'INVALID': 4,
    'EMPTY': 5,
    'TOO_LONG': 6,
    'SENDQ': 7,
}

TOX_ERR_GET_PORT = {
    'OK': 0,
    'NOT_BOUND': 1,
}

TOX_GROUP_PRIVACY_STATE = {

    #
    # The group is considered to be public. Anyone may join the group using the Chat ID.
    #
    # If the group is in this state, even if the Chat ID is never explicitly shared
    # with someone outside of the group, information including the Chat ID, IP addresses,
    # and peer ID's (but not Tox ID's) is visible to anyone with access to a node
    # storing a DHT entry for the given group.
    #
    'TOX_GROUP_PRIVACY_STATE_PUBLIC': 0,

    #
    # The group is considered to be private. The only way to join the group is by having
    # someone in your contact list send you an invite.
    #
    # If the group is in this state, no group information (mentioned above) is present in the DHT;
    # the DHT is not used for any purpose at all. If a public group is set to private,
    # all DHT information related to the group will expire shortly.
    #
    'TOX_GROUP_PRIVACY_STATE_PRIVATE': 1
}

TOX_GROUP_ROLE = {

    #
    # May kick and ban all other peers as well as set their role to anything (except founder).
    # Founders may also set the group password, toggle the privacy state, and set the peer limit.
    #
    'TOX_GROUP_ROLE_FOUNDER': 0,

    #
    # May kick, ban and set the user and observer roles for peers below this role.
    # May also set the group topic.
    #
    'TOX_GROUP_ROLE_MODERATOR': 1,

    #
    # May communicate with other peers normally.
    #
    'TOX_GROUP_ROLE_USER': 2,

    #
    # May observe the group and ignore peers; may not communicate with other peers or with the group.
    #
    'TOX_GROUP_ROLE_OBSERVER': 3
}

TOX_ERR_GROUP_NEW = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_NEW_OK': 0,

    #
    # The group name exceeded TOX_GROUP_MAX_GROUP_NAME_LENGTH.
    #
    'TOX_ERR_GROUP_NEW_TOO_LONG': 1,

    #
    # group_name is NULL or length is zero.
    #
    'TOX_ERR_GROUP_NEW_EMPTY': 2,

    #
    # TOX_GROUP_PRIVACY_STATE is an invalid type.
    #
    'TOX_ERR_GROUP_NEW_PRIVACY': 3,

    #
    # The group instance failed to initialize.
    #
    'TOX_ERR_GROUP_NEW_INIT': 4,

    #
    # The group state failed to initialize. This usually indicates that something went wrong
    # related to cryptographic signing.
    #
    'TOX_ERR_GROUP_NEW_STATE': 5,

    #
    # The group failed to announce to the DHT. This indicates a network related error.
    #
    'TOX_ERR_GROUP_NEW_ANNOUNCE': 6,
}

TOX_ERR_GROUP_JOIN = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_JOIN_OK': 0,

    #
    # The group instance failed to initialize.
    #
    'TOX_ERR_GROUP_JOIN_INIT': 1,

    #
    # The chat_id pointer is set to NULL or a group with chat_id already exists. This usually
    # happens if the client attempts to create multiple sessions for the same group.
    #
    'TOX_ERR_GROUP_JOIN_BAD_CHAT_ID': 2,

    #
    # Password length exceeded TOX_GROUP_MAX_PASSWORD_SIZE.
    #
    'TOX_ERR_GROUP_JOIN_TOO_LONG': 3,
}

TOX_ERR_GROUP_RECONNECT = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_RECONNECT_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_RECONNECT_GROUP_NOT_FOUND': 1,
}

TOX_ERR_GROUP_LEAVE = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_LEAVE_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_LEAVE_GROUP_NOT_FOUND': 1,

    #
    # Message length exceeded 'TOX_GROUP_MAX_PART_LENGTH.
    #
    'TOX_ERR_GROUP_LEAVE_TOO_LONG': 2,

    #
    # The parting packet failed to send.
    #
    'TOX_ERR_GROUP_LEAVE_FAIL_SEND': 3,

    #
    # The group chat instance failed to be deleted. This may occur due to memory related errors.
    #
    'TOX_ERR_GROUP_LEAVE_DELETE_FAIL': 4,
}

TOX_ERR_GROUP_SELF_QUERY = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_SELF_QUERY_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_SELF_QUERY_GROUP_NOT_FOUND': 1,
}


TOX_ERR_GROUP_SELF_NAME_SET = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_SELF_NAME_SET_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_SELF_NAME_SET_GROUP_NOT_FOUND': 1,

    #
    # Name length exceeded 'TOX_MAX_NAME_LENGTH.
    #
    'TOX_ERR_GROUP_SELF_NAME_SET_TOO_LONG': 2,

    #
    # The length given to the set function is zero or name is a NULL pointer.
    #
    'TOX_ERR_GROUP_SELF_NAME_SET_INVALID': 3,

    #
    # The name is already taken by another peer in the group.
    #
    'TOX_ERR_GROUP_SELF_NAME_SET_TAKEN': 4,

    #
    # The packet failed to send.
    #
    'TOX_ERR_GROUP_SELF_NAME_SET_FAIL_SEND': 5
}

TOX_ERR_GROUP_SELF_STATUS_SET = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_SELF_STATUS_SET_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_SELF_STATUS_SET_GROUP_NOT_FOUND': 1,

    #
    # An invalid type was passed to the set function.
    #
    'TOX_ERR_GROUP_SELF_STATUS_SET_INVALID': 2,

    #
    # The packet failed to send.
    #
    'TOX_ERR_GROUP_SELF_STATUS_SET_FAIL_SEND': 3
}

TOX_ERR_GROUP_PEER_QUERY = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_PEER_QUERY_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_PEER_QUERY_GROUP_NOT_FOUND': 1,

    #
    # The ID passed did not designate a valid peer.
    #
    'TOX_ERR_GROUP_PEER_QUERY_PEER_NOT_FOUND': 2
}

TOX_ERR_GROUP_STATE_QUERIES = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_STATE_QUERIES_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_STATE_QUERIES_GROUP_NOT_FOUND': 1
}


TOX_ERR_GROUP_TOPIC_SET = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_TOPIC_SET_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_TOPIC_SET_GROUP_NOT_FOUND': 1,

    #
    # Topic length exceeded 'TOX_GROUP_MAX_TOPIC_LENGTH.
    #
    'TOX_ERR_GROUP_TOPIC_SET_TOO_LONG': 2,

    #
    # The caller does not have the required permissions to set the topic.
    #
    'TOX_ERR_GROUP_TOPIC_SET_PERMISSIONS': 3,

    #
    # The packet could not be created. This error is usually related to cryptographic signing.
    #
    'TOX_ERR_GROUP_TOPIC_SET_FAIL_CREATE': 4,

    #
    # The packet failed to send.
    #
    'TOX_ERR_GROUP_TOPIC_SET_FAIL_SEND': 5
}

TOX_ERR_GROUP_SEND_MESSAGE = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_SEND_MESSAGE_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_SEND_MESSAGE_GROUP_NOT_FOUND': 1,

    #
    # Message length exceeded 'TOX_MAX_MESSAGE_LENGTH.
    #
    'TOX_ERR_GROUP_SEND_MESSAGE_TOO_LONG': 2,

    #
    # The message pointer is null or length is zero.
    #
    'TOX_ERR_GROUP_SEND_MESSAGE_EMPTY': 3,

    #
    # The message type is invalid.
    #
    'TOX_ERR_GROUP_SEND_MESSAGE_BAD_TYPE': 4,

    #
    # The caller does not have the required permissions to send group messages.
    #
    'TOX_ERR_GROUP_SEND_MESSAGE_PERMISSIONS': 5,

    #
    # Packet failed to send.
    #
    'TOX_ERR_GROUP_SEND_MESSAGE_FAIL_SEND': 6
}

TOX_ERR_GROUP_SEND_PRIVATE_MESSAGE = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_SEND_PRIVATE_MESSAGE_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_SEND_PRIVATE_MESSAGE_GROUP_NOT_FOUND': 1,

    #
    # The ID passed did not designate a valid peer.
    #
    'TOX_ERR_GROUP_SEND_PRIVATE_MESSAGE_PEER_NOT_FOUND': 2,

    #
    # Message length exceeded 'TOX_MAX_MESSAGE_LENGTH.
    #
    'TOX_ERR_GROUP_SEND_PRIVATE_MESSAGE_TOO_LONG': 3,

    #
    # The message pointer is null or length is zero.
    #
    'TOX_ERR_GROUP_SEND_PRIVATE_MESSAGE_EMPTY': 4,

    #
    # The caller does not have the required permissions to send group messages.
    #
    'TOX_ERR_GROUP_SEND_PRIVATE_MESSAGE_PERMISSIONS': 5,

    #
    # Packet failed to send.
    #
    'TOX_ERR_GROUP_SEND_PRIVATE_MESSAGE_FAIL_SEND': 6
}

TOX_ERR_GROUP_SEND_CUSTOM_PACKET = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_SEND_CUSTOM_PACKET_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_SEND_CUSTOM_PACKET_GROUP_NOT_FOUND': 1,

    #
    # Message length exceeded 'TOX_MAX_MESSAGE_LENGTH.
    #
    'TOX_ERR_GROUP_SEND_CUSTOM_PACKET_TOO_LONG': 2,

    #
    # The message pointer is null or length is zero.
    #
    'TOX_ERR_GROUP_SEND_CUSTOM_PACKET_EMPTY': 3,

    #
    # The caller does not have the required permissions to send group messages.
    #
    'TOX_ERR_GROUP_SEND_CUSTOM_PACKET_PERMISSIONS': 4
}

TOX_ERR_GROUP_INVITE_FRIEND = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_INVITE_FRIEND_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_INVITE_FRIEND_GROUP_NOT_FOUND': 1,

    #
    # The friend number passed did not designate a valid friend.
    #
    'TOX_ERR_GROUP_INVITE_FRIEND_FRIEND_NOT_FOUND': 2,

    #
    # Creation of the invite packet failed. This indicates a network related error.
    #
    'TOX_ERR_GROUP_INVITE_FRIEND_INVITE_FAIL': 3,

    #
    # Packet failed to send.
    #
    'TOX_ERR_GROUP_INVITE_FRIEND_FAIL_SEND': 4
}

TOX_ERR_GROUP_INVITE_ACCEPT = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_INVITE_ACCEPT_OK': 0,

    #
    # The invite data is not in the expected format.
    #
    'TOX_ERR_GROUP_INVITE_ACCEPT_BAD_INVITE': 1,

    #
    # The group instance failed to initialize.
    #
    'TOX_ERR_GROUP_INVITE_ACCEPT_INIT_FAILED': 2,

    #
    # Password length exceeded 'TOX_GROUP_MAX_PASSWORD_SIZE.
    #
    'TOX_ERR_GROUP_INVITE_ACCEPT_TOO_LONG': 3
}

TOX_GROUP_JOIN_FAIL = {

    #
    # You are using the same nickname as someone who is already in the group.
    #
    'TOX_GROUP_JOIN_FAIL_NAME_TAKEN': 0,

    #
    # The group peer limit has been reached.
    #
    'TOX_GROUP_JOIN_FAIL_PEER_LIMIT': 1,

    #
    # You have supplied an invalid password.
    #
    'TOX_GROUP_JOIN_FAIL_INVALID_PASSWORD': 2,

    #
    # The join attempt failed due to an unspecified error. This often occurs when the group is
    # not found in the DHT.
    #
    'TOX_GROUP_JOIN_FAIL_UNKNOWN': 3
}

TOX_ERR_GROUP_FOUNDER_SET_PASSWORD = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PASSWORD_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PASSWORD_GROUP_NOT_FOUND': 1,

    #
    # The caller does not have the required permissions to set the password.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PASSWORD_PERMISSIONS': 2,

    #
    # Password length exceeded 'TOX_GROUP_MAX_PASSWORD_SIZE.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PASSWORD_TOO_LONG': 3,

    #
    # The packet failed to send.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PASSWORD_FAIL_SEND': 4
}

TOX_ERR_GROUP_FOUNDER_SET_PRIVACY_STATE = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PRIVACY_STATE_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PRIVACY_STATE_GROUP_NOT_FOUND': 1,

    #
    # 'TOX_GROUP_PRIVACY_STATE is an invalid type.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PRIVACY_STATE_INVALID': 2,

    #
    # The caller does not have the required permissions to set the privacy state.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PRIVACY_STATE_PERMISSIONS': 3,

    #
    # The privacy state could not be set. This may occur due to an error related to
    # cryptographic signing of the new shared state.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PRIVACY_STATE_FAIL_SET': 4,

    #
    # The packet failed to send.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PRIVACY_STATE_FAIL_SEND': 5
}

TOX_ERR_GROUP_FOUNDER_SET_PEER_LIMIT = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PEER_LIMIT_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PEER_LIMIT_GROUP_NOT_FOUND': 1,

    #
    # The caller does not have the required permissions to set the peer limit.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PEER_LIMIT_PERMISSIONS': 2,

    #
    # The peer limit could not be set. This may occur due to an error related to
    # cryptographic signing of the new shared state.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PEER_LIMIT_FAIL_SET': 3,

    #
    # The packet failed to send.
    #
    'TOX_ERR_GROUP_FOUNDER_SET_PEER_LIMIT_FAIL_SEND': 4
}

TOX_ERR_GROUP_TOGGLE_IGNORE = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_TOGGLE_IGNORE_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_TOGGLE_IGNORE_GROUP_NOT_FOUND': 1,

    #
    # The ID passed did not designate a valid peer.
    #
    'TOX_ERR_GROUP_TOGGLE_IGNORE_PEER_NOT_FOUND': 2
}

TOX_ERR_GROUP_MOD_SET_ROLE = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_MOD_SET_ROLE_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_MOD_SET_ROLE_GROUP_NOT_FOUND': 1,

    #
    # The ID passed did not designate a valid peer. Note: you cannot set your own role.
    #
    'TOX_ERR_GROUP_MOD_SET_ROLE_PEER_NOT_FOUND': 2,

    #
    # The caller does not have the required permissions for this action.
    #
    'TOX_ERR_GROUP_MOD_SET_ROLE_PERMISSIONS': 3,

    #
    # The role assignment is invalid. This will occur if you try to set a peer's role to
    # the role they already have.
    #
    'TOX_ERR_GROUP_MOD_SET_ROLE_ASSIGNMENT': 4,

    #
    # The role was not successfully set. This may occur if something goes wrong with role setting': ,
    # or if the packet fails to send.
    #
    'TOX_ERR_GROUP_MOD_SET_ROLE_FAIL_ACTION': 5
}

TOX_ERR_GROUP_MOD_REMOVE_PEER = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_PEER_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_PEER_GROUP_NOT_FOUND': 1,

    #
    # The ID passed did not designate a valid peer.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_PEER_PEER_NOT_FOUND': 2,

    #
    # The caller does not have the required permissions for this action.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_PEER_PERMISSIONS': 3,

    #
    # The peer could not be removed from the group.
    #
    # If a ban was set': , this error indicates that the ban entry could not be created.
    # This is usually due to the peer's IP address already occurring in the ban list. It may also
    # be due to the entry containing invalid peer information': , or a failure to cryptographically
    # authenticate the entry.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_PEER_FAIL_ACTION': 4,

    #
    # The packet failed to send.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_PEER_FAIL_SEND': 5
}

TOX_ERR_GROUP_MOD_REMOVE_BAN = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_BAN_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_BAN_GROUP_NOT_FOUND': 1,

    #
    # The caller does not have the required permissions for this action.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_BAN_PERMISSIONS': 2,

    #
    # The ban entry could not be removed. This may occur if ban_id does not designate
    # a valid ban entry.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_BAN_FAIL_ACTION': 3,

    #
    # The packet failed to send.
    #
    'TOX_ERR_GROUP_MOD_REMOVE_BAN_FAIL_SEND': 4
}

TOX_GROUP_MOD_EVENT = {

    #
    # A peer has been kicked from the group.
    #
    'TOX_GROUP_MOD_EVENT_KICK': 0,

    #
    # A peer has been banned from the group.
    #
    'TOX_GROUP_MOD_EVENT_BAN': 1,

    #
    # A peer as been given the observer role.
    #
    'TOX_GROUP_MOD_EVENT_OBSERVER': 2,

    #
    # A peer has been given the user role.
    #
    'TOX_GROUP_MOD_EVENT_USER': 3,

    #
    # A peer has been given the moderator role.
    #
    'TOX_GROUP_MOD_EVENT_MODERATOR': 4,
}

TOX_ERR_GROUP_BAN_QUERY = {

    #
    # The function returned successfully.
    #
    'TOX_ERR_GROUP_BAN_QUERY_OK': 0,

    #
    # The group number passed did not designate a valid group.
    #
    'TOX_ERR_GROUP_BAN_QUERY_GROUP_NOT_FOUND': 1,

    #
    # The ban_id does not designate a valid ban list entry.
    #
    'TOX_ERR_GROUP_BAN_QUERY_BAD_ID': 2,
}

TOX_PUBLIC_KEY_SIZE = 32

TOX_ADDRESS_SIZE = TOX_PUBLIC_KEY_SIZE + 6

TOX_MAX_FRIEND_REQUEST_LENGTH = 1016

TOX_MAX_MESSAGE_LENGTH = 1372

TOX_GROUP_MAX_TOPIC_LENGTH = 512

TOX_GROUP_MAX_PART_LENGTH = 128

TOX_GROUP_MAX_GROUP_NAME_LENGTH = 48

TOX_GROUP_MAX_PASSWORD_SIZE = 32

TOX_GROUP_CHAT_ID_SIZE = 32

TOX_GROUP_PEER_PUBLIC_KEY_SIZE = 32

TOX_MAX_NAME_LENGTH = 128

TOX_MAX_STATUS_MESSAGE_LENGTH = 1007

TOX_SECRET_KEY_SIZE = 32

TOX_FILE_ID_LENGTH = 32

TOX_HASH_LENGTH = 32

TOX_MAX_CUSTOM_PACKET_SIZE = 1373
