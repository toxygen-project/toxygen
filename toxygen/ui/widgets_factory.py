from ui.main_screen_widgets import *
from ui.menu import *
from ui.groups_widgets import *


class WidgetsFactory:

    def __init__(self, settings, profile, profile_manager, contacts_manager, file_transfer_handler, smiley_loader,
                 plugin_loader, toxes, version, groups_service):
        self._settings = settings
        self._profile = profile
        self._profile_manager = profile_manager
        self._contacts_manager = contacts_manager
        self._file_transfer_handler = file_transfer_handler
        self._smiley_loader = smiley_loader
        self._plugin_loader = plugin_loader
        self._toxes = toxes
        self._version = version
        self._groups_service = groups_service

    def create_screenshot_window(self, *args):
        return ScreenShotWindow(self._file_transfer_handler, self._contacts_manager, *args)

    def create_smiley_window(self, parent):
        return SmileyWindow(parent, self._smiley_loader)

    def create_welcome_window(self):
        return WelcomeScreen(self._settings)

    def create_profile_settings_window(self):
        return ProfileSettings(self._profile, self._profile_manager,  self._settings, self._toxes)

    def create_network_settings_window(self):
        return NetworkSettings(self._settings, self._profile.reset)

    def create_audio_settings_window(self):
        return AudioSettings(self._settings)

    def create_video_settings_window(self):
        return VideoSettings(self._settings)

    def create_update_settings_window(self):
        return UpdateSettings(self._settings)

    def create_plugins_settings_window(self):
        return PluginsSettings(self._plugin_loader)

    def create_add_contact_window(self, tox_id):
        return AddContact(self._settings, self._contacts_manager, tox_id)

    def create_welcome_window(self):
        return WelcomeScreen(self._settings)

    def create_privacy_settings_window(self):
        return PrivacySettings(self._contacts_manager, self._settings)

    def create_interface_settings_window(self):
        return InterfaceSettings(self._settings, self._smiley_loader)

    def create_notification_settings_window(self):
        return NotificationsSettings(self._settings)

    def create_smiley_window(self, parent):
        return SmileyWindow(parent, self._smiley_loader)

    def create_sticker_window(self):
        return StickerWindow(self._file_transfer_handler, self._contacts_manager)

    def create_group_screen_window(self):
        return CreateGroupScreen(self._groups_service)

    def create_join_group_screen_window(self):
        return JoinGroupScreen(self._groups_service)
