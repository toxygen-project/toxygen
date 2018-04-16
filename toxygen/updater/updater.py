import util.util as util
import util.ui as util_ui
import os
from user_data import settings
import platform
import urllib
from PyQt5 import QtNetwork, QtCore
import subprocess


def connection_available():
    try:
        urllib.request.urlopen('http://216.58.192.142', timeout=1)  # google.com
        return True
    except:
        return False


def updater_available():
    if is_from_sources():
        return os.path.exists(util.curr_directory() + '/toxygen_updater.py')
    elif platform.system() == 'Windows':
        return os.path.exists(util.curr_directory() + '/toxygen_updater.exe')
    else:
        return os.path.exists(util.curr_directory() + '/toxygen_updater')


def check_for_updates(current_version, settings):
    major, minor, patch = list(map(lambda x: int(x), current_version.split('.')))
    versions = generate_versions(major, minor, patch)
    for version in versions:
        if send_request(version, settings):
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
        if platform.system() == 'Windows':
            name = 'toxygen_windows.zip'
        elif util.is_64_bit():
            name = 'toxygen_linux_64.tar.gz'
        else:
            name = 'toxygen_linux.tar.gz'
        return 'https://github.com/toxygen-project/toxygen/releases/download/v{}/{}'.format(version, name)


def get_params(url, version):
    if is_from_sources():
        if platform.system() == 'Windows':
            return ['python', 'toxygen_updater.py', url, version]
        else:
            return ['python3', 'toxygen_updater.py', url, version]
    elif platform.system() == 'Windows':
        return [util.curr_directory() + '/toxygen_updater.exe', url, version]
    else:
        return ['./toxygen_updater', url, version]


def download(version):
    os.chdir(util.curr_directory())
    url = get_url(version)
    params = get_params(url, version)
    print('Updating Toxygen')
    util.log('Updating Toxygen')
    try:
        subprocess.Popen(params)
    except Exception as ex:
        util.log('Exception: running updater failed with ' + str(ex))


def send_request(version, settings):
    netman = QtNetwork.QNetworkAccessManager()
    proxy = QtNetwork.QNetworkProxy()
    if settings['proxy_type']:
        proxy.setType(QtNetwork.QNetworkProxy.Socks5Proxy if settings['proxy_type'] == 2 else QtNetwork.QNetworkProxy.HttpProxy)
        proxy.setHostName(settings['proxy_host'])
        proxy.setPort(settings['proxy_port'])
        netman.setProxy(proxy)
    url = test_url(version)
    try:
        request = QtNetwork.QNetworkRequest()
        request.setUrl(QtCore.QUrl(url))
        reply = netman.get(request)
        while not reply.isFinished():
            QtCore.QThread.msleep(1)
            QtCore.QCoreApplication.processEvents()
        attr = reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)
        return attr is not None and 200 <= attr < 300
    except Exception as ex:
        util.log('TOXYGEN UPDATER ERROR: ' + str(ex))
        return False


def generate_versions(major, minor, patch):
    new_major = '.'.join([str(major + 1), '0', '0'])
    new_minor = '.'.join([str(major), str(minor + 1), '0'])
    new_patch = '.'.join([str(major), str(minor), str(patch + 1)])
    return new_major, new_minor, new_patch


def start_update_if_needed(version, settings):
    updating = False
    if settings['update'] and updater_available() and connection_available():  # auto update
        version = check_for_updates(version, settings)
        if version is not None:
            if settings['update'] == 2:
                download(version)
                updating = True
            else:
                reply = QtWidgets.QMessageBox.question(None,
                                                       'Toxygen',
                                                       QtWidgets.QApplication.translate("login",
                                                                                        'Update for Toxygen was found. Download and install it?'),
                                                       QtWidgets.QMessageBox.Yes,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    download(version)
                    updating = True

    return updating
