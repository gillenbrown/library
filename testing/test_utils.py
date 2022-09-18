# Have a class to store the various attributes to test
# stolen from https://stackoverflow.com/a/23689767
class PaperDict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Use my paper as the main testing paper.
mine = PaperDict(
    bibcode="2018ApJ...864...94B",
    ads_url="https://ui.adsabs.harvard.edu/abs/2018ApJ...864...94B/abstract",
    arxiv_id="1804.09819",
    arxiv_url=f"https://arxiv.org/abs/1804.09819",
    arxiv_url_v2=f"https://arxiv.org/abs/1804.09819v2",
    arxiv_pdf_url=f"https://arxiv.org/pdf/1804.09819.pdf",
    arxiv_pdf_url_v2=f"https://arxiv.org/pdf/1804.09819v2.pdf",
    title="Nuclear Star Clusters in Cosmological Simulations",
    authors=["Brown, Gillen", "Gnedin, Oleg Y.", "Li, Hui"],
    pubdate="2018-09-00",
    journal="The Astrophysical Journal",
    volume=864,
    page=94,
    abstract=(
        "We investigate the possible connection between the most massive globular "
        "clusters, such as ω Cen and M54, and nuclear star clusters (NSCs) of "
        "dwarf galaxies that exhibit similar spreads in age and metallicity. "
        "We examine galactic nuclei in cosmological galaxy formation simulations"
        " at z ≈ 1.5 to explore whether their age and metallicity spreads could "
        "explain these massive globular clusters. We derive structural properties "
        "of these nuclear regions, including mass, size, rotation, and shape. By "
        "using theoretical supernova yields to model the supernova enrichment in "
        "the simulations, we obtain individual elemental abundances for "
        "Fe, O, Na, Mg, and Al. Our nuclei are systematically more metal-rich "
        "than their host galaxies, which lie on the expected mass-metallicity "
        "relation. Some nuclei have a spread in Fe and age comparable to the "
        "massive globular clusters of the Milky Way, lending support to the "
        "hypothesis that NSCs of dwarf galaxies could be the progenitors of "
        "these objects. None of our nuclear regions contain the light element "
        "abundance spreads that characterize globular clusters, even when a "
        "large age spread is present. Our results demonstrate that extended "
        "star formation history within clusters, with metal pollution provided "
        "solely by supernova ejecta, is capable of replicating the metallicity "
        "spreads of massive globular clusters, but still requires another "
        "polluter to produce the light element variations."
    ),
    bibtex=(
        "@ARTICLE{2018ApJ...864...94B,\n"
        "       author = {{Brown}, Gillen and {Gnedin}, Oleg Y. and {Li}, Hui},\n"
        '        title = "{Nuclear Star Clusters in Cosmological Simulations}",\n'
        "      journal = {\\apj},\n"
        "     keywords = {galaxies: formation, galaxies: nuclei, galaxies: "
        "star clusters: general, globular clusters: general, Astrophysics - "
        "Astrophysics of Galaxies, Astrophysics - Solar and Stellar Astrophysics},\n"
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
    ),
)

# Also use Tremonti et al. 2004 as a test paper
tremonti = PaperDict(
    bibcode="2004ApJ...613..898T",
    title=(
        "The Origin of the Mass-Metallicity Relation: Insights from 53,000 "
        "Star-forming Galaxies in the Sloan Digital Sky Survey"
    ),
    authors=[
        "Tremonti, Christy A.",
        "Heckman, Timothy M.",
        "Kauffmann, Guinevere",
        "Brinchmann, Jarle",
        "Charlot, Stéphane",
        "White, Simon D. M.",
        "Seibert, Mark",
        "Peng, Eric W.",
        "Schlegel, David J.",
        "Uomoto, Alan",
        "Fukugita, Masataka",
        "Brinkmann, Jon",
    ],
    pubdate="2004-10-00",
    journal="The Astrophysical Journal",
    volume=613,
    page=898,
    abstract=(
        "We utilize Sloan Digital Sky Survey imaging and spectroscopy of ~53,000 "
        "star-forming galaxies at z~0.1 to study the relation between stellar mass and "
        "gas-phase metallicity. We derive gas-phase oxygen abundances and stellar "
        "masses using new techniques that make use of the latest stellar evolutionary "
        "synthesis and photoionization models. We find a tight (+/-0.1 dex) "
        "correlation between stellar mass and metallicity spanning over 3 orders of "
        "magnitude in stellar mass and a factor of 10 in metallicity. The relation is "
        "relatively steep from 10<SUP>8.5</SUP> to 10<SUP>10.5</SUP> M<SUB>solar</SUB> "
        "h<SUP>-2</SUP><SUB>70</SUB>, in good accord with known trends between "
        "luminosity and metallicity, but flattens above 10<SUP>10.5</SUP> "
        "M<SUB>solar</SUB>. We use indirect estimates of the gas mass based on the "
        "Hα luminosity to compare our data to predictions from simple closed box "
        "chemical evolution models. We show that metal loss is strongly "
        "anticorrelated with baryonic mass, with low-mass dwarf galaxies being 5 "
        "times more metal depleted than L<SUP>*</SUP> galaxies at z~0.1. Evidence for "
        "metal depletion is not confined to dwarf galaxies but is found in galaxies "
        "with masses as high as 10<SUP>10</SUP> M<SUB>solar</SUB>. We interpret this "
        "as strong evidence of both the ubiquity of galactic winds and their "
        "effectiveness in removing metals from galaxy potential wells."
    ),
    bibtex=(
        "@ARTICLE{2004ApJ...613..898T,\n"
        "       author = {{Tremonti}, Christy A. and {Heckman}, Timothy M. and "
        "{Kauffmann}, Guinevere and {Brinchmann}, Jarle and {Charlot}, St{\\'e}phane "
        "and {White}, Simon D.~M. and {Seibert}, Mark and {Peng}, Eric W. and "
        "{Schlegel}, David J. and {Uomoto}, Alan and {Fukugita}, Masataka and "
        "{Brinkmann}, Jon},\n"
        '        title = "{The Origin of the Mass-Metallicity Relation: Insights from '
        '53,000 Star-forming Galaxies in the Sloan Digital Sky Survey}",\n'
        "      journal = {\\apj},\n"
        "     keywords = {Galaxies: Abundances, Galaxies: Evolution, Galaxies: "
        "Fundamental Parameters, Galaxies: Statistics, Astrophysics},\n"
        "         year = 2004,\n"
        "        month = oct,\n"
        "       volume = {613},\n"
        "       number = {2},\n"
        "        pages = {898-913},\n"
        "          doi = {10.1086/423264},\n"
        "archivePrefix = {arXiv},\n"
        "       eprint = {astro-ph/0405537},\n"
        " primaryClass = {astro-ph},\n"
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/2004ApJ...613..898T},\n"
        "      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n"
        "}\n\n"
    ),
)

