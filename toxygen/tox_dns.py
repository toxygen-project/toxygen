import json
import urllib.request
from util import log
import settings
try:
    from PySide import QtNetwork, QtCore
except:
    from PyQt4 import QtNetwork, QtCore


def tox_dns(email):
    """
    TOX DNS 4
    :param email: data like 'groupbot@toxme.io'
    :return: tox id on success else None
    """
    site = email.split('@')[1]
    data = {"action": 3, "name": "{}".format(email)}
    urls = ('https://{}/api'.format(site), 'http://{}/api'.format(site))
    s = settings.Settings.get_instance()
    if not s['proxy_type']:  # no proxy
        for url in urls:
            try:
                return send_request(url, data)
            except Exception as ex:
                log('TOX DNS ERROR: ' + str(ex))
    else:  # proxy
        netman = QtNetwork.QNetworkAccessManager()
        proxy = QtNetwork.QNetworkProxy()
        proxy.setType(QtNetwork.QNetworkProxy.Socks5Proxy if s['proxy_type'] == 2 else QtNetwork.QNetworkProxy.HttpProxy)
        proxy.setHostName(s['proxy_host'])
        proxy.setPort(s['proxy_port'])
        netman.setProxy(proxy)
        for url in urls:
            try:
                request = QtNetwork.QNetworkRequest(url)
                request.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, "application/json")
                reply = netman.post(request, bytes(json.dumps(data), 'utf-8'))

                while not reply.isFinished():
                    QtCore.QThread.msleep(1)
                    QtCore.QCoreApplication.processEvents()
                data = bytes(reply.readAll().data())
                result = json.loads(str(data, 'utf-8'))
                if not result['c']:
                    return result['tox_id']
            except Exception as ex:
                log('TOX DNS ERROR: ' + str(ex))

    return None  # error


def send_request(url, data):
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(req, bytes(json.dumps(data), 'utf-8'))
    res = json.loads(str(response.read(), 'utf-8'))
    if not res['c']:
        return res['tox_id']
    else:
        raise LookupError()
