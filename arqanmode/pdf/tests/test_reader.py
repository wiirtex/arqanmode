import pytest

from pdf import PDFReader

test_data = [
    (
        'pdf/tests/data/file0.pdf',
        [
            'The application user interface must be either physically or '
            'logically separated from data storage and management interfaces.',
            'The application must set the HTTPOnly flag on session cookies.',
            'The application must not expose session IDs.',
            'The application must destroy the session ID value and/or cookie on logoff or browser close.'
        ]
    )
]


@pytest.mark.parametrize('file_name,expected', test_data)
def test_get_sentences(pdf_reader: PDFReader, file_name: str, expected: list[str]):
    with open(file_name, 'rb') as file:
        file_content = file.read()
    result = pdf_reader.get_sentences(file_content)
    assert expected == result


test_data = [
    (
        'pdf/tests/data/file0.pdf',
        [
            'The application user interface must be either physically or logically',
            'separated from data storage and management interfaces.',
            'The application must set the HTTPOnly flag on session cookies.',
            'The application must not expose session IDs.',
            'The application must destroy the session ID value and/or cookie on logoff',
            'or browser close.'
        ]
    )
]


@pytest.mark.parametrize('file_name,expected', test_data)
def test_get_lines(pdf_reader: PDFReader, file_name: str, expected: list[str]):
    with open(file_name, 'rb') as file:
        file_content = file.read()
    result = pdf_reader._get_lines(file_content)
    assert expected == result


test_data = [
    (
        [
            'The application user interface must be either physically or logically',
            'separated from data storage and management interfaces. The application must not expose session IDs.',
            'The application must set the HTTPOnly flag on session cookies.',
            'The application must destroy the session ID value and/or cookie on logoff',
            'or browser close.'
        ],
        [
            'The application user interface must be either physically or '
            'logically separated from data storage and management interfaces. '
            'The application must not expose session IDs.',
            'The application must set the HTTPOnly flag on session cookies.',
            'The application must destroy the session ID value and/or cookie on logoff or browser close.'
        ]
    )
]


@pytest.mark.parametrize('lines,expected', test_data)
def test_concatenate_lines(pdf_reader: PDFReader, lines: list[str], expected: list[str]):
    result = pdf_reader._concatenate_lines(lines)
    assert expected == result
