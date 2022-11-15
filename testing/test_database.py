import random
import time
from pathlib import Path
import shutil
import sqlite3
import contextlib

import pytest

from library.database import Database, PaperAlreadyInDatabaseError
import test_utils as u

# define some tags that include punctuation, which can mess up SQL. I'll use these
# later
punctuation_tags = [
    '"',
    "'",
    """ this is "single ' and double " quotes" """,
    """ this has everything: '"('");.,!-: """,
    ";",
    ".",
    ",",
    "(",
    ")",
    "!",
    "-",
    ":",
]

# ======================================================================================
#
# Fixtures to use as temporary database
#
# ======================================================================================
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
    db.add_paper(u.mine.bibcode)
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
    db.add_paper(u.mine.bibcode)
    db.add_paper(u.tremonti.bibcode)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db_update")
def temporary_db_with_old_arxiv_paper():
    """
    Fixture to get a database I've prefilled with one paper with arXiv only details.
    This paper has since been published in a journal, so this is designed to check
    whether the database can update papers to include this information.

    Note that this provides a temporary database that's a copy of the original, since
    I don't want that one to be modified
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    shutil.copy2(Path(__file__).parent / "testing_update.db", file_path)
    db = Database(file_path)
    yield db
    file_path.unlink()  # removes this file


# ======================================================================================
#
# convenience function for creating import bibtex files
#
# ======================================================================================
def create_bibtex(*args):
    """
    Write the given text into a random bibtex file, and return the file location

    :param args: bibtex entries to write to the file
    :type args: str
    :return: path to the file location
    :rtype: pathlib.Path
    """
    text = "\n\n".join(args)
    file_path = Path(f"{random.randint(0, 1000000000)}.bib").resolve()
    with open(file_path, "w") as bibfile:
        bibfile.write(text)
    return file_path


# ======================================================================================
#
# basic validation of databases
#
# ======================================================================================
def test_database_has_one_table(db):
    tables = db._execute("SELECT name FROM sqlite_master WHERE type='table';")
    assert len(tables) == 1


def test_database_has_papers_table(db):
    tables = db._execute("SELECT name FROM sqlite_master WHERE type='table';")
    names = [item["name"] for item in tables]
    assert "papers" in names


# ======================================================================================
#
# test adding papers and getting attributes
#
# ======================================================================================
def test_num_papers_is_correct_as_papers_are_added(db_empty):
    assert db_empty.num_papers() == 0
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.num_papers() == 1
    db_empty.add_paper(u.tremonti.bibcode)
    assert db_empty.num_papers() == 2


def test_add_paper_from_ads_url(db_empty):
    db_empty.add_paper(u.mine.ads_url)
    # I won't test the value, just that it found something. I'll test values below
    assert db_empty.get_paper_attribute(u.mine.bibcode, "title") is not None


def test_add_paper_from_arvix_url(db_empty):
    db_empty.add_paper(u.mine.arxiv_url)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "title") is not None


def test_add_paper_from_arvix_url_v2(db_empty):
    db_empty.add_paper(u.mine.arxiv_url_v2)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "title") is not None


def test_add_paper_from_arxiv_id(db_empty):
    db_empty.add_paper(u.mine.arxiv_id)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "title") is not None


def test_add_paper_from_arxiv_pdf_url(db_empty):
    db_empty.add_paper(u.mine.arxiv_pdf_url)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "title") is not None


def test_add_paper_from_arxiv_pdf_url_v2(db_empty):
    db_empty.add_paper(u.mine.arxiv_pdf_url_v2)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "title") is not None


def test_add_paper_from_ads_bibcode(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "title") is not None


def test_add_unpublished_paper_from_ads_bibcode(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "title") is not None


# ======================================================================================
#
# test the accuracy of added paper details
#
# ======================================================================================
def test_added_paper_has_correct_bibcode(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "bibcode") == u.mine.bibcode


def test_added_paper_has_correct_title(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "title") == u.mine.title


def test_added_paper_has_correct_authors(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "authors") == u.mine.authors


def test_added_paper_has_correct_pubdate(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "pubdate") == u.mine.pubdate


def test_added_paper_has_correct_journal(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "journal") == u.mine.journal


def test_added_paper_has_correct_volume(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "volume") == u.mine.volume


def test_added_paper_has_correct_page(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "page") == u.mine.page


def test_added_paper_has_correct_abstract(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "abstract") == u.mine.abstract


def test_added_paper_has_correct_bibtex(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "bibtex") == u.mine.bibtex


def test_added_paper_has_correct_arxiv_id(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "arxiv_id") == u.mine.arxiv_id


def test_added_unpublished_paper_has_correct_bibcode(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "bibcode") == u.forbes.bibcode


def test_added_unpublished_paper_has_correct_title(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "title") == u.forbes.title


def test_added_unpublished_paper_has_correct_authors(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "authors") == u.forbes.authors


def test_added_unpublished_paper_has_correct_pubdate(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "pubdate") == u.forbes.pubdate


def test_added_unpublished_paper_has_correct_journal(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "journal") == u.forbes.journal


def test_added_unpublished_paper_has_correct_volume(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "volume") == u.forbes.volume


def test_added_unpublished_paper_has_correct_page(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "page") == u.forbes.page


def test_added_unpublished_paper_has_correct_abstract(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert (
        db_empty.get_paper_attribute(u.forbes.bibcode, "abstract") == u.forbes.abstract
    )


def test_added_unpublished_paper_has_correct_bibtex(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert db_empty.get_paper_attribute(u.forbes.bibcode, "bibtex") == u.forbes.bibtex


def test_added_unpublished_paper_has_correct_arxiv_id(db_empty):
    db_empty.add_paper(u.forbes.bibcode)
    assert (
        db_empty.get_paper_attribute(u.forbes.bibcode, "arxiv_id") == u.forbes.arxiv_id
    )


def test_added_not_on_arxiv_paper_has_correct_bibcode(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "bibcode") == u.bbfh.bibcode


def test_added_not_on_arxiv_paper_has_correct_title(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "title") == u.bbfh.title


def test_added_not_on_arxiv_paper_has_correct_authors(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "authors") == u.bbfh.authors


def test_added_not_on_arxiv_paper_has_correct_pubdate(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "pubdate") == u.bbfh.pubdate


def test_added_not_on_arxiv_paper_has_correct_journal(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "journal") == u.bbfh.journal


def test_added_not_on_arxiv_paper_has_correct_volume(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "volume") == u.bbfh.volume


def test_added_not_on_arxiv_paper_has_correct_page(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "page") == u.bbfh.page


def test_added_not_on_arxiv_paper_has_correct_abstract(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "abstract") == u.bbfh.abstract


def test_added_not_on_arxiv_paper_has_correct_bibtex(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert db_empty.get_paper_attribute(u.bbfh.bibcode, "bibtex") == u.bbfh.bibtex


def test_added_not_on_arxiv_paper_has_correct_arxiv_id(db_empty):
    db_empty.add_paper(u.bbfh.bibcode)
    assert (
        db_empty.get_paper_attribute(u.bbfh.bibcode, "arxiv_id") == "Not on the arXiv"
    )


def test_added_nonnumeric_page_paper_has_correct_page(db_empty):
    db_empty.add_paper(u.marks.bibcode)
    assert db_empty.get_paper_attribute(u.marks.bibcode, "page") == u.marks.page


def test_added_paper_returns_correct_bibcode(db_empty):
    test_bibcode = db_empty.add_paper(u.mine.ads_url)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "bibcode") == test_bibcode
    assert test_bibcode == u.mine.bibcode


def test_bibcode_correct_after_adding_paper(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "bibcode") == u.mine.bibcode


# ======================================================================================
#
# error checking of adding and getting paper attributes
#
# ======================================================================================
def test_error_raised_if_nonexistent_paper_is_searched_for(db_one):
    with pytest.raises(ValueError):
        db_one.get_paper_attribute(u.tremonti.bibcode, "bibcode")


def test_raise_custom_error_if_paper_is_already_in_database(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    with pytest.raises(PaperAlreadyInDatabaseError):
        db_empty.add_paper(u.mine.bibcode)
    assert db_empty.num_papers() == 1


def test_raises_errror_if_attribute_does_not_exist(db):
    with pytest.raises(ValueError):
        db.get_paper_attribute(u.mine.bibcode, "bad attribute")


def test_raise_error_when_attempting_to_modify_nonexistent_attribute(db):
    with pytest.raises(ValueError):
        db.set_paper_attribute(u.mine.bibcode, "slkdfsldkj", "New value")


def test_raise_error_when_attempting_to_modify_nonexistent_bibcode(db):
    with pytest.raises(ValueError):
        db.set_paper_attribute("sdlkfjsldfkj", "title", "new_title")


def test_raise_error_when_attempting_to_modify_value_with_wrong_data_type(db):
    with pytest.raises(ValueError):
        db.set_paper_attribute(u.mine.bibcode, "title", (4, 3))


# ======================================================================================
#
# test getting attribues
#
# ======================================================================================
def test_get_all_bibcodes_does_what_it_says(db):
    # already has two papers
    # sort the lists of bibcodes so comparison can be made
    test_bibcodes = sorted(db.get_all_bibcodes())
    true_bibcodes = sorted([u.mine.bibcode, u.tremonti.bibcode])
    assert test_bibcodes == true_bibcodes


def test_get_correct_attributes_title(db):
    assert db.get_paper_attribute(u.mine.bibcode, "title") == u.mine.title
    assert db.get_paper_attribute(u.tremonti.bibcode, "title") == u.tremonti.title


def test_get_correct_attributes_authors(db):
    assert db.get_paper_attribute(u.mine.bibcode, "authors") == u.mine.authors
    assert db.get_paper_attribute(u.tremonti.bibcode, "authors") == u.tremonti.authors


def test_get_correct_attributes_pubdate(db):
    assert db.get_paper_attribute(u.mine.bibcode, "pubdate") == u.mine.pubdate
    assert db.get_paper_attribute(u.tremonti.bibcode, "pubdate") == u.tremonti.pubdate


def test_get_correct_attributes_journal(db):
    assert db.get_paper_attribute(u.mine.bibcode, "journal") == u.mine.journal
    assert db.get_paper_attribute(u.tremonti.bibcode, "journal") == u.tremonti.journal


def test_get_correct_attributes_volume(db):
    assert db.get_paper_attribute(u.mine.bibcode, "volume") == u.mine.volume
    assert db.get_paper_attribute(u.tremonti.bibcode, "volume") == u.tremonti.volume


def test_get_correct_attributes_page(db):
    assert db.get_paper_attribute(u.mine.bibcode, "page") == u.mine.page
    assert db.get_paper_attribute(u.tremonti.bibcode, "page") == u.tremonti.page


def test_get_correct_attributes_abstract(db):
    assert db.get_paper_attribute(u.mine.bibcode, "abstract") == u.mine.abstract
    assert db.get_paper_attribute(u.tremonti.bibcode, "abstract") == u.tremonti.abstract


def test_get_correct_attributes_bibtex(db):
    assert db.get_paper_attribute(u.mine.bibcode, "bibtex") == u.mine.bibtex
    assert db.get_paper_attribute(u.tremonti.bibcode, "bibtex") == u.tremonti.bibtex


def test_accents_kept_in_author_list(db_empty):
    db_empty.add_paper(u.juan.url)
    assert db_empty.get_paper_attribute(u.juan.bibcode, "authors") == u.juan.authors


# ======================================================================================
#
# test modifying paper attributes
#
# ======================================================================================
def test_modify_title_as_an_example_with_set_paper_attribute(db):
    db.set_paper_attribute(u.mine.bibcode, "title", "New Title")
    assert db.get_paper_attribute(u.mine.bibcode, "title") == "New Title"


def test_modify_authors_list_with_set_paper_attribute(db):
    new_list = ["Last, First", "Last2, First2"]
    db.set_paper_attribute(u.mine.bibcode, "authors", new_list)
    assert db.get_paper_attribute(u.mine.bibcode, "authors") == new_list


# ======================================================================================
#
# local file
#
# ======================================================================================
def test_local_file_is_none_before_it_is_set(db):
    assert db.get_paper_attribute(u.mine.bibcode, "local_file") == None
    assert db.get_paper_attribute(u.tremonti.bibcode, "local_file") == None


def test_add_attribute_file_loc_is_done_correctly(db):
    test_loc = "/Users/gillenb/test.pdf"
    db.set_paper_attribute(u.mine.bibcode, "local_file", test_loc)
    assert db.get_paper_attribute(u.mine.bibcode, "local_file") == test_loc


# ======================================================================================
#
# test citation string
#
# ======================================================================================
def test_cite_string_one_author(db):
    db.set_paper_attribute(u.mine.bibcode, "authors", ["Brown, Gillen"])
    true_cite_string = f"Brown, 2018, ApJ, {u.mine.volume}, {u.mine.page}"
    assert db.get_cite_string(u.mine.bibcode) == true_cite_string


def test_cite_string_two_authors(db):
    new_authors = ["Brown, Gillen", "Gnedin, Oleg Y."]
    db.set_paper_attribute(u.mine.bibcode, "authors", new_authors)
    true_cite_string = f"Brown, Gnedin, 2018, ApJ, {u.mine.volume}, {u.mine.page}"
    assert db.get_cite_string(u.mine.bibcode) == true_cite_string


def test_cite_string_three_authors(db):
    # my paper already has three authors
    true_cite_string = f"Brown, Gnedin, Li, 2018, ApJ, {u.mine.volume}, {u.mine.page}"
    assert db.get_cite_string(u.mine.bibcode) == true_cite_string


def test_cite_string_four_authors_uses_et_al(db):
    new_authors = ["Brown, Gillen", "Gnedin, Oleg Y.", "Li, Hui", "Author, Test"]
    db.set_paper_attribute(u.mine.bibcode, "authors", new_authors)
    true_cite_string = f"Brown et al., 2018, ApJ, {u.mine.volume}, {u.mine.page}"
    assert db.get_cite_string(u.mine.bibcode) == true_cite_string


def test_cite_string_many_authors_uses_et_al(db):
    true_cite_string = (
        f"Tremonti et al., 2004, ApJ, " f"{u.tremonti.volume}, {u.tremonti.page}"
    )
    assert db.get_cite_string(u.tremonti.bibcode) == true_cite_string


def test_cite_string_apj_is_shortened(db):
    true_cite_string = f"Brown, Gnedin, Li, 2018, ApJ, {u.mine.volume}, {u.mine.page}"
    assert db.get_cite_string(u.mine.bibcode) == true_cite_string


def test_cite_string_apjs_is_shortened(db):
    bibcode = "2011ApJS..197...30Z"
    db.add_paper(bibcode)
    assert db.get_cite_string(bibcode) == "Zemp et al., 2011, ApJS, 197, 30"


def test_cite_string_mnras_is_shortened_test_paper(db):
    db.set_paper_attribute(
        u.mine.bibcode, "journal", "Monthly Notices of the Royal Astronomical Society"
    )
    true_cite_string = f"Brown, Gnedin, Li, 2018, MNRAS, {u.mine.volume}, {u.mine.page}"
    assert db.get_cite_string(u.mine.bibcode) == true_cite_string


def test_cite_string_aj_is_shortened(db):
    bibcode = "1999AJ....118..752Z"
    db.add_paper(bibcode)
    assert db.get_cite_string(bibcode) == "Zepf et al., 1999, AJ, 118, 752"


def test_cite_string_araa_is_shortened(db):
    bibcode = "2018ARA&A..56...83B"
    db.add_paper(bibcode)
    assert db.get_cite_string(bibcode) == "Bastian, Lardo, 2018, ARA&A, 56, 83"


def test_cite_string_pasp_is_shortened(db):
    bibcode = "2000PASP..112.1360A"
    db.add_paper(bibcode)
    assert db.get_cite_string(bibcode) == "Anderson, King, 2000, PASP, 112, 1360"


def test_cite_string_pasj_is_shortened(db):
    bibcode = "2021PASJ...73.1074F"
    db.add_paper(bibcode)
    assert db.get_cite_string(bibcode) == "Fujii et al., 2021, PASJ, 73, 1074"


def test_cite_string_nonnumeric_page_and_a_and_a_journal_shortened(db):
    db.add_paper(u.marks.bibcode)
    true_cite_string = "Marks, Kroupa, 2012, A&A, 543, A8"
    assert db.get_cite_string(u.marks.bibcode) == true_cite_string


def test_cite_string_a_and_a_supplment_shortened(db):
    bibcode = "1999A&AS..139..393L"
    db.add_paper(bibcode)
    assert db.get_cite_string(bibcode) == "Larsen, 1999, A&AS, 139, 393"


def test_cite_string_unpublished(db):
    db.add_paper(u.forbes.bibcode)
    true_cite_string = "Forbes, 2020, arXiv:2003.14327"
    assert db.get_cite_string(u.forbes.bibcode) == true_cite_string


def test_cite_string_no_page_no_arxiv(db):
    db.add_paper(u.grasha_thesis.bibcode)
    true_cite_string = "Grasha, 2018"
    assert db.get_cite_string(u.grasha_thesis.bibcode) == true_cite_string


# ======================================================================================
#
# tags
#
# ======================================================================================
def test_can_add_long_tag_to_database(db):
    new_tag = "a b c d e f g h i j k l m n o p q r s t u v w x y z"
    db.add_new_tag(new_tag)
    assert new_tag in db.get_all_tags()


def test_cannot_use_backticks_in_tag_name(db):
    with pytest.raises(ValueError):
        db.add_new_tag("`")


def test_cannot_use_square_brackets_in_tag_name(db):
    with pytest.raises(ValueError):
        db.add_new_tag("[")
    with pytest.raises(ValueError):
        db.add_new_tag("]")


def test_can_add_tag_with_punctuation(db):
    for t in punctuation_tags:
        db.add_new_tag(t)
        assert t in db.get_all_tags()


def test_can_add_new_tag_column_and_it_is_false_for_all_papers(db):
    db.add_new_tag("test_tag")
    for bibcode in db.get_all_bibcodes():
        assert db.paper_has_tag(bibcode, "test_tag") is False


def test_cannot_access_tags_from_get_paper_attribute(db):
    db.add_new_tag("test_tag")
    with pytest.raises(ValueError):
        db.get_paper_attribute(u.mine.bibcode, "test_tag")


def test_can_add_tag_to_a_paper(db):
    db.add_new_tag("test_tag")
    assert db.paper_has_tag(u.mine.bibcode, "test_tag") is False
    db.tag_paper(u.mine.bibcode, "test_tag")
    assert db.paper_has_tag(u.mine.bibcode, "test_tag") is True


def test_can_add_tag_with_punctuation_to_a_paper(db):
    for tag in punctuation_tags:
        db.add_new_tag(tag)
        db.tag_paper(u.mine.bibcode, tag)
        assert db.paper_has_tag(u.mine.bibcode, tag) is True


def test_can_add_tag_to_a_paper_and_only_that_paper_tagged(db):
    db.add_new_tag("test_tag")
    db.tag_paper(u.mine.bibcode, "test_tag")
    assert db.paper_has_tag(u.tremonti.bibcode, "test_tag") is False


def test_can_add_tag_with_spaces_to_a_paper(db):
    db.add_new_tag("test tag")
    assert db.paper_has_tag(u.mine.bibcode, "test tag") is False
    db.tag_paper(u.mine.bibcode, "test tag")
    assert db.paper_has_tag(u.mine.bibcode, "test tag") is True


def test_can_remove_tag_from_a_paper(db):
    db.add_new_tag("test")
    db.tag_paper(u.mine.bibcode, "test")
    assert db.paper_has_tag(u.mine.bibcode, "test") is True
    db.untag_paper(u.mine.bibcode, "test")
    assert db.paper_has_tag(u.mine.bibcode, "test") is False


def test_can_remove_tag_with_punctuation_to_a_paper(db):
    for tag in punctuation_tags:
        db.add_new_tag(tag)
        db.tag_paper(u.mine.bibcode, tag)
        assert db.paper_has_tag(u.mine.bibcode, tag) is True
        db.untag_paper(u.mine.bibcode, tag)
        assert db.paper_has_tag(u.mine.bibcode, tag) is False


def test_cannot_add_duplicate_tag_to_database(db):
    db.add_new_tag("test")
    with pytest.raises(ValueError):
        db.add_new_tag("test")


def test_cannot_add_duplicate_tag_capitalization_to_database(db):
    db.add_new_tag("test")
    with pytest.raises(ValueError):
        db.add_new_tag("TEST")


def test_cannot_add_empty_tag_to_database(db):
    with pytest.raises(ValueError):
        db.add_new_tag("   ")


def test_get_all_tags_is_sorted_ignoring_case(db):
    new_tags = ["ABC", "aaa", "zaa", "ZBB"]
    for t in new_tags:
        db.add_new_tag(t)
    assert db.get_all_tags() == sorted(new_tags, key=lambda x: x.lower())


def test_get_all_tags_on_a_paper_is_correct(db):
    for t in ["1", "2", "3", "A", "B", "C"]:
        db.add_new_tag(t)

    db.tag_paper(u.mine.bibcode, "1")
    db.tag_paper(u.mine.bibcode, "3")
    db.tag_paper(u.mine.bibcode, "B")
    assert db.get_paper_tags(u.mine.bibcode) == ["1", "3", "B"]


def test_get_all_tags_on_a_paper_is_sorted_ignoring_case(db):
    tags = ["abc", "ABZ", "zyx", "ZAA"]
    for t in tags:
        db.add_new_tag(t)
    # add extra not used by paper
    db.add_new_tag("slkdjlskdj")

    for t in tags:
        db.tag_paper(u.mine.bibcode, t)
    assert db.get_paper_tags(u.mine.bibcode) == sorted(tags, key=lambda x: x.lower())


def test_papers_unread_when_added(db_empty):
    db_empty.add_new_tag("Unread")
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_tags(u.mine.bibcode) == ["Unread"]


@pytest.mark.parametrize("tag", ["unread", "Unread", "UNREAD", "UnReAd"])
def test_papers_unread_when_added_capitalization(db_empty, tag):
    db_empty.add_new_tag(tag)
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_tags(u.mine.bibcode) == [tag]


# =============
# deleting tags
# =============
# I put this in a separate section since there's a lot of testing here, since I use
# the method of completely remaking the table just to delete one column. So I want to
# make sure nothing else gets messed up
def test_delete_tag_removed_from_db(db):
    db.add_new_tag("test_tag")
    assert db.get_all_tags() == ["test_tag"]
    db.delete_tag("test_tag")
    assert db.get_all_tags() == []


def test_delete_tag_removed_from_db_but_not_others(db):
    for t in ["1", "2", "3", "4", "5", "6"] + punctuation_tags:
        db.add_new_tag(t)
    db.delete_tag("3")
    assert db.get_all_tags() == sorted(["1", "2", "4", "5", "6"] + punctuation_tags)


def test_delete_tag_raises_error_if_not_exist(db):
    with pytest.raises(ValueError):
        db.delete_tag("test_tag")


def test_delete_nonexistent_tag_doesnt_mess_up_others(db):
    tags = ["1", "2", "3", "A", "B", "C"]
    for t in tags:
        db.add_new_tag(t)
    with pytest.raises(ValueError):
        db.delete_tag("test_tag")
    assert db.get_all_tags() == tags


def test_delete_tag_removes_it_from_papers(db):
    db.add_new_tag("test_tag")
    db.add_new_tag("test_tag 2")
    db.tag_paper(u.mine.bibcode, "test_tag")
    db.tag_paper(u.mine.bibcode, "test_tag 2")
    db.delete_tag("test_tag")
    assert db.get_paper_tags(u.mine.bibcode) == ["test_tag 2"]


def test_can_delete_tag_with_punctuation(db):
    for t in punctuation_tags:
        db.add_new_tag(t)
        db.delete_tag(t)
    assert db.get_all_tags() == []


def test_delete_tag_doesnt_mess_up_papers(db):
    db.add_new_tag("test_tag")
    db.tag_paper(u.mine.bibcode, "test_tag")
    db.delete_tag("test_tag")
    assert db.get_all_bibcodes() == [u.tremonti.bibcode, u.mine.bibcode]


def test_delete_tag_doesnt_mess_up_local_file(db):
    db.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    db.add_new_tag("test_tag")
    db.tag_paper(u.mine.bibcode, "test_tag")
    db.delete_tag("test_tag")
    assert db.get_paper_attribute(u.mine.bibcode, "local_file") == __file__


def test_delete_tag_doesnt_mess_up_user_notes(db):
    db.set_paper_attribute(u.mine.bibcode, "user_notes", "These are some great notes!")
    db.add_new_tag("test_tag")
    db.tag_paper(u.mine.bibcode, "test_tag")
    db.delete_tag("test_tag")
    assert (
        db.get_paper_attribute(u.mine.bibcode, "user_notes")
        == "These are some great notes!"
    )


def test_delete_tag_doesnt_mess_up_citation_keyword(db):
    db.set_paper_attribute(u.mine.bibcode, "citation_keyword", "brown_etal_18")
    db.add_new_tag("test_tag")
    db.tag_paper(u.mine.bibcode, "test_tag")
    db.delete_tag("test_tag")
    assert db.get_paper_attribute(u.mine.bibcode, "citation_keyword") == "brown_etal_18"


# ======================================================================================
#
# deleting papers
#
# ======================================================================================
def test_delete_paper_removes_one(db):
    assert db.num_papers() == 2
    db.delete_paper(u.mine.bibcode)
    assert db.num_papers() == 1


def test_delete_paper_removes_correct_one(db):
    db.delete_paper(u.mine.bibcode)
    # test that the paper left is not mine
    with pytest.raises(ValueError):
        db.get_paper_attribute(u.mine.bibcode, "title")


# ======================================================================================
#
# export papers of a given tag
#
# ======================================================================================
def test_export_all_papers(db):
    out_file_loc = Path(__file__).parent / "test.txt"
    db.export("all", out_file_loc)
    # read the file
    with open(out_file_loc, "r") as out_file:
        file_contents = out_file.read()
    # remove the file now before the test, so it always gets deleted
    out_file_loc.unlink()
    # then compare the contents to what we expect. The bibtex file should be in
    # order of date.
    expected_file_contents = u.tremonti.bibtex + "\n" + u.mine.bibtex + "\n"
    assert expected_file_contents == file_contents


def test_export_one_tag(db_empty):
    # the order of the bibtex fils should be in order of date, so we need to make
    # our list of papers in that order (since we'll use it to compare)
    papers_to_add = [u.bbfh, u.tremonti, u.mine, u.forbes]
    for paper in papers_to_add:
        db_empty.add_paper(paper.bibcode)
    # then tag a few of them
    db_empty.add_new_tag("test_tag")
    tagged_papers = papers_to_add[::2]
    for paper in tagged_papers:
        db_empty.tag_paper(paper.bibcode, "test_tag")
    # then export
    out_file_loc = Path(__file__).parent / "test.txt"
    db_empty.export("test_tag", out_file_loc)
    # read the file
    with open(out_file_loc, "r") as out_file:
        file_contents = out_file.read()
    # remove the file now before the test, so it always gets deleted
    out_file_loc.unlink()
    # then compare the contents to what we expect
    expected_file_contents = "\n".join([p.bibtex for p in tagged_papers]) + "\n"
    assert expected_file_contents == file_contents


def test_export_tag_with_no_papers(db):
    # add tag, but add no papers before exporting
    db.add_new_tag("empty")
    out_file_loc = Path(__file__).parent / "test.txt"
    db.export("empty", out_file_loc)
    # read the file
    with open(out_file_loc, "r") as out_file:
        file_contents = out_file.read()
    # remove the file now before the test, so it always gets deleted
    out_file_loc.unlink()
    # then compare the contents to what we expect
    assert file_contents == ""


def test_export_tag_does_not_exist_raises_error(db):
    with pytest.raises(ValueError):
        db.export("lklkjlkj", "test.txt")


# ======================================================================================
#
# user notes
#
# ======================================================================================
def test_user_notes_empty_at_start(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "user_notes") is None


def test_user_notes_can_be_saved(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    test_text = "testing testing testing"
    db_empty.set_paper_attribute(u.mine.bibcode, "user_notes", test_text)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "user_notes") == test_text


# ======================================================================================
#
# the update system
#
# ======================================================================================
# Test the updating of the database to get journal information for arXiv papers.
# Note that this updating is done on initialization, so we don't need to do anything
# to check that the update was done. The initial contents of the database will be
# wiped. Also note that in several of the later checks, I use the new bibcode rather
# than the old to access attributes, so that checks that it was updated too.
# Some more information on the database used here: I manually changed it to have the
# bibcode corresponding to the arXiv submission, then mangled all the other paper data.
# All of it should be replaced by the update system. I did enter some notes and a local
# file, so those should be kept by the system, along with the tags. I also saved a real
# entry from an arXiv paper before it was published, so I have a more realistic test
# too.
# first validate the testing database -- it should look strange
def test_validate_test_update_db():
    # I don't want to use the database code, since it automatically updates. So instead
    # to validate I copy some of the reading code from the database object and hack
    # it into here. It's ugly, but I like the interface to the database automatically
    # updating, so to test the un-updated version I need to do this.
    def sql(sql, parameters=()):
        db_loc = Path(__file__).parent / "testing_update.db"
        with contextlib.closing(sqlite3.connect(db_loc)) as conn:
            # using this factory makes the returned quantities easier to use
            conn.row_factory = sqlite3.Row
            with conn:  # auto commits changes to the database
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(sql, parameters)
                    return cursor.fetchall()

    old_bibcode_1, old_bibcode_2 = "2018arXiv180409819B", "2022arXiv220300559B"
    new_bibcodes = [p["bibcode"] for p in sql("SELECT bibcode FROM papers")]
    assert new_bibcodes == [
        u.tremonti.bibcode,
        u.grasha_thesis.bibcode,
        old_bibcode_1,
        u.forbes.bibcode,
        old_bibcode_2,
    ]
    t1 = sql("SELECT title FROM papers WHERE bibcode=?", (old_bibcode_1,))[0]["title"]
    assert t1 == "NSCs Rule!"

    t2 = sql("SELECT title FROM papers WHERE bibcode=?", (old_bibcode_2,))[0]["title"]
    assert (
        t2 == "Testing Feedback from Star Clusters in "
        "Simulations of the Milky Way Formation"
    )


def test_update_system_can_update_bibcode(db_update):
    # also checks that it does not crash for Grasha's thesis, which is not on the arxiv
    assert db_update.get_all_bibcodes() == [
        u.tremonti.bibcode,
        u.mine.bibcode,
        u.grasha_thesis.bibcode,
        u.forbes.bibcode,
        u.mine_recent.bibcode,
    ]


def test_update_system_can_update_title(db_update):
    for p in [u.mine, u.mine_recent]:
        assert db_update.get_paper_attribute(p.bibcode, "title") == p.title


def test_update_system_can_update_authors(db_update):
    for p in [u.mine, u.mine_recent]:
        assert db_update.get_paper_attribute(p.bibcode, "authors") == p.authors


def test_update_system_can_update_abstract(db_update):
    for p in [u.mine, u.mine_recent]:
        assert db_update.get_paper_attribute(p.bibcode, "abstract") == p.abstract


def test_update_system_can_update_pubdate(db_update):
    for p in [u.mine, u.mine_recent]:
        assert db_update.get_paper_attribute(p.bibcode, "pubdate") == p.pubdate


def test_update_system_gets_new_journal(db_update):
    for p in [u.mine, u.mine_recent]:
        assert db_update.get_paper_attribute(p.bibcode, "journal") == p.journal


def test_update_system_gets_new_volume(db_update):
    for p in [u.mine, u.mine_recent]:
        assert db_update.get_paper_attribute(p.bibcode, "volume") == p.volume


def test_update_system_gets_new_page(db_update):
    for p in [u.mine, u.mine_recent]:
        assert db_update.get_paper_attribute(p.bibcode, "page") == p.page


def test_update_system_does_not_change_arxiv_id(db_update):
    for p in [u.mine, u.mine_recent]:
        assert db_update.get_paper_attribute(p.bibcode, "arxiv_id") == p.arxiv_id


def test_update_system_does_not_update_citation_keyword_if_set(db_update):
    assert (
        db_update.get_paper_attribute(u.mine.bibcode, "citation_keyword")
        == "brown_etal_18"
    )


def test_update_system_updates_citation_keyword_if_not_set(db_update):
    assert (
        db_update.get_paper_attribute(u.mine_recent.bibcode, "citation_keyword")
        == u.mine_recent.bibcode
    )


def test_update_system_gets_new_bibtex(db_update):
    for p, key in zip(
        [u.mine, u.mine_recent], ["brown_etal_18", u.mine_recent.bibcode]
    ):
        # for each of these, replace the first line with the assigned key
        true_bibtex_lines = p.bibtex.split("\n")
        true_bibtex_lines[0] = "@ARTICLE{" + f"{key},"
        true_bibtex = "\n".join(true_bibtex_lines)
        assert db_update.get_paper_attribute(p.bibcode, "bibtex") == true_bibtex


def test_update_system_does_not_change_local_file(db_update):
    assert (
        db_update.get_paper_attribute(u.mine.bibcode, "local_file")
        == "/Users/gillenbrown/code/library/testing/test.pdf"
    )
    assert db_update.get_paper_attribute(u.mine_recent.bibcode, "local_file") == None


def test_update_system_does_not_change_tags(db_update):
    assert db_update.get_paper_tags(u.mine.bibcode) == ["test", "Unread"]
    assert db_update.get_paper_tags(u.mine_recent.bibcode) == ["Unread"]


def test_update_system_does_not_change_notes(db_update):
    assert (
        db_update.get_paper_attribute(u.mine.bibcode, "user_notes")
        == "Test notes are here!"
    )
    assert db_update.get_paper_attribute(u.mine_recent.bibcode, "user_notes") == None


def test_update_system_does_not_update_published_papers(db_update):
    assert (
        db_update.get_paper_attribute(u.tremonti.bibcode, "bibtex") == u.tremonti.bibtex
    )
    assert db_update.get_paper_attribute(u.forbes.bibcode, "bibtex") == u.forbes.bibtex


def test_update_system_does_not_run_soon_after_last_check(db_update, monkeypatch):
    # the update system runs automatically on creation. We'll make a new database
    # using the same file, but monkeypatch the update system to check what papers
    # are actually called to update
    updates = []
    monkeypatch.setattr(Database, "update_paper", lambda _, b: updates.append(b))
    print(db_update.db_file)
    Database(db_update.db_file)
    assert updates == []


def test_update_system_runs_again_after_a_day(db_update, monkeypatch):
    # the update system runs automatically on creation. We'll modify the update time
    # to be more than a day in the past, then make a new database using the same file.
    # We'll monkeypatch the update system to check what papers are actually called
    yesterday = time.time() - 25 * 60 * 60  # extra hour
    for bibcode in db_update.get_all_bibcodes():
        db_update.set_paper_attribute(bibcode, "update_time", yesterday)
    updates = []
    monkeypatch.setattr(Database, "update_paper", lambda _, b: updates.append(b))
    Database(db_update.db_file)
    assert updates == [u.grasha_thesis.bibcode, u.forbes.bibcode]


# ======================================================================================
#
# citation keyword
#
# ======================================================================================
def test_default_citation_keyword_is_bibcode(db):
    assert db.get_paper_attribute(u.mine.bibcode, "citation_keyword") == u.mine.bibcode


def test_can_change_citation_keyword(db):
    db.set_paper_attribute(u.mine.bibcode, "citation_keyword", "brown_etal_18")
    assert db.get_paper_attribute(u.mine.bibcode, "citation_keyword") == "brown_etal_18"


def test_duplicate_citation_keywords_not_allowed(db):
    db.set_paper_attribute(u.mine.bibcode, "citation_keyword", "brown_etal_18")
    with pytest.raises(RuntimeError):
        db.set_paper_attribute(u.tremonti.bibcode, "citation_keyword", "brown_etal_18")


def test_spaces_not_allowed_in_citation_keywords(db):
    with pytest.raises(ValueError):
        db.set_paper_attribute(u.mine.bibcode, "citation_keyword", "brown etal 18")


def test_blank_citation_keyword_not_allowed(db):
    with pytest.raises(ValueError):
        db.set_paper_attribute(u.mine.bibcode, "citation_keyword", "")


def test_bibtex_export_reflects_citation_keywords(db):
    db.set_paper_attribute(u.mine.bibcode, "citation_keyword", "brown_etal_18")
    test_bibtex = db.get_paper_attribute(u.mine.bibcode, "bibtex")
    # to see if mine works, manually replace the first line
    true_bibtex_lines = u.mine.bibtex.split("\n")
    true_bibtex_lines[0] = "@ARTICLE{brown_etal_18,"
    true_bibtex = "\n".join(true_bibtex_lines)
    assert test_bibtex == true_bibtex


def test_bibtex_export_reflects_citation_keywords_for_book(db):
    db.add_paper(u.mvdbw_book.bibcode)
    db.set_paper_attribute(u.mvdbw_book.bibcode, "citation_keyword", "mo_book")
    test_bibtex = db.get_paper_attribute(u.mvdbw_book.bibcode, "bibtex")
    true_bibtex = (
        "@BOOK{mo_book,\n"
        "       author = {{Mo}, Houjun and {van den Bosch}, "
        "Frank C. and {White}, Simon},\n"
        '        title = "{Galaxy Formation and Evolution}",\n'
        "         year = 2010,\n"
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/2010gfe..book.....M},\n"
        "      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n"
        "}\n"
        "\n"
        ""
    )
    assert true_bibtex == test_bibtex


# ======================================================================================
#
# import system
#
# ======================================================================================
def test_import_malformed_bibtex_fails(db_empty):
    file_loc = create_bibtex("@ARTICLE{\nsldkfjsldkfj\n}")
    db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert db_empty.get_all_bibcodes() == []


def test_import_single_good_paper_with_adsurl_adds_to_database(db_empty):
    file_loc = create_bibtex(u.mine.bibtex)
    db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert db_empty.get_all_bibcodes() == [u.mine.bibcode]


def test_import_single_good_paper_with_arxivid_adds_to_database(db_empty):
    bibtex = u.mine.bibtex.replace(
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/2018ApJ...864...94B},\n", ""
    )
    bibtex = bibtex.replace("          doi = {10.3847/1538-4357/aad595},\n", "")
    file_loc = create_bibtex(bibtex)
    db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert db_empty.get_all_bibcodes() == [u.mine.bibcode]


def test_import_two_good_papers_with_adsurl_adds_to_database(db_empty):
    file_loc = create_bibtex(u.mine.bibtex, u.tremonti.bibtex)
    db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert db_empty.get_all_bibcodes() == [u.tremonti.bibcode, u.mine.bibcode]


def test_import_return_tuple_bad_entry(db_empty):
    file_loc = create_bibtex("@ARTICLE{\nsldkfjsldkfj\n}")
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (0, 0, 1)


def test_import_return_tuple_one_good_paper(db_empty):
    file_loc = create_bibtex(u.mine.bibtex)
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (1, 0, 0)


def test_import_return_tuple_two_good_papers(db_empty):
    file_loc = create_bibtex(u.mine.bibtex, u.tremonti.bibtex)
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (2, 0, 0)


def test_import_return_tuple_duplicate(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    file_loc = create_bibtex(u.mine.bibtex)
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (0, 1, 0)


def test_import_return_tuple_internal_duplicate(db_empty):
    file_loc = create_bibtex(u.mine.bibtex, u.mine.bibtex)
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (1, 1, 0)


def test_import_return_tuple_one_good_one_duplicate(db_empty):
    db_empty.add_paper(u.mine.bibcode)
    file_loc = create_bibtex(u.mine.bibtex, u.tremonti.bibtex)
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (1, 1, 0)


def test_import_return_tuple_two_good_one_failure(db_empty):
    file_loc = create_bibtex(
        u.mine.bibtex, "@ARTICLE{\nsldkfjsldkfj\n}", u.tremonti.bibtex
    )
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (2, 0, 1)


def test_import_return_tuple_two_good_one_failure_one_duplicate(db_empty):
    file_loc = create_bibtex(
        u.mine.bibtex, "@ARTICLE{\nsldkfjsldkfj\n}", u.tremonti.bibtex, u.mine.bibtex
    )
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (2, 1, 1)


def test_import_return_tuple_could_not_identify_paper(db_empty):
    # modify a bibtex file to be unidentifiable
    file_loc = create_bibtex(
        "@ARTICLE{1957RvMP...29..547B,\n"
        " author = {{Burbidge}, E. Margaret},\n"
        '  title = "{Synthesis of the Elements in Stars},"\n'
        "journal = {Reviews of Modern Physics},\n"
        "   year = 1957,\n"
        "}"
    )
    results = db_empty.import_bibtex(file_loc)
    file_loc.unlink()  # delete before tests may fail
    assert results == (0, 0, 1)
