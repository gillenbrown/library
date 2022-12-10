# Have a class to store the various attributes to test
# stolen from https://stackoverflow.com/a/23689767
class PaperDict(dict):
    """dot.notation access to dictionary attributes"""

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item):
        return self[item]


# Use my paper as the main testing paper.
mine = PaperDict(
    bibcode="2018ApJ...864...94B",
    bibcode_old="2018arXiv180409819B",
    ads_url="https://ui.adsabs.harvard.edu/abs/2018ApJ...864...94B/abstract",
    ads_url_old="https://ui.adsabs.harvard.edu/abs/2018arXiv180409819B",
    arxiv_id="1804.09819",
    arxiv_url=f"https://arxiv.org/abs/1804.09819",
    arxiv_url_v2=f"https://arxiv.org/abs/1804.09819v2",
    arxiv_pdf_url=f"https://arxiv.org/pdf/1804.09819.pdf",
    arxiv_pdf_url_v2=f"https://arxiv.org/pdf/1804.09819v2.pdf",
    title="Nuclear Star Clusters in Cosmological Simulations",
    authors=["Brown, Gillen", "Gnedin, Oleg Y.", "Li, Hui"],
    pubdate="2018-09-00",
    year=2018,
    journal="The Astrophysical Journal",
    volume=864,
    page=94,
    doi="10.3847/1538-4357/aad595",
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
    arxiv_url="https://arxiv.org/abs/astro-ph/0405537",
    arxiv_id="astro-ph/0405537",
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
    year=2020,
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
    url_old="https://ui.adsabs.harvard.edu/abs/2012arXiv1205.1508M/abstract",
    bibcode="2012A&A...543A...8M",
    bibcode_old="2012arXiv1205.1508M",
    page="A8",
)

grasha_thesis = PaperDict(
    url="https://ui.adsabs.harvard.edu/abs/2018PhDT........36G/abstract",
    bibcode="2018PhDT........36G",
    page=-1,
)

juan = PaperDict(
    url="https://ui.adsabs.harvard.edu/abs/2018ApJ...863...60R/abstract",
    bibcode="2018ApJ...863...60R",
    authors=["Remolina González, J. D.", "Sharon, K.", "Mahler, G."],
)

used_for_no_ads_key = PaperDict(
    # I need one paper that isn't used anywhere else in the tests other than when I'm
    # testing for a bad ADS key, so that my ADS wrapper doesn't store it in the cache
    url="https://ui.adsabs.harvard.edu/abs/2021AJ....161...40G/abstract"
)

# my most recent paper. Used for the updating test
mine_recent = PaperDict(
    bibcode="2022MNRAS.514..280B",
    title=(
        "Testing feedback from star clusters in simulations of the Milky Way formation"
    ),
    authors=["Brown, Gillen", "Gnedin, Oleg Y."],
    pubdate="2022-07-00",
    arxiv_id="2203.00559",
    journal="Monthly Notices of the Royal Astronomical Society",
    volume=514,
    page=280,
    abstract=(
        "We present a suite of galaxy formation simulations that directly model star "
        "cluster formation and disruption. Starting from a model previously developed "
        "by our group, here we introduce several improvements to the prescriptions "
        "for cluster formation and feedback, then test these updates using a large "
        "suite of cosmological simulations of Milky Way mass galaxies. We perform a "
        "differential analysis with the goal of understanding how each of the updates "
        "affects star cluster populations. Two key parameters are the momentum boost "
        "of supernova feedback f<SUB>boost</SUB> and star formation efficiency per "
        "free-fall time ϵ<SUB>ff</SUB>. We find that f<SUB>boost</SUB> has a strong "
        "influence on the galactic star formation rate, with higher values leading to "
        "less star formation. The efficiency ϵ<SUB>ff</SUB> does not have a "
        "significant impact on the global star formation rate, but dramatically "
        "changes cluster properties, with increasing ϵ<SUB>ff</SUB> leading to a "
        "higher maximum cluster mass, shorter age spread of stars within clusters, "
        "and higher integrated star formation efficiencies. We also explore the "
        "redshift evolution of the observable cluster mass function, finding that "
        "most massive clusters have formed at high redshift z &gt; 4. Extrapolation "
        "of cluster disruption to z = 0 produces good agreement with both the "
        "Galactic globular cluster mass function and age-metallicity relation. Our "
        "results emphasize the importance of using small-scale properties of galaxies "
        "to calibrate subgrid models of star cluster formation and feedback."
    ),
    bibtex=(
        "@ARTICLE{2022MNRAS.514..280B,\n"
        "       author = {{Brown}, Gillen and {Gnedin}, Oleg Y.},\n"
        '        title = "{Testing feedback from star clusters in simulations of the '
        'Milky Way formation}",\n'
        "      journal = {\\mnras},\n"
        "     keywords = {methods: numerical, galaxies: evolution, galaxies: formation, "
        "galaxies: star clusters: general, galaxies: star formation, Astrophysics - "
        "Astrophysics of Galaxies},\n"
        "         year = 2022,\n"
        "        month = jul,\n"
        "       volume = {514},\n"
        "       number = {1},\n"
        "        pages = {280-301},\n"
        "          doi = {10.1093/mnras/stac1164},\n"
        "archivePrefix = {arXiv},\n"
        "       eprint = {2203.00559},\n"
        " primaryClass = {astro-ph.GA},\n"
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/2022MNRAS.514..280B},\n"
        "      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n"
        "}\n"
        "\n"
    ),
)

