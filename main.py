from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction

from translate_shell_parser import TranslateShellParser


class TranslateExtension(Extension):
    def __init__(self):
        super(TranslateExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or str()

        if len(query.strip()) == 0:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/gt-icon.png',
                                    name='No input',
                                    on_enter=HideWindowAction())
            ])

        try:
            translations = list(TranslateShellParser(query).execute())
        except OSError:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/gt-icon.png',
                    name='Looks like you have no translate-shell installed',
                    description="Select to open repo",
                    on_enter=OpenUrlAction('https://github.com/soimort/translate-shell')
                )
            ])

        items = [
            ExtensionResultItem(icon='images/gt-icon.png',
                                name=translation.translation,
                                description=translation.part_of_speech + ', ' + ' '.join(translation.synonyms),
                                on_enter=HideWindowAction())

            for translation in translations
        ]

        return RenderResultListAction(items)


if __name__ == '__main__':
    TranslateExtension().run()
