import json
import urllib.request
from util import log
import settings


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
    if s['proxy_type'] != 2:  # no proxy or http proxy
        proxy = s['proxy_host'] + ':' + s['proxy_port'] if s['proxy_type'] else None
        for url in urls:
            try:
                return send_request(url, data, proxy)
            except Exception as ex:
                log('TOX DNS ERROR: ' + str(ex))
    else:  # SOCKS5 proxy
        try:
            import socks
            import socket
            import requests

            socks.set_default_proxy(socks.SOCKS5, s['proxy_host'], s['proxy_port'])
            socket.socket = socks.socksocket
            for url in urls:
                try:
                    r = requests.get(url)
                    res = json.loads(r.text)
                    if not res['c']:
                        return res['tox_id']
                    else:
                        raise LookupError()
                except Exception as ex:
                    log('TOX DNS ERROR: ' + str(ex))
        except:
            pass
    return None  # error


def send_request(url, data, proxy):
    req = urllib.request.Request(url)
    if proxy is not None:
        req.set_proxy(proxy, 'http')
    req.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(req, bytes(json.dumps(data), 'utf-8'))
    res = json.loads(str(response.read(), 'utf-8'))
    if not res['c']:
        return res['tox_id']
    else:
        raise LookupError()
