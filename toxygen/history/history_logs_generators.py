from messenger.messages import *
import util.util as util


class HistoryLogsGenerator:

    def __init__(self, history, contact_name):
        self._history = history
        self._contact_name = contact_name

    def generate(self):
        return str()

    @staticmethod
    def _get_message_time(message):
        return util.convert_time(message.time) if message.author.type != MESSAGE_AUTHOR['NOT_SENT'] else 'Unsent'


class HtmlHistoryGenerator(HistoryLogsGenerator):

    def __init__(self, history, contact_name):
        super().__init__(history, contact_name)

    def generate(self):
        arr = []
        for message in self._history:
            if type(message) is TextMessage:
                x = '[{}] <b>{}:</b> {}<br>'
                arr.append(x.format(self._get_message_time(message), message.author.name, message.text))
        s = '<br>'.join(arr)
        html = '<html><head><meta charset="UTF-8"><title>{}</title></head><body>{}</body></html>'

        return html.format(self._contact_name, s)


class TextHistoryGenerator(HistoryLogsGenerator):

    def __init__(self, history, contact_name):
        super().__init__(history, contact_name)

    def generate(self):
        arr = [self._contact_name]
        for message in self._history:
            if type(message) is TextMessage:
                x = '[{}] {}: {}\n'
                arr.append(x.format(self._get_message_time(message), message.author.name, message.text))

        return '\n'.join(arr)
