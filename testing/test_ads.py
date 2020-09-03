import datetime

import pytest

from library.ads_wrapper import ADSWrapper
import test_utils as u

ads_call = ADSWrapper()


def test_cache_no_extra_queries_with_same_arxiv_to_bibcode_query():
    # here I'll query the same pre-existing paper with multiple URLs to ensure that
    # the caching is working as expected. I first have to make sure everything is in
    # the cache, so I need to do all needed searches, then I can duplicate them
    _ = ads_call.get_bibcode(u.my_arxiv_url)
    queries_start = ads_call.num_queries
    _ = ads_call.get_bibcode(u.my_ads_url)
    _ = ads_call.get_bibcode(u.my_arxiv_url)
    _ = ads_call.get_bibcode(u.my_arxiv_pdf_url)
    queries_new = ads_call.num_queries

    assert queries_new == queries_start


def test_cache_no_extra_queries_for_same_full_info_from_bibcode_query():
    # here I'll query the same pre-existing paper twoce to make sure that the caching
    # is working as expected. I first have to make sure everything is in the cache,
    # so I need to do all needed searches, then I can duplicate them
    _ = ads_call.get_info(u.my_bibcode)
    queries_start = ads_call.num_queries
    _ = ads_call.get_info(u.my_bibcode)
    queries_new = ads_call.num_queries

    assert queries_new == queries_start


def test_get_correct_bibcode_from_ads_url():
    bibcode = ads_call.get_bibcode(u.my_ads_url)
    assert bibcode == u.my_bibcode


def test_get_correct_bibcode_from_ads_bibcode():
    bibcode = ads_call.get_bibcode(u.my_bibcode)
    assert bibcode == u.my_bibcode


def test_get_correct_bibcode_from_arxiv_id():
    bibcode = ads_call.get_bibcode(u.my_arxiv_id)
    assert bibcode == u.my_bibcode


def test_get_correct_bibcode_from_arxiv_url():
    bibcode = ads_call.get_bibcode(u.my_arxiv_url)
    assert bibcode == u.my_bibcode


def test_get_correct_bibcode_from_arxiv_url_v2():
    bibcode = ads_call.get_bibcode(u.my_arxiv_url_v2)
    assert bibcode == u.my_bibcode


def test_get_correct_bibcode_from_arxiv_pdf_url():
    bibcode = ads_call.get_bibcode(u.my_arxiv_pdf_url)
    assert bibcode == u.my_bibcode


def test_get_correct_bibcode_from_arxiv_pdf_url_v2():
    bibcode = ads_call.get_bibcode(u.my_arxiv_pdf_url_v2)
    assert bibcode == u.my_bibcode


def test_raises_error_for_unrecognized_identifier():
    with pytest.raises(ValueError):
        ads_call.get_bibcode("www.wrong.com")


def test_get_correct_paper_title():
    results = ads_call.get_info(u.my_bibcode)
    assert results["title"] == u.my_title


def test_get_correct_paper_bibtex():
    results = ads_call.get_info(u.my_bibcode)
    assert results["bibtex"] == u.my_bibtex


def test_get_correct_paper_authors():
    results = ads_call.get_info(u.my_bibcode)
    assert results["authors"] == u.my_authors


def test_get_correct_paper_pubdate():
    results = ads_call.get_info(u.my_bibcode)
    assert results["pubdate"] == u.my_pubdate


def test_get_correct_paper_abstract():
    results = ads_call.get_info(u.my_bibcode)
    assert results["abstract"] == u.my_abstract


def test_get_correct_paper_journal():
    results = ads_call.get_info(u.my_bibcode)
    assert results["journal"] == u.my_journal


def test_get_correct_paper_volume():
    results = ads_call.get_info(u.my_bibcode)
    assert results["volume"] == u.my_volume


def test_get_correct_paper_page():
    results = ads_call.get_info(u.my_bibcode)
    assert results["page"] == u.my_page


def test_get_correct_paper_title_unpublished():
    results = ads_call.get_info(u.forbes_bibcode)
    assert results["title"] == u.forbes_title


def test_get_correct_paper_bibtex_unpublished():
    results = ads_call.get_info(u.forbes_bibcode)
    assert results["bibtex"] == u.forbes_bibtex


def test_get_correct_paper_authors_unpublished():
    results = ads_call.get_info(u.forbes_bibcode)
    assert results["authors"] == u.forbes_authors


def test_get_correct_paper_pubdate_unpublished():
    results = ads_call.get_info(u.forbes_bibcode)
    assert results["pubdate"] == u.forbes_pubdate


def test_get_correct_paper_abstract_unpublished():
    results = ads_call.get_info(u.forbes_bibcode)
    assert results["abstract"] == u.forbes_abstract


def test_get_correct_paper_journal_unpublished():
    results = ads_call.get_info(u.forbes_bibcode)
    assert results["journal"] == u.forbes_journal


def test_get_correct_paper_volume_unpublished():
    results = ads_call.get_info(u.forbes_bibcode)
    assert results["volume"] == u.forbes_volume


def test_get_correct_paper_page_unpublished():
    results = ads_call.get_info(u.forbes_bibcode)
    assert results["page"] == u.forbes_page
