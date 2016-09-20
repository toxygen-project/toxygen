import util
import requests


def check_for_updates():
    current_version = util.program_version
    major, minor, patch = list(map(lambda x: int(x), current_version.split('.')))
    versions = generate_versions(major, minor, patch)
    for version in versions:
        if send_request(version):
            return version
    return None


def send_request(version):
    # TODO: proxy support
    request = requests.get('https://github.com/toxygen-project/toxygen/releases/tag/v' + version)
    return request.status_code == 200


def generate_versions(major, minor, patch):
    new_major = '.'.join([str(major + 1), '0', '0'])
    new_minor = '.'.join([str(major), str(minor + 1), '0'])
    new_patch = '.'.join([str(major), str(minor), str(patch + 1)])
    return new_major, new_minor, new_patch