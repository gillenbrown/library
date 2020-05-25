import random
from pathlib import Path

import pytest

from library.database import Database, PaperAlreadyInDatabaseError
import test_utils as u


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
    db.add_paper(u.my_bibcode)
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
    db.add_paper(u.my_bibcode)
    db.add_paper(u.tremonti_bibcode)
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
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.num_papers() == 1
    db_empty.add_paper(u.tremonti_bibcode)
    assert db_empty.num_papers() == 2


def test_add_paper_from_ads_url(db_empty):
    db_empty.add_paper(u.my_ads_url)
    # I won't test the value, just that it found something. I'll test values below
    assert db_empty.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arvix_url(db_empty):
    db_empty.add_paper(u.my_arxiv_url)
    assert db_empty.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arvix_url_v2(db_empty):
    db_empty.add_paper(u.my_arxiv_url_v2)
    assert db_empty.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arxiv_id(db_empty):
    db_empty.add_paper(u.my_arxiv_id)
    assert db_empty.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arxiv_pdf_url(db_empty):
    db_empty.add_paper(u.my_arxiv_pdf_url)
    assert db_empty.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_arxiv_pdf_url_v2(db_empty):
    db_empty.add_paper(u.my_arxiv_pdf_url_v2)
    assert db_empty.get_paper_attribute(u.my_bibcode, "title") is not None


def test_add_paper_from_ads_bibcode(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "title") is not None


def test_added_paper_has_correct_bibcode(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "bibcode") == u.my_bibcode


def test_added_paper_has_correct_title(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "title") == u.my_title


def test_added_paper_has_correct_authors(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "authors") == u.my_authors


def test_added_paper_has_correct_pubdate(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "pubdate") == u.my_pubdate


def test_added_paper_has_correct_journal(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "journal") == u.my_journal


def test_added_paper_has_correct_volume(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "volume") == u.my_volume


def test_added_paper_has_correct_page(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "page") == u.my_page


def test_added_paper_has_correct_abstract(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "abstract") == u.my_abstract


def test_added_paper_has_correct_bibtex(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "bibtex") == u.my_bibtex


def test_added_paper_returns_correct_bibcode(db_empty):
    test_bibcode = db_empty.add_paper(u.my_ads_url)
    assert db_empty.get_paper_attribute(u.my_bibcode, "bibcode") == test_bibcode
    assert test_bibcode == u.my_bibcode


def test_bibcode_correct_after_adding_paper(db_empty):
    db_empty.add_paper(u.my_bibcode)
    assert db_empty.get_paper_attribute(u.my_bibcode, "bibcode") == u.my_bibcode


def test_error_raised_if_nonexistent_paper_is_searched_for(db_one):
    with pytest.raises(ValueError):
        db_one.get_paper_attribute(u.tremonti_bibcode, "bibcode")


def test_raise_custom_error_if_paper_is_already_in_database(db_empty):
    db_empty.add_paper(u.my_bibcode)
    with pytest.raises(PaperAlreadyInDatabaseError):
        db_empty.add_paper(u.my_bibcode)
    assert db_empty.num_papers() == 1


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


def test_raises_errror_if_attribute_does_not_exist(db):
    with pytest.raises(ValueError):
        db.get_paper_attribute(u.my_bibcode, "bad attribute")


def test_local_file_is_none_before_it_is_set(db):
    assert db.get_paper_attribute(u.my_bibcode, "local_file") == None
    assert db.get_paper_attribute(u.tremonti_bibcode, "local_file") == None


def test_add_attribute_file_loc_is_done_correctly(db):
    test_loc = "/Users/gillenb/test.pdf"
    db.set_paper_attribute(u.my_bibcode, "local_file", test_loc)
    assert db.get_paper_attribute(u.my_bibcode, "local_file") == test_loc


def test_raise_error_when_attempting_to_modify_nonexistent_attribute(db):
    with pytest.raises(ValueError):
        db.set_paper_attribute(u.my_bibcode, "slkdfsldkj", "New value")


def test_raise_error_when_attempting_to_modify_nonexistent_bibcode(db):
    with pytest.raises(ValueError):
        db.set_paper_attribute("sdlkfjsldfkj", "title", "new_title")


