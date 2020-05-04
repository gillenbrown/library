# import ads.sandbox as ads
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

    def _get_bibtex_entry(self, bibcode):
        try:
            return self._bibtexs_from_bibcode[bibcode]
        except KeyError:
            self.num_queries += 1
            # the ADS package recommends using Export Query rather than the
            # other ways of getting the bibtex entry
            bibtex = ads.ExportQuery(bibcodes=bibcode).execute()
            self._bibtexs_from_bibcode[bibcode] = bibtex
            return bibtex


    def _get_bibcode_from_arxiv_id(self, arxiv_id):
        try:
            return self._bibcode_from_arxiv_id[arxiv_id]
        except KeyError:
            self.num_queries += 1
            query = ads.SearchQuery(q="arXiv:{}".format(arxiv_id),
                                            fl=["bibcode"])
            bibcode = list(query)[0].bibcode
            self._bibcode_from_arxiv_id[arxiv_id] = bibcode
            return bibcode

    @staticmethod
    def _bibcode_to_ads_url(bibcode):
        return "https://ui.adsabs.harvard.edu/abs/{}/abstract".format(bibcode)

    def get_bibtex(self, url):
        if "ui.adsabs.harvard.edu/abs/" in url:
            # first get the bibcode from the URL. This is always the thing after
            # "abs" in the abstract
            split_url = url.split("/")
            bibcode_idx = split_url.index("abs") + 1
            bibcode = split_url[bibcode_idx]

        elif "arxiv.org" in url:
            # first get the identifier from the url
            arxiv_identifier = url.split("/")[-1]
            # if they give a pdf link ignore the pdf
            arxiv_identifier = arxiv_identifier.replace(".pdf", "")
            bibcode = self._get_bibcode_from_arxiv_id(arxiv_identifier)
        else:
            raise ValueError("URL not recognized")

        return self._get_bibtex_entry(bibcode)



