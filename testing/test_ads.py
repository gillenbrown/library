import pytest

from library.ads_wrapper import ADSWrapper
import test_utils as u

ads_call = ADSWrapper()

def test_cache_no_extra_queries():
    # here I'll query the same pre-existing paper with multiple URLs to ensure
    # that the caching is working as expected I first have to make sure
    # everything is in the cache, so I need to do all needed searches, then I
    # can duplicate them
    _ = ads_call.get_bibtex(u.my_arxiv_url)
    queries_start = ads_call.num_queries
    _ = ads_call.get_bibtex(u.my_ads_url)
    _ = ads_call.get_bibtex(u.my_arxiv_url)
    _ = ads_call.get_bibtex(u.my_arxiv_pdf_url)
    queries_new = ads_call.num_queries

    assert queries_new == queries_start

def test_get_bibtex_from_ads():
    bibtex = ads_call.get_bibtex(u.my_ads_url)
    assert bibtex == u.my_bibtex

def test_create_paper_from_arxiv():
    bibtex = ads_call.get_bibtex(u.my_arxiv_url)
    # same as above test, just with arxiv link
    assert bibtex == u.my_bibtex

def test_create_paper_from_arxiv_pdf():
    bibtex = ads_call.get_bibtex(u.my_arxiv_pdf_url)
    # same as above test, just with arxiv link to the pdf
    assert bibtex == u.my_bibtex

#TODO: test that adding papers from one of multiple ADS links gives the same paper