def test_raise_error_when_attempting_to_modify_value_with_wrong_data_type(db):
    with pytest.raises(ValueError):
        db.set_paper_attribute(u.my_bibcode, "title", (4, 3))


def test_modify_title_as_an_example_with_set_paper_attribute(db):
    db.set_paper_attribute(u.my_bibcode, "title", "New Title")
    assert db.get_paper_attribute(u.my_bibcode, "title") == "New Title"


def test_modify_authors_list_with_set_paper_attribute(db):
    new_list = ["Last, First", "Last2, First2"]
    db.set_paper_attribute(u.my_bibcode, "authors", new_list)
    assert db.get_paper_attribute(u.my_bibcode, "authors") == new_list


def test_cite_string_one_author(db):
    db.set_paper_attribute(u.my_bibcode, "authors", ["Brown, Gillen"])
    true_cite_string = f"Brown, 2018, ApJ, {u.my_volume}, {u.my_page}"
    assert db.get_cite_string(u.my_bibcode) == true_cite_string


def test_cite_string_two_authors(db):
    new_authors = ["Brown, Gillen", "Gnedin, Oleg Y."]
    db.set_paper_attribute(u.my_bibcode, "authors", new_authors)
    true_cite_string = f"Brown, Gnedin, 2018, ApJ, {u.my_volume}, {u.my_page}"
    assert db.get_cite_string(u.my_bibcode) == true_cite_string


def test_cite_string_three_authors(db):
    # my paper already has three authors
    true_cite_string = f"Brown, Gnedin, Li, 2018, ApJ, {u.my_volume}, {u.my_page}"
    assert db.get_cite_string(u.my_bibcode) == true_cite_string


def test_cite_string_four_authors_uses_et_al(db):
    new_authors = ["Brown, Gillen", "Gnedin, Oleg Y.", "Li, Hui", "Author, Test"]
    db.set_paper_attribute(u.my_bibcode, "authors", new_authors)
    true_cite_string = f"Brown et al., 2018, ApJ, {u.my_volume}, {u.my_page}"
    assert db.get_cite_string(u.my_bibcode) == true_cite_string


def test_cite_string_many_authors_uses_et_al(db):
    true_cite_string = (
        f"Tremonti et al., 2004, ApJ, " f"{u.tremonti_volume}, {u.tremonti_page}"
    )
    assert db.get_cite_string(u.tremonti_bibcode) == true_cite_string


def test_cite_string_apj_is_shortened(db):
    true_cite_string = f"Brown, Gnedin, Li, 2018, ApJ, {u.my_volume}, {u.my_page}"
    assert db.get_cite_string(u.my_bibcode) == true_cite_string


def test_cite_string_mnras_is_shortened_test_paper(db):
    test_bibcode = "2003MNRAS.344.1000B"
    db.add_paper(test_bibcode)
    true_cite_string = f"Bruzual, Charlot, 2003, MNRAS, 344, 1000"
    assert db.get_cite_string(test_bibcode) == true_cite_string


def test_can_add_new_tag_column_and_it_is_false_for_all_papers(db):
    db.add_new_tag("test_tag")
    for bibcode in db.get_all_bibcodes():
        assert db.paper_has_tag(bibcode, "test_tag") is False


def test_cannot_access_tags_from_get_paper_attribute(db):
    db.add_new_tag("test_tag")
    with pytest.raises(ValueError):
        db.get_paper_attribute(u.my_bibcode, "test_tag")


def test_can_add_tag_to_a_paper(db):
    db.add_new_tag("test_tag")
    assert db.paper_has_tag(u.my_bibcode, "test_tag") is False
    db.tag_paper(u.my_bibcode, "test_tag")
    assert db.paper_has_tag(u.my_bibcode, "test_tag") is True


def test_can_add_tag_to_a_paper_and_only_that_paper_tagged(db):
    db.add_new_tag("test_tag")
    db.tag_paper(u.my_bibcode, "test_tag")
    assert db.paper_has_tag(u.tremonti_bibcode, "test_tag") is False
