import random
import os

import pytest

from library.database import Database
import test_utils as u


@pytest.fixture(name="db")
def temporary_db():
    filename = f"{random.randint(0, 1000000000)}.db"
    file_path = os.path.abspath(f"./{filename}")
    db = Database(filename)
    yield db
    os.remove(file_path)


def test_database_number_of_tables(db):
    tables = db._execute("SELECT name FROM sqlite_master WHERE type='table';")
    assert len(tables) == 1


def test_database_has_papers_table(db):
    tables = db._execute("SELECT name FROM sqlite_master WHERE type='table';")
    names = [item["name"] for item in tables]
    assert "papers" in names


def test_add_paper_length(db):
    assert db.num_papers() == 0
    db.add_paper(u.my_bibcode, u.my_bibtex)
    assert db.num_papers() == 1
    db.add_paper(u.tremonti_bibcode, "")
    assert db.num_papers() == 2


def test_add_get_paper(db):
    db.add_paper(u.my_bibcode, u.my_bibtex)
    assert db.get_paper(u.my_bibcode)["bibtex"] == u.my_bibtex


def test_get_paper_not_found(db):
    with pytest.raises(ValueError):
        db.get_paper("slkdfjlsdkfj")


def test_no_uniques_but_no_crash(db):
    db.add_paper(u.my_bibcode, u.my_bibtex)
    db.add_paper(u.my_bibcode, u.my_bibtex)
    assert db.num_papers() == 1


def test_get_all_bibcodes(db):
    db.add_paper(u.my_bibcode, u.my_bibtex)
    db.add_paper(u.tremonti_bibcode, "")
    assert db.get_all_bibcodes() == [u.my_bibcode, u.tremonti_bibcode]
