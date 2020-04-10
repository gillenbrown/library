import pytest

from library.work import Work, Paper

my_url = "https://ui.adsabs.harvard.edu/abs/2018ApJ...864...94B/abstract"
@pytest.fixture
def ads_paper():
    return Paper(my_url)

def test_get_bibtex_from_ads(ads_paper):
    assert ads_paper.bibtex_entry == (
        "@ARTICLE{2018ApJ...864...94B,\n"
        "       author = {{Brown}, Gillen and {Gnedin}, Oleg Y. and {Li}, Hui},\n"
        '        title = "{Nuclear Star Clusters in Cosmological Simulations}",\n'
        "      journal = {\\apj},\n"
        "     keywords = {galaxies: formation, galaxies: nuclei, galaxies: star clusters: general, globular clusters: general, Astrophysics - Astrophysics of Galaxies, Astrophysics - Solar and Stellar Astrophysics},\n"
        "         year = 2018,\n"
        "        month = sep,\n"
        "       volume = {864},\n"
        "       number = {1},\n"
        "          eid = {94},\n"
        "        pages = {94},\n"
        "          doi = {10.3847/1538-4357/aad595},\n"
        "archivePrefix = {arXiv},\n"
        "       eprint = {1804.09819},\n"
        " primaryClass = {astro-ph.GA},\n"
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/2018ApJ...864...94B},\n"
        "      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n"
        "}\n\n"
    )

def test_create_paper_from_arxiv(ads_paper):
    arxiv_paper = Paper("https://arxiv.org/abs/1804.09819")
    # same as above test, just with arxiv link
    assert arxiv_paper.bibtex_entry == ads_paper.bibtex_entry

def test_create_paper_from_arxiv_pdf(ads_paper):
    arxiv_paper = Paper("https://arxiv.org/pdf/1804.09819.pdf")
    # same as above test, just with arxiv link
    assert arxiv_paper.bibtex_entry == ads_paper.bibtex_entry