# John Forbes has a paper that's on the arXiv only, with no journal
forbes = PaperDict(
    url="https://ui.adsabs.harvard.edu/abs/2020arXiv200314327F/abstract",
    bibcode="2020arXiv200314327F",
    arxiv_id="2003.14327",
    title=(
        "A PDF PSA, or Never gonna set_xscale again -- guilty feats with logarithms"
    ),
    bibtex=(
        "@ARTICLE{2020arXiv200314327F,\n"
        "       author = {{Forbes}, John C.},\n"
        '        title = "{A PDF PSA, or Never gonna set\\_xscale again -- guilty '
        'feats with logarithms}",\n'
        "      journal = {arXiv e-prints},\n"
        "     keywords = {Astrophysics - Cosmology and Nongalactic Astrophysics, "
        "Astrophysics - Instrumentation and Methods for Astrophysics},\n"
        "         year = 2020,\n"
        "        month = mar,\n"
        "          eid = {arXiv:2003.14327},\n"
        "        pages = {arXiv:2003.14327},\n"
        "archivePrefix = {arXiv},\n"
        "       eprint = {2003.14327},\n"
        " primaryClass = {astro-ph.CO},\n"
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/2020arXiv200314327F},\n"
        "      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n"
        "}\n\n"
    ),
    authors=["Forbes, John C."],
    pubdate="2020-03-00",
    abstract=(
        "In the course of doing astronomy, one often encounters plots of densities, "
        "for example probability densities, flux densities, and mass functions. "
        "Quite frequently the ordinate of these diagrams is plotted logarithmically to "
        "accommodate a large dynamic range. In this situation, I argue that it is "
        "critical to adjust the density appropriately, rather than simply setting "
        "the x-scale to `log' in your favorite plotting code. I will demonstrate "
        "the basic issue with a pedagogical example, then mention a few common plots "
        "where this may arise, and finally some possible exceptions to the rule."
    ),
    journal="arXiv e-prints",
    volume=-1,
    page=-1,
)

# BBFH was before the arXiv, so it has no arXiv info
bbfh = PaperDict(
    url="https://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B/abstract",
    bibcode="1957RvMP...29..547B",
    title="Synthesis of the Elements in Stars",
    bibtex=(
        "@ARTICLE{1957RvMP...29..547B,\n"
        "       author = {{Burbidge}, E. Margaret and {Burbidge}, G.~R. and {Fowler}, "
        "William A. and {Hoyle}, F.},\n"
        '        title = "{Synthesis of the Elements in Stars}",\n'
        "      journal = {Reviews of Modern Physics},\n"
        "         year = 1957,\n"
        "        month = jan,\n"
        "       volume = {29},\n"
        "       number = {4},\n"
        "        pages = {547-650},\n"
        "          doi = {10.1103/RevModPhys.29.547},\n"
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/1957RvMP...29..547B},\n"
        "      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n"
        "}\n\n"
    ),
    authors=[
        "Burbidge, E. Margaret",
        "Burbidge, G. R.",
        "Fowler, William A.",
        "Hoyle, F.",
    ],
    pubdate="1957-00-00",
    abstract="",
    journal="Reviews of Modern Physics",
    volume=29,
    page=547,
)

# Krumholz 2019 review is a test of Annual Reviews, which has an at symbol, which
# causes issues
krumholz = PaperDict(
    url="https://ui.adsabs.harvard.edu/abs/2019ARA%26A..57..227K/abstract",
    bibcode="2019ARA&A..57..227K",
)

# Marks Kroupa 2012 is one paper that has has a non-numeric page number
marks = PaperDict(
    url="https://ui.adsabs.harvard.edu/abs/2012A%26A...543A...8M/abstract",
    bibcode="2012A&A...543A...8M",
    page="A8",
)

grasha_thesis = PaperDict(
    url="https://ui.adsabs.harvard.edu/abs/2018PhDT........36G/abstract",
    bibcode="2018PhDT........36G",
    page=-1,
)
