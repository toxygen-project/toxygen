import json
import urllib.request
from util import log


def tox_dns(email):
    """
    TOX DNS 4
    :param email: data like 'groupbot@toxme.io'
    :return: tox id on success else None
    """
    site = email.split('@')[1]
    data = {"action": 3, "name": "{}".format(email)}
    for url in ('https://{}/api'.format(site), 'http://{}/api'.format(site)):
        try:
            return send_request(url, data)
        except Exception as ex:  # try http
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
