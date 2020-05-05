import pytest

from library.ads_wrapper import ADSWrapper
import test_utils as u

ads_call = ADSWrapper()


def test_cache_no_extra_queries_bibcode():
    # here I'll query the same pre-existing paper with multiple URLs to ensure
    # that the caching is working as expected. I first have to make sure
    # everything is in the cache, so I need to do all needed searches, then I
    # can duplicate them
    _ = ads_call.get_bibcode(u.my_arxiv_url)
    queries_start = ads_call.num_queries
    _ = ads_call.get_bibcode(u.my_ads_url)
    _ = ads_call.get_bibcode(u.my_arxiv_url)
    _ = ads_call.get_bibcode(u.my_arxiv_pdf_url)
    queries_new = ads_call.num_queries

    assert queries_new == queries_start


def test_cache_no_extra_queries_bibtex():
    # here I'll query the same pre-existing paper twoce to make sure
    # that the caching is working as expected. I first have to make sure
    # everything is in the cache, so I need to do all needed searches, then I
    # can duplicate them
    _ = ads_call.get_bibtex(u.my_bibcode)
    queries_start = ads_call.num_queries
    _ = ads_call.get_bibcode(u.my_bibcode)
    queries_new = ads_call.num_queries

    assert queries_new == queries_start


def test_get_bibcode_from_ads():
    bibcode = ads_call.get_bibcode(u.my_ads_url)
    assert bibcode == u.my_bibcode


def test_get_bibcode_from_ads_bibcode():
    bibcode = ads_call.get_bibcode(u.my_bibcode)
    assert bibcode == u.my_bibcode


def test_get_bibcode_from_arxiv_id():
    bibcode = ads_call.get_bibcode(u.my_arxiv_id)
    assert bibcode == u.my_bibcode


def test_get_bibcode_from_arxiv_url():
    bibcode = ads_call.get_bibcode(u.my_arxiv_url)
    assert bibcode == u.my_bibcode


def test_get_bibcode_from_arxiv_url_v2():
    bibcode = ads_call.get_bibcode(u.my_arxiv_url_v2)
    assert bibcode == u.my_bibcode


def test_get_bibcode_from_arxiv_pdf():
    bibcode = ads_call.get_bibcode(u.my_arxiv_pdf_url)
    assert bibcode == u.my_bibcode


def test_get_bibcode_from_arxiv_pdf_v2():
    bibcode = ads_call.get_bibcode(u.my_arxiv_pdf_url_v2)
    assert bibcode == u.my_bibcode


def test_bibcode_error_from_other_source():
    with pytest.raises(ValueError):
        ads_call.get_bibcode("www.wrong.com")


def test_get_bibtex():
    bibtex = ads_call.get_bibtex(u.my_bibcode)
    assert bibtex == u.my_bibtex


# TODO: test that adding papers from one of multiple ADS links gives the same paper
