import util
import os
import settings
import platform
import urllib
try:
    from PySide import QtNetwork, QtCore
except ImportError:
    from PyQt4 import QtNetwork, QtCore
import subprocess


def connection_available():
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)  # google.com
        return True
    except:
        return False


def check_for_updates():
    current_version = util.program_version
    major, minor, patch = list(map(lambda x: int(x), current_version.split('.')))
    versions = generate_versions(major, minor, patch)
    for version in versions:
        if send_request(version):
            return version
    return None  # no new version was found


def is_from_sources():
    return __file__.endswith('.py')


def test_url(version):
    return 'https://github.com/toxygen-project/toxygen/releases/tag/v' + version


def get_url(version):
    if is_from_sources():
        return 'https://github.com/toxygen-project/toxygen/archive/v' + version + '.zip'
    else:
        name = 'toxygen_windows.zip' if platform.system() == 'Windows' else 'toxygen_linux.tar.gz'
        return 'https://github.com/toxygen-project/toxygen/releases/tag/v{}/{}'.format(version, name)


def get_params(url, version):
    if is_from_sources():
        return ['python3', 'toxygen_updater.py', url, version]
    elif platform.system() == 'Windows':
        return ['run', 'toxygen_updater.exe', url, version]
    else:
        return ['./toxygen_updater', url, version]


def download(version):
    os.chdir(util.curr_directory())
    url = get_url(version)
    params = get_params(url, version)
    try:
        subprocess.Popen(params)
    except Exception as ex:
        util.log('Exception: running updater failed with ' + str(ex))


def send_request(version):
    s = settings.Settings.get_instance()
    netman = QtNetwork.QNetworkAccessManager()
    proxy = QtNetwork.QNetworkProxy()
    if s['proxy_type']:
        proxy.setType(QtNetwork.QNetworkProxy.Socks5Proxy if s['proxy_type'] == 2 else QtNetwork.QNetworkProxy.HttpProxy)
        proxy.setHostName(s['proxy_host'])
        proxy.setPort(s['proxy_port'])
        netman.setProxy(proxy)
    url = test_url(version)
    try:
        request = QtNetwork.QNetworkRequest(url)
        reply = netman.get(request)
        while not reply.isFinished():
            QtCore.QThread.msleep(1)
            QtCore.QCoreApplication.processEvents()
        attr = reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        return 200 <= attr < 300
    except Exception as ex:
        util.log('TOXYGEN UPDATER ERROR: ' + str(ex))
        return False


def generate_versions(major, minor, patch):
    new_major = '.'.join([str(major + 1), '0', '0'])
    new_minor = '.'.join([str(major), str(minor + 1), '0'])
    new_patch = '.'.join([str(major), str(minor), str(patch + 1)])
    return new_major, new_minor, new_patch
