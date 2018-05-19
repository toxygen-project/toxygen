from PyQt5 import QtWidgets
import utils.ui as util_ui


# -----------------------------------------------------------------------------------------------------------------
# Builder
# -----------------------------------------------------------------------------------------------------------------

def _create_menu(menu_name, parent):
    menu_name = menu_name or ''

    return QtWidgets.QMenu(menu_name) if parent is None else parent.addMenu(menu_name)


class ContactMenuBuilder:

    def __init__(self):
        self._actions = {}
        self._submenus = {}
        self._name = None
        self._index = 0

    def with_name(self, name):
        self._name = name

        return self

    def with_action(self, text, handler):
        self._add_action(text, handler)

        return self

    def with_actions(self, actions):
        for action in actions:
            (text, handler) = action
            self._add_action(text, handler)

        return self

    def with_submenu(self, submenu_builder):
        self._add_submenu(submenu_builder)

        return self

    def with_optional_submenu(self, submenu_builder):
        if submenu_builder is not None:
            self._add_submenu(submenu_builder)

        return self

    def build(self, parent=None):
        menu = _create_menu(self._name, parent)

        for i in range(self._index):
            if i in self._actions:
                text, handler = self._actions[i]
                action = menu.addAction(text)
                action.triggered.connect(handler)
            else:
                submenu_builder = self._submenus[i]
                submenu = submenu_builder.build(menu)
                menu.addMenu(submenu)

        return menu

    def _add_submenu(self, submenu):
        self._submenus[self._index] = submenu
        self._index += 1

    def _add_action(self, text, handler):
        self._actions[self._index] = (text, handler)
        self._index += 1

# -----------------------------------------------------------------------------------------------------------------
# Generators
# -----------------------------------------------------------------------------------------------------------------


class BaseContactMenuGenerator:

    def __init__(self, contact):
        self._contact = contact

    def generate(self, plugin_loader, contacts_manager, main_screen, settings, number, groups_service):
        return ContactMenuBuilder().build()

    def _generate_copy_menu_builder(self, main_screen):
        copy_menu_builder = ContactMenuBuilder()
        (copy_menu_builder
         .with_name(util_ui.tr('Copy'))
         .with_action(util_ui.tr('Name'), lambda: main_screen.copy_text(self._contact.name))
         .with_action(util_ui.tr('Status message'), lambda: main_screen.copy_text(self._contact.status_message))
         .with_action(util_ui.tr('Public key'), lambda: main_screen.copy_text(self._contact.tox_id))
         )

        return copy_menu_builder


class FriendMenuGenerator(BaseContactMenuGenerator):

    def generate(self, plugin_loader, contacts_manager, main_screen, settings, number, groups_service):
        history_menu_builder = self._generate_history_menu_builder(main_screen, number)
        copy_menu_builder = self._generate_copy_menu_builder(main_screen)
        plugins_menu_builder = self._generate_plugins_menu_builder(plugin_loader, number)
        groups_menu_builder = self._generate_groups_menu(contacts_manager, groups_service)

        allowed = self._contact.tox_id in settings['auto_accept_from_friends']
        auto = util_ui.tr('Disallow auto accept') if allowed else util_ui.tr('Allow auto accept')

        builder = ContactMenuBuilder()
        menu = (builder
                .with_action(util_ui.tr('Set alias'), lambda: main_screen.set_alias(number))
                .with_submenu(history_menu_builder)
                .with_submenu(copy_menu_builder)
                .with_action(auto, lambda: main_screen.auto_accept(number, not allowed))
                .with_action(util_ui.tr('Remove friend'), lambda: main_screen.remove_friend(number))
                .with_action(util_ui.tr('Block friend'), lambda: main_screen.block_friend(number))
                .with_action(util_ui.tr('Notes'), lambda: main_screen.show_note(self._contact))
                .with_optional_submenu(plugins_menu_builder)
                .with_optional_submenu(groups_menu_builder)
                ).build()

        return menu

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _generate_history_menu_builder(main_screen, number):
        history_menu_builder = ContactMenuBuilder()
        (history_menu_builder
         .with_name(util_ui.tr('Chat history'))
         .with_action(util_ui.tr('Clear history'), lambda: main_screen.clear_history(number))
         .with_action(util_ui.tr('Export as text'), lambda: main_screen.export_history(number))
         .with_action(util_ui.tr('Export as HTML'), lambda: main_screen.export_history(number, False))
         )

        return history_menu_builder

    @staticmethod
    def _generate_plugins_menu_builder(plugin_loader, number):
        if plugin_loader is None:
            return None
        plugins_actions = plugin_loader.get_menu(number)
        if not len(plugins_actions):
            return None
        plugins_menu_builder = ContactMenuBuilder()
        (plugins_menu_builder
         .with_name(util_ui.tr('Plugins'))
         .with_actions(plugins_actions)
         )

        return plugins_menu_builder

    def _generate_groups_menu(self, contacts_manager, groups_service):
        chats = contacts_manager.get_group_chats()
        if not len(chats) or self._contact.status is None:
            return None
        groups_menu_builder = ContactMenuBuilder()
        (groups_menu_builder
         .with_name(util_ui.tr('Invite to group'))
         .with_actions([(g.name, lambda: groups_service.invite_friend(self._contact.number, g.number)) for g in chats])
         )

        return groups_menu_builder


class GroupMenuGenerator(BaseContactMenuGenerator):

    def generate(self, plugin_loader, contacts_manager, main_screen, settings, number, groups_service):
        copy_menu_builder = self._generate_copy_menu_builder(main_screen)

        builder = ContactMenuBuilder()
        menu = (builder
                .with_action(util_ui.tr('Set alias'), lambda: main_screen.set_alias(number))
                .with_submenu(copy_menu_builder)
                .with_action(util_ui.tr('Leave group'), lambda: groups_service.leave_group(self._contact.number))
                .with_action(util_ui.tr('Notes'), lambda: main_screen.show_note(self._contact))
                ).build()

        return menu
