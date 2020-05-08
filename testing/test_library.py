import random
from pathlib import Path

import pytest

from library.lib import Library
import test_utils as u


@pytest.fixture(name="lib")
def temporary_library():
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Library(file_path)
    yield db
    file_path.unlink()  # removes this file


def test_init_has_database(lib):
    assert lib.storage_location is not None
    assert lib.database is not None


def test_add_paper_from_ads_url(lib):
    lib.add_paper(u.my_ads_url)
    assert lib.get_paper(u.my_bibcode) is not None


def test_add_paper_from_arvix_url(lib):
    lib.add_paper(u.my_arxiv_url)
    assert lib.get_paper(u.my_bibcode) is not None


def test_add_paper_from_arxiv_id(lib):
    lib.add_paper(u.my_arxiv_id)
    assert lib.get_paper(u.my_bibcode) is not None


def test_add_paper_from_arxiv_pdf_url(lib):
    lib.add_paper(u.my_arxiv_pdf_url)
    assert lib.get_paper(u.my_bibcode) is not None


def test_add_paper_from_ads_bibcode(lib):
    lib.add_paper(u.my_bibcode)
    assert lib.get_paper(u.my_bibcode) is not None


def test_nonexistent_paper_not_found(lib):
    lib.add_paper(u.my_bibcode)
    with pytest.raises(ValueError):
        lib.get_paper("sldfsldkfjlsdkfj")


def test_get_all_bibcodes(lib):
    lib.add_paper(u.my_bibcode,)
    lib.add_paper(u.tremonti_bibcode)
    assert lib.get_all_bibcodes() == [u.my_bibcode, u.tremonti_bibcode]
