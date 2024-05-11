import re
import string
from collections import Counter

import spacy
from fitz import Document
from unicodedata import normalize


class PDFReader:
    FOOTER_PATTERN = re.compile(r'Page\s+\d+\s+of\s+\d*', re.IGNORECASE)
    LIST_PATTERN = re.compile(r'^[a-zA-Z]\.|^([0-9]*\.[0-9]*)+')
    END_OF_SENTENCE_CHARACTERS = {'.', '?', '!'}

    def __init__(self):
        self._lang = spacy.load('en_core_web_sm')

    def get_sentences(self, file_content: bytes) -> list[str]:
        """Extracts and filters sentences from PDF file"""

        lines = self._get_lines(file_content)
        lines = self._concatenate_lines(lines)

        sents = []
        for line in lines:
            doc = self._lang(line)
            line_sents = [line_sent.strip() for sentence in doc.sents for line_sent in sentence.text.split('\n')]
            filtered_line_sents = filter(self._filter_line, line_sents)
            sents.extend(filtered_line_sents)

        return self._remove_lists(sents)

    def _get_lines(self, file_content: bytes) -> list[str]:
        doc = Document(stream=file_content, filetype='pdf')
        lines = []
        for page in doc:
            page_text = page.get_textpage().extractText()
            page_lines = [line.strip() for line in page_text.split('\n') if len(line.strip()) > 0]
            lines.extend(page_lines)

        repetitions = Counter(lines)
        lines = [normalize('NFKC', line) for line in lines if repetitions[line] < doc.page_count / 2]

        lines = self._remove_footers(lines)
        lines = self._remove_headers(lines)
        lines = self._remove_lists(lines)
        lines = self._remove_empty_lines(lines)

        return lines

    @classmethod
    def _remove_footers(cls, lines: list[str]) -> list[str]:
        def is_footer(line: str) -> bool:
            return re.search(cls.FOOTER_PATTERN, line) is not None

        if len(lines) == 0:
            return []
        return list(filter(lambda l: not is_footer(l), lines))

    @classmethod
    def _remove_headers(cls, lines: list[str]) -> list[str]:
        def is_header(line: str) -> bool:
            return line.count('.') > 10

        if len(lines) == 0:
            return []
        return list(filter(lambda l: not is_header(l), lines))

    @classmethod
    def _remove_lists(cls, lines: list[str]) -> list[str]:
        def remove(line: str) -> str:
            return re.sub(cls.LIST_PATTERN, '', line).strip()

        if len(lines) == 0:
            return []
        return list(map(remove, lines))

    @classmethod
    def _remove_empty_lines(cls, lines: list[str]) -> list[str]:
        if len(lines) == 0:
            return []
        return list(filter(lambda l: len(l) != 0, lines))

    def _concatenate_lines(self, lines: list[str]) -> list[str]:
        if len(lines) == 0:
            return []

        result = [lines[0]]
        for i in range(1, len(lines)):
            prev_line = result[-1]
            curr_line = lines[i]

            if not self._merge_lines(prev_line, curr_line):
                result.append(curr_line)
                continue

            if prev_line[-1] == '-':
                result[-1] = prev_line[:-1] + curr_line
            else:
                result[-1] = prev_line + ' ' + curr_line
        return result

    @classmethod
    def _merge_lines(cls, line1: str, line2: str) -> bool:
        return len(line1) > 30 and not line1.isupper() and \
            line1.strip()[-1] not in cls.END_OF_SENTENCE_CHARACTERS and \
            any(char.isalpha() for char in line2) and \
            not all(map(cls._is_camel_case, line1))

    @classmethod
    def _is_camel_case(cls, text: str) -> bool:
        return text != text.lower() and text != text.upper()

    @classmethod
    def _filter_line(cls, line: str) -> bool:
        def is_footer(text: str) -> bool:
            return re.search(cls.FOOTER_PATTERN, text) is not None

        return line and len(line.split()) > 3 and len(line.strip()) > 30 \
            and any(char.isalpha() for char in line) and not is_footer(line) and \
            all(char in string.printable for char in line)
