import os
import random

import pytest

from library.library import Library
import test_utils as u


@pytest.fixture(name="lib")
def temporary_library():
    filename = f"{random.randint(0, 1000000000)}.db"
    file_path = os.path.abspath(f"./{filename}")
    db = Library(filename)
    yield db
    os.remove(file_path)

def test_init_has_database(lib):
    assert lib.storage_location is not None
    assert lib.database is not None