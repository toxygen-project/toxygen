import json
import urllib2
from util import log
# TODO: add TOX DNS 3 support


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
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(data))
    res = json.loads(response.read())
    if not res['c']:
        return res['tox_id']
    else:
        raise LookupError()
