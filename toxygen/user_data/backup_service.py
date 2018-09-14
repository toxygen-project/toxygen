import os.path
from utils.util import get_profile_name_from_path, join_path


class BackupService:

    def __init__(self, settings, profile_manager):
        self._settings = settings
        self._profile_name = get_profile_name_from_path(profile_manager.get_path())

        settings.settings_saved_event.add_callback(self._settings_saved)
        profile_manager.profile_saved_event.add_callback(self._profile_saved)

    def _settings_saved(self, data):
        if not self._check_if_should_save_backup():
            return

        file_path = join_path(self._get_backup_directory(), self._profile_name + '.json')

        with open(file_path, 'wt') as fl:
            fl.write(data)

    def _profile_saved(self, data):
        if not self._check_if_should_save_backup():
            return

        file_path = join_path(self._get_backup_directory(), self._profile_name + '.tox')

        with open(file_path, 'wb') as fl:
            fl.write(data)

    def _check_if_should_save_backup(self):
        backup_directory = self._get_backup_directory()
        if backup_directory is None:
            return False

        return os.path.exists(backup_directory) and os.path.isdir(backup_directory)

    def _get_backup_directory(self):
        return self._settings['backup_directory']
