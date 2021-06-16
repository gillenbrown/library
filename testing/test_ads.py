import datetime

import pytest

from library.ads_wrapper import ADSWrapper
import test_utils as u

ads_call = ADSWrapper()


def test_cache_no_extra_queries_with_same_arxiv_to_bibcode_query():
    # here I'll query the same pre-existing paper with multiple URLs to ensure that
    # the caching is working as expected. I first have to make sure everything is in
    # the cache, so I need to do all needed searches, then I can duplicate them
    _ = ads_call.get_bibcode(u.mine.arxiv_url)
    queries_start = ads_call.num_queries
    _ = ads_call.get_bibcode(u.mine.ads_url)
    _ = ads_call.get_bibcode(u.mine.arxiv_url)
    _ = ads_call.get_bibcode(u.mine.arxiv_pdf_url)
    queries_new = ads_call.num_queries

    assert queries_new == queries_start


def test_cache_no_extra_queries_for_same_full_info_from_bibcode_query():
    # here I'll query the same pre-existing paper twoce to make sure that the caching
    # is working as expected. I first have to make sure everything is in the cache,
    # so I need to do all needed searches, then I can duplicate them
    _ = ads_call.get_info(u.mine.bibcode)
    queries_start = ads_call.num_queries
    _ = ads_call.get_info(u.mine.bibcode)
    queries_new = ads_call.num_queries

    assert queries_new == queries_start


def test_get_correct_bibcode_from_ads_url():
    bibcode = ads_call.get_bibcode(u.mine.ads_url)
    assert bibcode == u.mine.bibcode


def test_get_correct_bibcode_from_ads_url_with_and_symbol():
    bibcode = ads_call.get_bibcode(u.krumholz.url)
    assert bibcode == u.krumholz.bibcode


def test_get_correct_bibcode_from_ads_bibcode():
    bibcode = ads_call.get_bibcode(u.mine.bibcode)
    assert bibcode == u.mine.bibcode


def test_get_correct_bibcode_from_arxiv_id():
    bibcode = ads_call.get_bibcode(u.mine.arxiv_id)
    assert bibcode == u.mine.bibcode


def test_get_correct_bibcode_from_arxiv_url():
    bibcode = ads_call.get_bibcode(u.mine.arxiv_url)
    assert bibcode == u.mine.bibcode


def test_get_correct_bibcode_from_arxiv_url_v2():
    bibcode = ads_call.get_bibcode(u.mine.arxiv_url_v2)
    assert bibcode == u.mine.bibcode


def test_get_correct_bibcode_from_arxiv_pdf_url():
    bibcode = ads_call.get_bibcode(u.mine.arxiv_pdf_url)
    assert bibcode == u.mine.bibcode


def test_get_correct_bibcode_from_arxiv_pdf_url_v2():
    bibcode = ads_call.get_bibcode(u.mine.arxiv_pdf_url_v2)
    assert bibcode == u.mine.bibcode


def test_raises_error_for_unrecognized_identifier():
    with pytest.raises(ValueError):
        ads_call.get_bibcode("www.wrong.com")


def test_get_correct_paper_title():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["title"] == u.mine.title


def test_get_correct_paper_bibtex():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["bibtex"] == u.mine.bibtex


def test_get_correct_paper_authors():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["authors"] == u.mine.authors


def test_get_correct_paper_pubdate():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["pubdate"] == u.mine.pubdate


def test_get_correct_paper_abstract():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["abstract"] == u.mine.abstract


def test_get_correct_paper_journal():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["journal"] == u.mine.journal


def test_get_correct_paper_volume():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["volume"] == u.mine.volume


def test_get_correct_paper_page():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["page"] == u.mine.page


def test_get_correct_paper_arxiv_id():
    results = ads_call.get_info(u.mine.bibcode)
    assert results["arxiv_id"] == u.mine.arxiv_id


def test_get_correct_paper_title_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["title"] == u.forbes.title


def test_get_correct_paper_bibtex_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["bibtex"] == u.forbes.bibtex


def test_get_correct_paper_authors_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["authors"] == u.forbes.authors


def test_get_correct_paper_pubdate_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["pubdate"] == u.forbes.pubdate


def test_get_correct_paper_abstract_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["abstract"] == u.forbes.abstract


def test_get_correct_paper_journal_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["journal"] == u.forbes.journal


def test_get_correct_paper_volume_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["volume"] == u.forbes.volume


def test_get_correct_paper_page_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["page"] == u.forbes.page


def test_get_correct_paper_arxiv_id_unpublished():
    results = ads_call.get_info(u.forbes.bibcode)
    assert results["arxiv_id"] == u.forbes.arxiv_id


def test_get_correct_paper_title_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["title"] == u.bbfh.title


def test_get_correct_paper_bibtex_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["bibtex"] == u.bbfh.bibtex


def test_get_correct_paper_authors_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["authors"] == u.bbfh.authors


def test_get_correct_paper_pubdate_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["pubdate"] == u.bbfh.pubdate


def test_get_correct_paper_abstract_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["abstract"] == u.bbfh.abstract


def test_get_correct_paper_journal_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["journal"] == u.bbfh.journal


def test_get_correct_paper_volume_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["volume"] == u.bbfh.volume


def test_get_correct_paper_page_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["page"] == u.bbfh.page


def test_get_correct_paper_arxiv_id_not_on_arxiv():
    results = ads_call.get_info(u.bbfh.bibcode)
    assert results["arxiv_id"] == "Not on the arXiv"


def test_get_correct_page_nonnumeric_page():
    results = ads_call.get_info(u.marks.bibcode)
    assert results["page"] == u.marks.page
