# import ads.sandbox as ads
import ads

class Work(object):
    def __init__(self):
        return

def bibcode_to_ads_url(bibcode):
    return "https://ui.adsabs.harvard.edu/abs/{}/abstract".format(bibcode)

class Paper(Work):
    def __init__(self, url):
        if "ui.adsabs.harvard.edu/abs/" in url:
            self._handle_ads_url(url)
        if "arxiv.org" in url:
            self._handle_arxiv_url(url)

        super().__init__()

    @staticmethod
    def _get_bibtex_entry(bibcode):
        return ads.ExportQuery(bibcodes=bibcode).execute()

    def _handle_ads_url(self, url):
        self.ads_url = url
        # first get the bibcode from the URL. This is always the thing after
        # "abs" in the abstract
        split_url = url.split("/")
        bibcode_idx = split_url.index("abs") + 1
        bibcode = split_url[bibcode_idx]

        # the ADS package recommends using Export Query rather than the other
        # ways of getting the bibtex entry
        self.bibtex_entry = self._get_bibtex_entry(bibcode)

    def _handle_arxiv_url(self, url):
        # first get the identifier from the url
        arxiv_identifier = url.split("/")[-1]
        # if they give a pdf link ignore the pdf
        arxiv_identifier = arxiv_identifier.replace(".pdf", "")

        # use this to get the bibcode
        query = ads.SearchQuery(q="arXiv:{}".format(arxiv_identifier),
                                fl=["bibcode"])
        bibcode = list(query)[0].bibcode

        self.bibtex_entry = self._get_bibtex_entry(bibcode)
        self.ads_url = bibcode_to_ads_url(bibcode)
