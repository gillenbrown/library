import datetime

import pytest

from library.ads_wrapper import ADSWrapper
import test_utils as u

ads_call = ADSWrapper()


def test_num_queries():
    # must be done first, to test that the dummy query system works
    assert 0 <= ads_call.num_queries() <= 5000


def test_cache_no_extra_queries_with_same_arxiv_to_bibcode_query():
    # here I'll query the same pre-existing paper with multiple URLs to ensure that
    # the caching is working as expected. I first have to make sure everything is in
    # the cache, so I need to do all needed searches, then I can duplicate them
    _ = ads_call.get_bibcode(u.mine.arxiv_url)
    queries_start = ads_call.num_queries()
    _ = ads_call.get_bibcode(u.mine.ads_url)
    _ = ads_call.get_bibcode(u.mine.arxiv_url)
    _ = ads_call.get_bibcode(u.mine.arxiv_pdf_url)
    queries_new = ads_call.num_queries()

    assert queries_new == queries_start


def test_cache_no_extra_queries_with_same_doi():
    # here I'll query the same pre-existing paper with multiple URLs to ensure that
    # the caching is working as expected. I first have to make sure everything is in
    # the cache, so I need to do all needed searches, then I can duplicate them
    _ = ads_call.get_bibcode(u.mine.doi)
    queries_start = ads_call.num_queries()
    _ = ads_call.get_bibcode(u.mine.doi)

    assert ads_call.num_queries() == queries_start


def test_cache_no_extra_queries_for_same_full_info_from_bibcode_query():
    # here I'll query the same pre-existing paper twoce to make sure that the caching
    # is working as expected. I first have to make sure everything is in the cache,
    # so I need to do all needed searches, then I can duplicate them
    _ = ads_call.get_info(u.mine.bibcode)
    queries_start = ads_call.num_queries()
    _ = ads_call.get_info(u.mine.bibcode)
    queries_new = ads_call.num_queries()

    assert queries_new == queries_start


# ======================================================================================
#
# Test getting bibcodes from various URLs
#
# ======================================================================================
def test_get_correct_bibcode_from_ads_url():
    assert ads_call.get_bibcode(u.mine.ads_url) == u.mine.bibcode


def test_get_correct_bibcode_from_ads_url_with_and_symbol():
    assert ads_call.get_bibcode(u.krumholz.url) == u.krumholz.bibcode


def test_get_correct_bibcode_from_oldstyle_ads_url():
    url = f"http://adsabs.harvard.edu/abs/{u.mine.bibcode}"
    assert ads_call.get_bibcode(url) == u.mine.bibcode


def test_get_correct_bibcode_from_ads_url_with_outdated_bibcode():
    assert ads_call.get_bibcode(u.mine.ads_url_old) == u.mine.bibcode


def test_get_correct_bibcode_from_ads_url_with_outdated_bibcode_old_arxiv():
    assert ads_call.get_bibcode(u.marks.url_old) == u.marks.bibcode


def test_get_correct_bibcode_from_ads_bibcode():
    assert ads_call.get_bibcode(u.mine.bibcode) == u.mine.bibcode


def test_get_correct_bibcode_from_ads_bibcode_old():
    assert ads_call.get_bibcode(u.mine.bibcode_old) == u.mine.bibcode


def test_get_correct_bibcode_from_ads_bibcode_old_arxiv():
    assert ads_call.get_bibcode(u.marks.bibcode_old) == u.marks.bibcode


def test_get_correct_bibcode_from_arxiv_id():
    assert ads_call.get_bibcode(u.mine.arxiv_id) == u.mine.bibcode


def test_get_correct_bibcode_from_old_arxiv_id():
    assert ads_call.get_bibcode(u.tremonti.arxiv_id) == u.tremonti.bibcode


def test_get_correct_bibcode_from_old_arxiv_id_style_2():
    assert ads_call.get_bibcode("arXiv:" + u.tremonti.arxiv_id) == u.tremonti.bibcode


def test_get_correct_bibcode_from_arxiv_url():
    assert ads_call.get_bibcode(u.mine.arxiv_url) == u.mine.bibcode


def test_get_correct_bibcode_from_arxiv_url_v2():
    assert ads_call.get_bibcode(u.mine.arxiv_url_v2) == u.mine.bibcode


def test_get_correct_bibcode_from_old_arxiv_url():
    assert ads_call.get_bibcode(u.tremonti.arxiv_url) == u.tremonti.bibcode


def test_get_correct_bibcode_from_arxiv_pdf_url():
    assert ads_call.get_bibcode(u.mine.arxiv_pdf_url) == u.mine.bibcode


