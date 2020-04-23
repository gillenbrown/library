# import ads.sandbox as ads
import ads

class Work(object):
    def __init__(self):
        return


class Paper(Work):
    """
    Class representing a scholarly paper accessible through ADS.
    """

    # Since I am getting this info by querying the API, and there's a cap on
    # the number of queries per day, I want to cache things if possible.
    # The two things I get are the bibtext entries, obtained using the ADS
    # bibcode, and the bibcode, obtained from the arxiv ID. I'll store those
    # as class level dictionaries so all instances can access them. This is
    # mostly useful for tests, when we'll access the same paper a lot
    _bibtexs_from_bibcode = dict()
    _bibcode_from_arxiv_id = dict()
    num_queries = 0  # track this for debugging/testing purposes

    @classmethod
    def _get_bibtex_entry(cls, bibcode):
        try:
            return cls._bibtexs_from_bibcode[bibcode]
        except KeyError:
            cls.num_queries += 1
            # the ADS package recommends using Export Query rather than the
            # other ways of getting the bibtex entry
            bibtex = ads.ExportQuery(bibcodes=bibcode).execute()
            cls._bibtexs_from_bibcode[bibcode] = bibtex
            return bibtex

    @classmethod
    def _get_bibcode_from_arxiv_id(cls, arxiv_id):
        try:
            return cls._bibcode_from_arxiv_id[arxiv_id]
        except KeyError:
            cls.num_queries += 1
            query = ads.SearchQuery(q="arXiv:{}".format(arxiv_id),
                                    fl=["bibcode"])
            bibcode = list(query)[0].bibcode
            cls._bibcode_from_arxiv_id[arxiv_id] = bibcode
            return bibcode

    @staticmethod
    def _bibcode_to_ads_url(bibcode):
        return "https://ui.adsabs.harvard.edu/abs/{}/abstract".format(bibcode)

    def __init__(self, url):
        if "ui.adsabs.harvard.edu/abs/" in url:
            self._handle_ads_url(url)
        if "arxiv.org" in url:
            self._handle_arxiv_url(url)

        super().__init__()

    def _handle_ads_url(self, url):
        self.ads_url = url
        # first get the bibcode from the URL. This is always the thing after
        # "abs" in the abstract
        split_url = url.split("/")
        bibcode_idx = split_url.index("abs") + 1
        bibcode = split_url[bibcode_idx]

        self.bibtex_entry = self._get_bibtex_entry(bibcode)

    def _handle_arxiv_url(self, url):
        # first get the identifier from the url
        arxiv_identifier = url.split("/")[-1]
        # if they give a pdf link ignore the pdf
        arxiv_identifier = arxiv_identifier.replace(".pdf", "")
        bibcode = self._get_bibcode_from_arxiv_id(arxiv_identifier)

        self.bibtex_entry = self._get_bibtex_entry(bibcode)
        self.ads_url = self._bibcode_to_ads_url(bibcode)
