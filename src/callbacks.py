# TODO: add all callbacks (replace test callbacks and use wrappers)


def self_connection_status(a, b, c):
    print 'WOW, it works!'
    print 'Status: ', str(b)


def friend_status(a, b, c, d):
    print "Friend connected! Friend's data: ", str(a), str(b), str(c)


def friend_message(a, b, c, d, e, f):
    print 'Message: ', unicode(d, "utf-8")


def init_callbacks(tox):
    tox.callback_friend_status(friend_status, 0)
    tox.callback_friend_message(friend_message, 0)
    tox.callback_self_connection_status(self_connection_status, 0)
