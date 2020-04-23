import pytest

from library.work import Paper
import test_utils as u

@pytest.fixture(name="paper")
def fixture_ads_paper():
    return Paper(u.my_ads_url)

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

def test_bibtex_cache(paper):
    # this cache will already be created.
    assert paper._bibtexs_from_bibcode[u.my_bibcode] == u.my_bibtex

def test_arxiv_to_bibcode_cache(paper):
    # to make sure the cache exists I'll add the paper via arxiv link
    _ = Paper(u.my_arxiv_pdf_url)
    # then test the original cache, to ensure it's shared
    assert paper._bibcode_from_arxiv_id[u.my_arxiv_id] == u.my_bibcode

def test_no_extra_queries(paper):
    # here I'll query the same pre-existing paper with multiple URLs to ensure
    # that the caching is working as expected
    queries_start = paper.num_queries
    _ = Paper(u.my_ads_url)
    _ = Paper(u.my_arxiv_url)
    p = Paper(u.my_arxiv_pdf_url)
    queries_new = p.num_queries

    assert queries_new == queries_start

#TODO: test that adding papers from one of multiple ADS links gives the same paper