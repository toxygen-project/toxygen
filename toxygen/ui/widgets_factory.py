from ui.main_screen_widgets import *
from ui.menu import *


class WidgetsFactory:

    def __init__(self, settings, profile, contacts_manager, file_transfer_handler, smiley_loader):
        self._settings = settings
        self._profile = profile
        self._contacts_manager = contacts_manager
        self._file_transfer_handler = file_transfer_handler
        self._smiley_loader = smiley_loader

    def create_screenshot_window(self, *args):
        return ScreenShotWindow(self._file_transfer_handler, *args)

    def create_smiley_window(self, parent):
        return SmileyWindow(parent, self._smiley_loader)

    def create_welcome_window(self):
        return WelcomeScreen(self._settings)

    def create_profile_settings_window(self):
        return ProfileSettings(self._profile)

    def create_network_settings_window(self):
        return NetworkSettings(self._settings, self._profile.reset)
