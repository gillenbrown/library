import pytest

from library.library import Library

@pytest.fixture
def new_library():
    return Library()

def test_init(new_library):
    assert new_library.papers == []
