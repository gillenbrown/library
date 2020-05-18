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
        u.tremonti_authors,
        u.tremonti_pubdate,
        u.tremonti_journal,
        u.tremonti_volume,
        u.tremonti_page,
        u.tremonti_abstract,
        u.tremonti_bibtex,
    )


@pytest.fixture(name="db_empty")
def temporary_db():
    """
    Fixture to get a databawses at a temporary path in the current directory. This will
    be removed once the test is done
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db_one")
def temporary_db_one_paper():
    """
    Fixture to get a databawses at a temporary path in the current directory. This will
    be removed once the test is done. One paper will be added to this library
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    add_my_paper(db)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db")
def temporary_db_two_papers():
    """
    Fixture to get a databawses at a temporary path in the current directory. This will
    be removed once the test is done. Two papers will be added to this library
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    add_my_paper(db)
    add_tremonti_paper(db)
    yield db
    file_path.unlink()  # removes this file


def test_database_has_one_table(db):
    tables = db._execute("SELECT name FROM sqlite_master WHERE type='table';")
    assert len(tables) == 1


def test_database_has_papers_table(db):
    tables = db._execute("SELECT name FROM sqlite_master WHERE type='table';")
    names = [item["name"] for item in tables]
    assert "papers" in names


def test_num_papers_is_correct_as_papers_are_added(db_empty):
    assert db_empty.num_papers() == 0
    add_my_paper(db_empty)
    assert db_empty.num_papers() == 1
    add_tremonti_paper(db_empty)
    assert db_empty.num_papers() == 2


def test_bibcode_correct_after_adding_paper(db_empty):
    add_my_paper(db_empty)
    assert db_empty.get_paper_attribute(u.my_bibcode, "bibcode") == u.my_bibcode


def test_error_raised_if_nonexistent_paper_is_searched_for(db_one):
    with pytest.raises(ValueError):
        db_one.get_paper_attribute(u.tremonti_bibcode, "bibcode")


def test_same_paper_can_be_added_twice_no_crash_but_only_in_database_once(db_one):
    add_my_paper(db_one)
    add_my_paper(db_one)
    assert db_one.num_papers() == 1


def test_get_all_bibcodes_does_what_it_says(db):
    # already has two papers
    # sort the lists of bibcodes so comparison can be made
    test_bibcodes = sorted(db.get_all_bibcodes())
    true_bibcodes = sorted([u.my_bibcode, u.tremonti_bibcode])
    assert test_bibcodes == true_bibcodes


def test_get_correct_attributes_title(db):
    assert db.get_paper_attribute(u.my_bibcode, "title") == u.my_title
    assert db.get_paper_attribute(u.tremonti_bibcode, "title") == u.tremonti_title


def test_get_correct_attributes_authors(db):
    assert db.get_paper_attribute(u.my_bibcode, "authors") == u.my_authors
    assert db.get_paper_attribute(u.tremonti_bibcode, "authors") == u.tremonti_authors


def test_get_correct_attributes_pubdate(db):
    assert db.get_paper_attribute(u.my_bibcode, "pubdate") == u.my_pubdate
    assert db.get_paper_attribute(u.tremonti_bibcode, "pubdate") == u.tremonti_pubdate


def test_get_correct_attributes_journal(db):
    assert db.get_paper_attribute(u.my_bibcode, "journal") == u.my_journal
    assert db.get_paper_attribute(u.tremonti_bibcode, "journal") == u.tremonti_journal


def test_get_correct_attributes_volume(db):
    assert db.get_paper_attribute(u.my_bibcode, "volume") == u.my_volume
    assert db.get_paper_attribute(u.tremonti_bibcode, "volume") == u.tremonti_volume


def test_get_correct_attributes_page(db):
    assert db.get_paper_attribute(u.my_bibcode, "page") == u.my_page
    assert db.get_paper_attribute(u.tremonti_bibcode, "page") == u.tremonti_page


def test_get_correct_attributes_abstract(db):
    assert db.get_paper_attribute(u.my_bibcode, "abstract") == u.my_abstract
    assert db.get_paper_attribute(u.tremonti_bibcode, "abstract") == u.tremonti_abstract


def test_get_correct_attributes_bibtex(db):
    assert db.get_paper_attribute(u.my_bibcode, "bibtex") == u.my_bibtex
    assert db.get_paper_attribute(u.tremonti_bibcode, "bibtex") == u.tremonti_bibtex
