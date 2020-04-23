import pytest

from library.work import Work, Paper
import test_utils as u

@pytest.fixture
def ads_paper():
    return Paper(u.my_ads_url)

def test_get_bibtex_from_ads(ads_paper):
    assert ads_paper.bibtex_entry == u.my_bibtex

def test_create_paper_from_arxiv(ads_paper):
    arxiv_paper = Paper(u.my_arxiv_url)
    # same as above test, just with arxiv link
    assert arxiv_paper.bibtex_entry == ads_paper.bibtex_entry

def test_create_paper_from_arxiv_pdf(ads_paper):
    arxiv_paper = Paper(u.my_arxiv_pdf_url)
    # same as above test, just with arxiv link
    assert arxiv_paper.bibtex_entry == ads_paper.bibtex_entry

#TODO: test that adding papers from one of multiple ADS links gives the same paper