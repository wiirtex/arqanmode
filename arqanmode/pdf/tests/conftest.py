import pytest

from pdf import PDFReader


@pytest.fixture()
def pdf_reader() -> PDFReader:
    return PDFReader()
