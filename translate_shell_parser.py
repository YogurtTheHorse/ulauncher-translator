import shlex
import subprocess


class TranslationItem:
    def __init__(self, translation, part_of_speech=None, examples=None, synonyms=None):
        self.translation = translation
        self.part_of_speech = part_of_speech or ''
        self.synonyms = synonyms or []
        self.examples = examples or []


class TranslateShellParser:
    def __init__(self, request):
        self.request = request

        self._current_translation = None
        self._examples = list()
        self._synonyms = list()

    def execute(self):
        try:
            args = shlex.split('trans -no-ansi ' + self.request)
        except ValueError:
            raise StopIteration

        result = subprocess.Popen(args, stdout=subprocess.PIPE). \
            communicate()[0]

        lines = result.split('\n')

        if len(lines) == 0:
            raise StopIteration

        if len(lines[0]) > 0:
            yield TranslationItem(lines[0])

        current_category = None
        for line in lines[1:]:
            line = line.replace('\t', ' ' * 4)
            stripped_line = line.lstrip()
            indent_count = len(line) - len(stripped_line)

            if indent_count == 0 and len(stripped_line) > 0:
                current_category = stripped_line
                continue

            if current_category in ['noun', 'verb', 'adjective']:
                translation_item = self._translation_category(current_category, indent_count, stripped_line)
                if translation_item is not None:
                    yield translation_item

    def _translation_category(self, current_category, indent_count, line):
        translation = None

        if len(line) == 0 or indent_count == 4:
            if self._current_translation is not None:
                translation = TranslationItem(
                    self._current_translation,
                    current_category,
                    self._examples,
                    self._synonyms
                )
                print(translation.translation)
            self._current_translation = None
            self._examples = list()
            self._synonyms = list()
        if indent_count == 4:
            if line.startswith('Synonyms: '):
                self._synonyms = line[len('Synonyms: '):].split(',')
                self._synonyms = [synonym.strip() for synonym in self._synonyms if len(synonym.strip()) > 0]
            else:
                self._current_translation = line
        elif indent_count == 8:
            if line.startswith('-'):
                self._examples.append(line[2:])
            else:
                self._examples = [example.strip() for example in line.split(',') if len(example.strip()) > 0]

        return translation