def test_get_correct_bibcode_from_arxiv_pdf_url_v2():
    assert ads_call.get_bibcode(u.mine.arxiv_pdf_url_v2) == u.mine.bibcode


def test_get_correct_bibcode_from_doi():
    assert ads_call.get_bibcode(u.mine.doi) == u.mine.bibcode


def test_get_correct_bibcode_from_doi_with_special_characters():
    assert ads_call.get_bibcode(u.larsen.doi) == u.larsen.bibcode


def test_get_correct_bibcode_from_doi_arxivlike():
    assert ads_call.get_bibcode(u.sellwood_binney.doi) == u.sellwood_binney.bibcode


def test_raises_error_for_unrecognized_identifier():
    with pytest.raises(ValueError):
        ads_call.get_bibcode("www.wrong.com")


def test_raises_error_for_doi_that_doesnt_exist_on_ads():
    with pytest.raises(ValueError):
        ads_call.get_bibcode("10.1000/182")


def test_raises_error_for_arxiv_paper_not_on_ads():
    # use an identifier from the future (Jan 2035, to be specific)
    with pytest.raises(ValueError):
        ads_call.get_bibcode("https://arxiv.org/abs/3501.00001")


def test_raises_error_for_adsurl_with_bad_bibcode():
    with pytest.raises(ValueError):
        ads_call.get_bibcode("http://adsabs.harvard.edu/abs/2007ARA\\%26A..45..565M")


# ======================================================================================
#
# Test getting bibcodes from various journal details
#
# ======================================================================================
def test_get_paper_from_journal_details():
    bibcode = ads_call.get_bibcode_from_journal(
        year=u.mine.year,
        journal=u.mine.journal,
        volume=u.mine.volume,
        page=u.mine.page,
        title=u.mine.title,
    )
    assert bibcode == u.mine.bibcode


def test_get_paper_from_journal_details_short_journal():
    bibcode = ads_call.get_bibcode_from_journal(
        year=u.mine.year,
        journal="\\apj",
        volume=u.mine.volume,
        page=u.mine.page,
        title=u.mine.title,
    )
    assert bibcode == u.mine.bibcode


def test_get_paper_from_journal_details_validates_title_correct():
    bibcode = ads_call.get_bibcode_from_journal(
        year=u.mine.year,
        journal=u.mine.journal,
        volume=u.mine.volume,
        page=u.mine.page,
        title=u.mine.title,
    )
    assert bibcode == u.mine.bibcode


def test_get_paper_from_journal_details_validates_title_lowercase_correct():
    bibcode = ads_call.get_bibcode_from_journal(
        year=u.mine.year,
        journal=u.mine.journal,
        volume=u.mine.volume,
        page=u.mine.page,
        title=u.mine.title.lower(),
    )
    assert bibcode == u.mine.bibcode


def test_get_paper_from_journal_details_works_for_slightly_different_titles():
    # this test inspired by some old papers that have a period at the end, which
    # was not in some bibtex files I tested with
    bibcode = ads_call.get_bibcode_from_journal(
        year=u.mine.year,
        journal=u.mine.journal,
        volume=u.mine.volume,
        page=u.mine.page,
        title=u.mine.title.lower() + ".",
    )
    assert bibcode == u.mine.bibcode


def test_get_paper_from_journal_details_doesnt_work_for_different_titles():
    # make sure fuzzy string matching isn't too fuzzy
    with pytest.raises(ValueError):
        ads_call.get_bibcode_from_journal(
            year=u.mine.year,
            journal=u.mine.journal,
            volume=u.mine.volume,
            page=u.mine.page,
            title="Test " + u.mine.title.lower() + ".",
        )


def test_get_paper_from_journal_details_works_when_bibstem_not_found():
    bibcode = ads_call.get_bibcode_from_journal(
        title=u.williams.title,
        year=u.williams.year,
        authors=u.williams.authors_bibtex,
        journal=u.williams.journal,
    )
    assert bibcode == u.williams.bibcode


def test_get_paper_from_journal_details_works_with_punctuation():
    bibcode = ads_call.get_bibcode_from_journal(
        title=u.carney.title, year=u.carney.year
    )
    assert bibcode == u.carney.bibcode


def test_get_paper_from_journal_details_works_with_punctuation_2():
    bibcode = ads_call.get_bibcode_from_journal(
        title=u.meylan.title, year=u.meylan.year
    )
    assert bibcode == u.meylan.bibcode


def test_get_paper_from_journal_details_works_with_accent_in_author():
    bibcode = ads_call.get_bibcode_from_journal(
        authors=u.juan.bibtex_authors,
        year=u.juan.year,
        pages=u.juan.page,
        volume=u.juan.volume,
        journal=u.juan.journal,
    )
    assert bibcode == u.juan.bibcode


