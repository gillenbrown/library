import pytest

from library.library import Library
import test_utils as u


@pytest.fixture(name="lib")
def fixture_new_library():
    return Library()

def test_init(lib):
    assert lib.papers == []

def test_add_paper_papers_list_length(lib):
    lib.add_paper(u.my_ads_url)
    assert len(lib.papers) == 1