mvdbw_book = PaperDict(
    bibcode="2010gfe..book.....M",
    bibtex=(
        "@BOOK{2010gfe..book.....M,\n"
        "       author = {{Mo}, Houjun and {van den Bosch}, Frank C. and {White}, Simon},\n"
        '        title = "{Galaxy Formation and Evolution}",\n'
        "         year = 2010,\n"
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/2010gfe..book.....M},\n"
        "      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n"
        "}\n"
        "\n"
        ""
    ),
)
larsen = PaperDict(
    doi="10.1051/aas:1999509",
    bibcode="1999A&AS..139..393L",
)

sellwood_binney = PaperDict(
    doi="10.1046/j.1365-8711.2002.05806.x",
    bibcode="2002MNRAS.336..785S",
)

behroozi = PaperDict(
    bibcode="2013ApJ...770...57B",
    bibtex=(
        "@ARTICLE{behroozi_etal13,\n"
        "   author = {{Behroozi}, P.~S. and {Wechsler}, R.~H. and {Conroy}, C.},\n"
        '    title = "{The Average Star Formation Histories of Galaxies in '
        'Dark Matter Halos from z = 0-8}",\n'
        "  journal = {\apj},\n"
        'archivePrefix = "arXiv",\n'
        "   eprint = {1207.6105},\n"
        ' primaryClass = "astro-ph.CO",\n'
        " keywords = {dark matter, galaxies: abundances, galaxies: evolution, "
        "methods: numerical },\n"
        "     year = 2013,\n"
        "    month = jun,\n"
        "   volume = 770,\n"
        "      eid = {57},\n"
        "    pages = {57},\n"
        "      doi = {10.1088/0004-637X/770/1/57},\n"
        "   adsurl = {http://adsabs.harvard.edu/abs/2013ApJ...770...57B}\n"
        "}"
    ),
)

kravtsov = PaperDict(
    bibcode="1999PhDT........25K",
    authors_bibtex="{Kravtsov}, Andrey V.",
    title="High-resolution simulations of structure formation in the universe",
    year=1999,
    bibtex=(
        "@PHDTHESIS{1999PhDT........25K,\n"
        "       author = {{Kravtsov}, Andrey V.},\n"
        '        title = "{High-resolution simulations of structure '
        'formation in the universe}",\n'
        "     keywords = {Physics: Astronomy and Astrophysics},\n"
        "       school = {New Mexico State University},\n"
        "         year = 1999,\n"
        "        month = jan,\n"
        "       adsurl = {https://ui.adsabs.harvard.edu/abs/1999PhDT........25K},\n"
        "      adsnote = {Provided by the SAO/NASA Astrophysics Data System}\n"
        "}"
    ),
)

williams = PaperDict(
    bibcode="2000prpl.conf...97W",
    authors_bibtex="{Williams}, J.~P. and {Blitz}, L. and {McKee}, C.~F.",
    title=(
        "The Structure and Evolution of Molecular Clouds: "
        "from Clumps to Cores to the IMF"
    ),
    journal="Protostars and Planets IV",
    year=2000,
    page=97,
    bibtex=(
        "@ARTICLE{williams_etal00,\n"
        "   author = {{Williams}, J.~P. and {Blitz}, L. and {McKee}, C.~F.},\n"
        '    title = "{The Structure and Evolution of Molecular Clouds: '
        'from Clumps to Cores to the IMF}",\n'
        "  journal = {Protostars and Planets IV},\n"
        "     year = 2000,\n"
        "    month = may,\n"
        "    pages = {97-120}\n"
        "}"
    ),
)

carney = PaperDict(
    bibcode="1996PASP..108..900C",
    title=(
        "The Constancy of [alpha/Fe] in Globular Clusters of Differing [Fe/H] and Age"
    ),
    year=1996,
)

meylan = PaperDict(
    bibcode="2001AJ....122..830M",
    title=(
        "Mayall II=G1 in M31: Giant Globular Cluster or Core of a "
        "Dwarf Elliptical Galaxy?"
    ),
    year=2001,
)
