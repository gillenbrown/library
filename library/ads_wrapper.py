import re

import ads

class ADSWrapper(object):
    """
    Class representing a scholarly paper accessible through ADS.
    """

    def __init__(self):
        # Since I am getting this info by querying the API, and there's a cap on
        # the number of queries per day, I want to cache things if possible.
        # The two things I get are the bibtext entries, obtained using the ADS
        # bibcode, and the bibcode, obtained from the arxiv ID. I'll store those
        # as class level dictionaries so all instances can access them. This is
        # mostly useful for tests, when we'll access the same paper a lot
        self._bibtexs_from_bibcode = dict()
        self._bibcode_from_arxiv_id = dict()
        self.num_queries = 0  # track this for debugging/testing purposes

    def get_bibtex(self, bibcode):
        try:
            return self._bibtexs_from_bibcode[bibcode]
        except KeyError:
            self.num_queries += 1
            # the ADS package recommends using Export Query rather than the
            # other ways of getting the bibtex entry
            bibtex = ads.ExportQuery(bibcodes=bibcode).execute()
            self._bibtexs_from_bibcode[bibcode] = bibtex
            return bibtex


    def _get_bibcode_from_arxiv(self, arxiv_id):
        #  remove any version info
        v_start = arxiv_id.find("v")  # returns -1 if not found
        if v_start > 0:
            arxiv_id = arxiv_id[:v_start]

        # try to get it from the cache first
        try:
            return self._bibcode_from_arxiv_id[arxiv_id]
        except KeyError:
            self.num_queries += 1
            query = ads.SearchQuery(q="arXiv:{}".format(arxiv_id),
                                            fl=["bibcode"])
            bibcode = list(query)[0].bibcode
            self._bibcode_from_arxiv_id[arxiv_id] = bibcode
            return bibcode

    def get_bibcode(self, identifier):
        # https://arxiv.org/help/arxiv_identifier
        arxiv_id_re = re.compile(r"[0-9]{4}\.[0-9]{4,5}")

        # http://adsabs.github.io/help/actions/bibcode
        year_at_front = re.compile(r"^[0-9]{4}")

        # re.search looks anywhere in the string
        if re.search(arxiv_id_re, identifier) is not None:
            arxiv_id = re.search(arxiv_id_re, identifier).group()
            return self._get_bibcode_from_arxiv(arxiv_id)
        elif "ui.adsabs.harvard.edu/abs/" in identifier:
            # first get the bibcode from the URL. This is always the thing after
            # "abs" in the abstract
            split_url = identifier.split("/")
            bibcode_idx = split_url.index("abs") + 1
            return split_url[bibcode_idx]
        # next check if it looks like a plain bibcode
        # # http://adsabs.github.io/help/actions/bibcode
        # re.match only looks at the beginning of the string, where the year
        # will be
        elif len(identifier) == 19 and re.match(year_at_front, identifier):
            return identifier
        else:
            raise ValueError("Identifier not recognized")
