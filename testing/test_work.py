import pytest

from library.work import Paper
import test_utils as u

@pytest.fixture(name="paper")
def fixture_ads_paper():
    return Paper(u.my_ads_url)

def test_cache_no_extra_queries(paper):
    # here I'll query the same pre-existing paper with multiple URLs to ensure
    # that the caching is working as expected I first have to make sure
    # everything is in the cache, so I need to do all needed searches, then I
    # can duplicate them
    _ = Paper(u.my_arxiv_url)
    queries_start = paper.num_queries
    _ = Paper(u.my_ads_url)
    _ = Paper(u.my_arxiv_url)
    p = Paper(u.my_arxiv_pdf_url)
    queries_new = paper.num_queries
    queries_other = p.num_queries  # check that it's shared between objects

    assert queries_new == queries_start
    assert queries_new == queries_other

def test_get_bibtex_from_ads(paper):
    assert paper.bibtex_entry == u.my_bibtex

def test_create_paper_from_arxiv(paper):
    arxiv_paper = Paper(u.my_arxiv_url)
    # same as above test, just with arxiv link
    assert arxiv_paper.bibtex_entry == paper.bibtex_entry

def test_create_paper_from_arxiv_pdf(paper):
    arxiv_paper = Paper(u.my_arxiv_pdf_url)
    # same as above test, just with arxiv link to the pdf
    assert arxiv_paper.bibtex_entry == paper.bibtex_entry



#TODO: test that adding papers from one of multiple ADS links gives the same paper