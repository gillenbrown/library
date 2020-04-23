import pytest

from library.library import Library
import test_utils as u


@pytest.fixture
def new_library():
    return Library()

def test_init(new_library):
    assert new_library.papers == []

def test_add_paper_papers_list_length(new_library):
    new_library.add_paper(u.my_ads_url)
    assert len(new_library.papers) == 1
