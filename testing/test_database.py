import random
import os
import sqlite3

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

def test_add_paper(db):
    db.add_paper(u.my_bibcode, u.my_bibtex)
    assert db.get_paper(u.my_bibcode)["bibtex"] == u.my_bibtex

def test_no_uniques(db):
    db.add_paper(u.my_bibcode, u.my_bibtex)
    with pytest.raises(sqlite3.IntegrityError):
        db.add_paper(u.my_bibcode, u.my_bibtex)