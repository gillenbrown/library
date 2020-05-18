import random
from pathlib import Path

import pytest

from library.lib import Library
import test_utils as u


@pytest.fixture(name="lib")
def temporary_library():
    """
    Fixture to get a library at a temporary path in the current directory. This will be
    removed once the test is done
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Library(file_path)
    yield db
    file_path.unlink()  # removes this file


def test_initialize_creates_database(lib):
    assert lib.storage_location is not None
    assert lib.database is not None


def test_add_paper_from_ads_url(lib):
    lib.add_paper(u.my_ads_url)
    # I won't test the value, just that it found something. I'll test values below
    assert lib.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arvix_url(lib):
    lib.add_paper(u.my_arxiv_url)
    assert lib.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arvix_url_v2(lib):
    lib.add_paper(u.my_arxiv_url_v2)
    assert lib.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arxiv_id(lib):
    lib.add_paper(u.my_arxiv_id)
    assert lib.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arxiv_pdf_url(lib):
    lib.add_paper(u.my_arxiv_pdf_url)
    assert lib.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arxiv_pdf_url_v2(lib):
    lib.add_paper(u.my_arxiv_pdf_url_v2)
    assert lib.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_ads_bibcode(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "title") is not None


def test_added_paper_has_correct_bibcode(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "bibcode") == u.my_bibcode


def test_added_paper_has_correct_title(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "title") == u.my_title


def test_added_paper_has_correct_authors(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "authors") == u.my_authors


def test_added_paper_has_correct_pubdate(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "pubdate") == u.my_pubdate


def test_added_paper_has_correct_journal(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "journal") == u.my_journal


def test_added_paper_has_correct_volume(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "volume") == u.my_volume


def test_added_paper_has_correct_page(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "page") == u.my_page


def test_added_paper_has_correct_abstract(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "abstract") == u.my_abstract


def test_added_paper_has_correct_bibtex(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper_attribute(u.my_bibcode, "bibtex") == u.my_bibtex


def test_raises_error_when_searching_for_paper_not_added_yet(lib):
    lib.add_paper(u.my_bibcode)
    with pytest.raises(ValueError):
        lib.get_paper_attribute(u.tremonti_bibcode, "title")


def test_get_all_bibcodes_actually_gets_all_bibcodes(lib):
    lib.add_paper(u.my_bibcode)
    lib.add_paper(u.tremonti_bibcode)
    # sort the list of bibcodes for actual comparison
    test_bibcodes = sorted(lib.get_all_bibcodes())
    true_bibcodes = sorted([u.my_bibcode, u.tremonti_bibcode])
    assert test_bibcodes == true_bibcodes
