import random
import urllib.request
from utils.util import *
from PyQt5 import QtNetwork, QtCore
import json


DEFAULT_NODES_COUNT = 4


class Node:

    def __init__(self, node):
        self._ip, self._port, self._tox_key = node['ipv4'], node['port'], node['public_key']
        self._priority = random.randint(1, 1000000) if node['status_tcp'] and node['status_udp'] else 0

    def get_priority(self):
        return self._priority

    priority = property(get_priority)

    def get_data(self):
        return self._ip, self._port, self._tox_key


def generate_nodes(nodes_count=DEFAULT_NODES_COUNT):
    with open(_get_nodes_path(), 'rt') as fl:
        json_nodes = json.loads(fl.read())['nodes']
    nodes = map(lambda json_node: Node(json_node), json_nodes)
    nodes = filter(lambda n: n.priority > 0, nodes)
    sorted_nodes = sorted(nodes, key=lambda x: x.priority)
    if nodes_count is not None:
        sorted_nodes = sorted_nodes[-DEFAULT_NODES_COUNT:]
    for node in sorted_nodes:
        yield node.get_data()


def download_nodes_list(settings):
    url = 'https://nodes.tox.chat/json'
    if not settings['download_nodes_list']:
        return

    if not settings['proxy_type']:  # no proxy
        try:
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req)
            result = response.read()
            _save_nodes(result)
        except Exception as ex:
            log('TOX nodes loading error: ' + str(ex))
    else:  # proxy
        netman = QtNetwork.QNetworkAccessManager()
        proxy = QtNetwork.QNetworkProxy()
        proxy.setType(
            QtNetwork.QNetworkProxy.Socks5Proxy if settings['proxy_type'] == 2 else QtNetwork.QNetworkProxy.HttpProxy)
        proxy.setHostName(settings['proxy_host'])
        proxy.setPort(settings['proxy_port'])
        netman.setProxy(proxy)
        try:
            request = QtNetwork.QNetworkRequest()
            request.setUrl(QtCore.QUrl(url))
            reply = netman.get(request)

            while not reply.isFinished():
                QtCore.QThread.msleep(1)
                QtCore.QCoreApplication.processEvents()
            data = bytes(reply.readAll().data())
            _save_nodes(data)
        except Exception as ex:
            log('TOX nodes loading error: ' + str(ex))


def _get_nodes_path():
    return join_path(curr_directory(__file__), 'nodes.json')


def _save_nodes(nodes):
    if not nodes:
        return
    print('Saving nodes...')
    with open(_get_nodes_path(), 'wb') as fl:
        fl.write(nodes)
