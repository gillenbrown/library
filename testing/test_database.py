import random
from pathlib import Path

import pytest

from library.database import Database
import test_utils as u


def add_my_paper(some_db):
    some_db.add_paper(
        u.my_bibcode,
        u.my_title,
        u.my_authors,
        u.my_pubdate,
        u.my_journal,
        u.my_volume,
        u.my_page,
        u.my_abstract,
        u.my_bibtex,
    )


def add_tremonti_paper(some_db):
    some_db.add_paper(
        u.tremonti_bibcode,
        u.tremonti_title,
        ["blank"],
        "blank",
        "blank",
        0,
        0,
        "blank",
        u.tremonti_bibtex,
    )


@pytest.fixture(name="db_empty")
def temporary_db():
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db")
def temporary_db_one_paper():
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    add_my_paper(db)
    yield db
    file_path.unlink()  # removes this file


def test_database_number_of_tables(db):
    tables = db._execute("SELECT name FROM sqlite_master WHERE type='table';")
    assert len(tables) == 1


def test_database_has_papers_table(db):
    tables = db._execute("SELECT name FROM sqlite_master WHERE type='table';")
    names = [item["name"] for item in tables]
    assert "papers" in names


def test_add_paper_length(db_empty):
    assert db_empty.num_papers() == 0
    add_my_paper(db_empty)
    assert db_empty.num_papers() == 1
    add_tremonti_paper(db_empty)
    assert db_empty.num_papers() == 2


def test_add_get_paper(db_empty):
    add_my_paper(db_empty)
    assert db_empty.get_paper_attribute(u.my_bibcode, "bibcode") == u.my_bibcode


def test_get_paper_not_found(db):
    with pytest.raises(ValueError):
        db.get_paper_attribute("nonsense_bibcode_value", "bibcode")


def test_no_uniques_but_no_crash(db):
    add_my_paper(db)
    add_my_paper(db)
    assert db.num_papers() == 1


def test_get_all_bibcodes(db):
    add_tremonti_paper(db)  # already has my paper
    # sort the lists of bibcodes so comparison can be made
    test_bibcodes = sorted(db.get_all_bibcodes())
    true_bibcodes = sorted([u.my_bibcode, u.tremonti_bibcode])
    assert test_bibcodes == true_bibcodes


def test_get_title(db):
    assert db.get_paper_attribute(u.my_bibcode, "title") == u.my_title


def test_get_authors(db):
    assert db.get_paper_attribute(u.my_bibcode, "authors") == u.my_authors


def test_get_pubdate(db):
    assert db.get_paper_attribute(u.my_bibcode, "pubdate") == u.my_pubdate


def test_get_journal(db):
    assert db.get_paper_attribute(u.my_bibcode, "journal") == u.my_journal


def test_get_volume(db):
    assert db.get_paper_attribute(u.my_bibcode, "volume") == u.my_volume


def test_get_page(db):
    assert db.get_paper_attribute(u.my_bibcode, "page") == u.my_page


def test_get_abstract(db):
    assert db.get_paper_attribute(u.my_bibcode, "abstract") == u.my_abstract


def test_get_bibtex(db):
    assert db.get_paper_attribute(u.my_bibcode, "bibtex") == u.my_bibtex
