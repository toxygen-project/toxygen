import util
import settings
try:
    from PySide import QtNetwork, QtCore
except:
    from PyQt4 import QtNetwork, QtCore


def check_for_updates():
    current_version = util.program_version
    major, minor, patch = list(map(lambda x: int(x), current_version.split('.')))
    versions = generate_versions(major, minor, patch)
    for version in versions:
        if send_request(version):
            return version
    return None  # no new version was found


def get_url(version):
    return 'https://github.com/toxygen-project/toxygen/releases/tag/v' + version


def download(version):
    s = settings.Settings.get_instance()
    if s['update']:
        netman = QtNetwork.QNetworkAccessManager()
        proxy = QtNetwork.QNetworkProxy()
        if s['proxy_type']:
            proxy.setType(
                QtNetwork.QNetworkProxy.Socks5Proxy if s['proxy_type'] == 2 else QtNetwork.QNetworkProxy.HttpProxy)
            proxy.setHostName(s['proxy_host'])
            proxy.setPort(s['proxy_port'])
            netman.setProxy(proxy)
        url = get_url(version)
        try:
            request = QtNetwork.QNetworkRequest(url)
            reply = netman.get(request)
            while not reply.isFinished():
                QtCore.QThread.msleep(1)
            data = bytes(reply.readAll().data())
            with open('toxygen.zip', 'wb') as fl:
                fl.write(data)
        except Exception as ex:
            util.log('Downloading new version of Toxygen failed with exception: ' + str(ex))


def send_request(version):
    s = settings.Settings.get_instance()
    netman = QtNetwork.QNetworkAccessManager()
    proxy = QtNetwork.QNetworkProxy()
    if s['proxy_type']:
        proxy.setType(QtNetwork.QNetworkProxy.Socks5Proxy if s['proxy_type'] == 2 else QtNetwork.QNetworkProxy.HttpProxy)
        proxy.setHostName(s['proxy_host'])
        proxy.setPort(s['proxy_port'])
        netman.setProxy(proxy)
    url = get_url(version)
    try:
        request = QtNetwork.QNetworkRequest(url)
        reply = netman.get(request)
        while not reply.isFinished():
            QtCore.QThread.msleep(1)
        return reply.attribute() == 200
    except Exception as ex:
        util.log('TOXYGEN UPDATER ERROR: ' + str(ex))
        return False


def generate_versions(major, minor, patch):
    new_major = '.'.join([str(major + 1), '0', '0'])
    new_minor = '.'.join([str(major), str(minor + 1), '0'])
    new_patch = '.'.join([str(major), str(minor), str(patch + 1)])
    return new_major, new_minor, new_patch