def test_get_paper_from_journal_details_works_with_nonbreaking_space_in_author():
    bibcode = ads_call.get_bibcode_from_journal(
        authors=u.anders.bibtex_authors,
        year=u.anders.year,
        journal=u.anders.journal,
        title=u.anders.title,
    )
    assert bibcode == u.anders.bibcode


def test_get_paper_from_journal_works_with_and_in_author_name():
    bibcode = ads_call.get_bibcode_from_journal(
        authors=u.chandar.bibtex_authors,
        year=u.chandar.year,
        volume=u.chandar.volume,
        page=u.chandar.page,
    )
    assert bibcode == u.chandar.bibcode


def test_get_paper_from_journal_details_sparse_works():
    bibcode = ads_call.get_bibcode_from_journal(
        title=u.kravtsov.title,
        year=u.kravtsov.year,
        authors=u.kravtsov.authors_bibtex,
    )
    assert bibcode == u.kravtsov.bibcode


def test_get_paper_from_journal_details_sparse_works_2():
    bibcode = ads_call.get_bibcode_from_journal(
        year=2018,
        author="{Brown}, Gillen and {Gnedin}, Oleg Y. and {Li}, Hui",
    )
    assert bibcode == u.mine.bibcode


def test_get_paper_from_journal_details_too_sparse_raises_error():
    with pytest.raises(ValueError) as e:
        ads_call.get_bibcode_from_journal(year="2018")
    assert str(e.value) == "multiple papers found that match this info"


def test_get_paper_from_journal_details_too_sparse_raises_error_2():
    with pytest.raises(ValueError) as e:
        ads_call.get_bibcode_from_journal()
    assert str(e.value) == "not enough publication details to uniquely identify paper"


def test_get_paper_from_journal_details_not_found_raises_error():
    with pytest.raises(ValueError) as e:
        ads_call.get_bibcode_from_journal(
            year=u.mine.year,
            journal=u.mine.journal,
            volume=u.mine.volume,
            page=u.mine.page,
            title="nonsense",
        )
    assert str(e.value) == "couldn't find paper with an exact match to this info on ADS"


def test_get_paper_from_journal_details_not_found_raises_error_2():
    with pytest.raises(ValueError) as e:
        ads_call.get_bibcode_from_journal(
            year="2035",
            journal=u.mine.journal,
            volume=u.mine.volume,
            page=u.mine.page,
            title=u.mine.title,
        )
    assert str(e.value) == "couldn't find paper with an exact match to this info on ADS"


def test_get_paper_from_journal_details_not_found_raises_error_3():
    with pytest.raises(ValueError) as e:
        ads_call.get_bibcode_from_journal(
            year=u.mine.year,
            journal=u.mine.journal,
            volume=u.mine.volume,
            page=-100,
            title=u.mine.title,
        )
    assert str(e.value) == "couldn't find paper with an exact match to this info on ADS"


def test_get_paper_from_journal_nonsense_journal_is_checked():
    with pytest.raises(ValueError) as e:
        ads_call.get_bibcode_from_journal(
            year=u.mine.year,
            journal="nonsense",
            volume=u.mine.volume,
            page=u.mine.page,
            title=u.mine.title,
        )
    assert str(e.value) == "couldn't find paper with an exact match to this info on ADS"


def test_get_paper_from_journal_journal_without_bibstem_not_specific():
    # do a quick thing to remove ApJ from the dictionary, then we'll add it back
    apj = "The Astrophysical Journal"
    original_value = ads_call.bibstems[apj]
    del ads_call.bibstems[apj]
    with pytest.raises(ValueError) as e:
        ads_call.get_bibcode_from_journal(year=2000, journal=apj, authors="Brown")
    assert str(e.value) == "multiple papers found that match this info"
    ads_call.bibstems[apj] = original_value


def test_get_paper_from_journal_bad_attribute_raises_error():
    with pytest.raises(Exception):
        ads_call.get_bibcode_from_journal(
            year=u.mine.year,
            title="{}",
        )


# ======================================================================================
#
# Test getting various paper attributes from bibcodes
#
# ======================================================================================
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


# ======================================================================================
#
# Test accessing papers with various tricky differences
#
# ======================================================================================
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


def test_get_correct_page_when_no_page():
    results = ads_call.get_info(u.grasha_thesis.bibcode)
    assert results["page"] == u.grasha_thesis.page


def test_ensure_accents_on_letters():
    results = ads_call.get_info(u.juan.bibcode)
    assert results["authors"] == u.juan.authors
