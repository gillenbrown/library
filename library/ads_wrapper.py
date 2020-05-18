import re
import datetime

import ads


class ADSWrapper(object):
    """
    Class representing a scholarly paper accessible through ADS.
    """

    def __init__(self):
        # Since I am getting this info by querying the API, and there's a cap on the
        # number of queries per day, I want to cache things if possible. The two things
        # I get are the bibtext entries, obtained using the ADS bibcode, and the
        # bibcode, obtained from the arxiv ID. I'll store those as class level
        # dictionaries so all instances can access them. This is mostly useful for
        # tests, when we'll access the same paper a lot
        self._info_from_bibcode = dict()
        self._bibcode_from_arxiv_id = dict()
        self.num_queries = 0  # track this for debugging/testing purposes

    def get_info(self, bibcode):
        try:
            return self._info_from_bibcode[bibcode]
        except KeyError:
            self.num_queries += 1
            # To reduce the number of queries we need to request everything ahead of
            # time with the `fl` parameter. Even though we already have the bibcode we
            # need to return this, as the bibtex entry won't be fetched ahead of time
            # for some reason
            quantities = [
                "abstract",
                "bibcode",
                "title",
                "author",
                "pubdate",
                "pub",
                "volume",
                "page",
            ]
            paper = list(ads.SearchQuery(bibcode=bibcode, fl=quantities))[0]
            # Recommended to do the bibtex separately, according to the ADS library
            bibtex = ads.ExportQuery(bibcodes=bibcode).execute()
            # We then need to parse the info a bit, as some things are in lists for
            # whatever reason
            results = {
                "abstract": paper.abstract,
                "bibtex": bibtex,
                "bibcode": bibcode,
                "title": paper.title[0],  # in a list for some reason
                "authors": paper.author,  # author actually has all authors
                "pubdate": paper.pubdate,
                "journal": paper.pub,
                "volume": int(paper.volume),
                "page": int(paper.page[0]),
            }

            # store this in the cache
            self._info_from_bibcode[bibcode] = results

            return results

    def _get_bibcode_from_arxiv(self, arxiv_id):
        # try to get it from the cache first
        try:
            return self._bibcode_from_arxiv_id[arxiv_id]
        except KeyError:
            self.num_queries += 1
            query = ads.SearchQuery(q="arXiv:{}".format(arxiv_id), fl=["bibcode"])
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
            # first get the bibcode from the URL. This is always the thing after "abs"
            # in the abstract
            split_url = identifier.split("/")
            bibcode_idx = split_url.index("abs") + 1
            return split_url[bibcode_idx]
        # next check if it looks like a plain bibcode
        # # http://adsabs.github.io/help/actions/bibcode
        # re.match only looks at the beginning of the string, where the year will be
        elif len(identifier) == 19 and re.match(year_at_front, identifier):
            return identifier
        else:
            raise ValueError("Identifier not recognized")
