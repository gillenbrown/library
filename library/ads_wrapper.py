import re

import ads


class ADSWrapper(object):
    """
    Class used to query ADS for papers.
    """

    def __init__(self):
        """
        Initialize the ADSWrapper object, no parameters required.
        """
        # Since I am getting info by querying the API, and there's a cap on the
        # number of queries per day, I want to cache things if possible. I used the
        # arXiv ID to get the bibcode, and then the bibcode to get various items about
        # that paper. I'll store those things as class level dictionaries so any
        # instances can access them. These caches are mostly useful for tests, where
        # we access the same paper many times.
        self._info_from_bibcode = dict()
        self._bibcode_from_arxiv_id = dict()
        self.num_queries = 0  # track this for debugging/testing purposes

    def get_info(self, bibcode):
        """
        Get many attributes of a paper identified by a bibcode.

        This returns the following attributes of the paper, most of which are
        self-explanatory:
        - "abstract"
        - "bibtex": The full bibtex entry for this paper from ADS.
        - "bibcode": The ADS bibcode of the paper (what was passed in)
        - "title"
        - "authors": List of authors of the paper, in the format "LastName, FirstName"
        - "pubdate": Publication date, in the format "YYYY/MM/DD" Day might be zero.
        - "journal"
        - "volume"
        - "page"

        :param bibcode: The bibcode of the paper.
        :type bibcode: str
        :return: Dictionary containing the attributes listed above.
        :rtype: dict
        """
        try:  # try to get it from the cache
            return self._info_from_bibcode[bibcode]
        except KeyError:  # not found, need to do an actual query
            self.num_queries += 1
            # To reduce the number of queries we need to request everything ahead of
            # time with the `fl` parameter.
            quantities = [
                "abstract",
                "title",
                "author",
                "pubdate",
                "pub",
                "volume",
                "page",
                "identifier",
            ]
            paper = list(ads.SearchQuery(bibcode=bibcode, fl=quantities))[0]
            # Recommended to do the bibtex separately, according to the ADS library
            bibtex = ads.ExportQuery(bibcodes=bibcode).execute()
            # parse the list of identifiers to get the arXiv id. The default value is
            # a message that the paper is not on the arXiv
            arxiv_id = "Not on the arXiv"
            for identifier in paper.identifier:
                if identifier.startswith("arXiv:"):
                    arxiv_id = identifier.split(":")[-1]
            # parse the volume and page data, which are not present if the paper is
            # not actually published
            if paper.volume is None:
                volume = -1
            else:
                volume = int(paper.volume)
            # page might be an arXiv string, which means it's unpublished
            if "arXiv" in paper.page[0]:
                page = -1
            else:
                page = int(paper.page[0])
            # some papers don't have an abstract (B2FH for example)
            abstract = paper.abstract
            if abstract is None:
                abstract = ""
            # We can then put these into a dictionary to return
            results = {
                "abstract": abstract,
                "bibtex": bibtex,
                "bibcode": bibcode,
                "title": paper.title[0],  # in a list for some reason
                "authors": paper.author,  # author actually has all authors
                "pubdate": paper.pubdate,
                "journal": paper.pub,
                "volume": volume,
                "page": page,
                "arxiv_id": arxiv_id,
            }

            # store this in the cache
            self._info_from_bibcode[bibcode] = results

            return results

    def _get_bibcode_from_arxiv(self, arxiv_id):
        """
        Get the ADS bibcode of a paper based on the arXiv ID.

        :param arxiv_id: arXiv ID of the paper.
        :type arxiv_id: str
        :return: ADS bibcode of the paper.
        :rtype: str
        """
        # try to get it from the cache first
        try:
            return self._bibcode_from_arxiv_id[arxiv_id]
        except KeyError:
            self.num_queries += 1

            query = ads.SearchQuery(q="arXiv:{}".format(arxiv_id), fl=["bibcode"])
            bibcode = list(query)[0].bibcode

            # store it in the cache
            self._bibcode_from_arxiv_id[arxiv_id] = bibcode

            return bibcode

    def get_bibcode(self, identifier):
        """
        Get the bibcode of a paper based on one of many ways to access a paper.

        The following things are recognized:
        - ADS bibcode
        - ADS URL that links to the paper
        - arXiv URL that links to the paper (either the abstract page or the pdf)
        - arXiv ID

        :param identifier: One of the following methods above for identifying a paper.
        :type identifier: str
        :return: The ADS bibcode of the paper referenced.
        :rtype: str
        """
        # Set up a few regular expressions to identify both arXiv IDs and things with
        # the year at the front, which is used when checking for bibcodes directly
        # https://arxiv.org/help/arxiv_identifier
        arxiv_id_re = re.compile(r"[0-9]{4}\.[0-9]{4,5}")

        # http://adsabs.github.io/help/actions/bibcode
        year_at_front = re.compile(r"^[0-9]{4}")

        # see if it has an arXiv ID
        # re.search looks anywhere in the string
        if re.search(arxiv_id_re, identifier) is not None:
            # get the part of the string that is the arXiv ID
            arxiv_id = re.search(arxiv_id_re, identifier).group()
            # then run the query
            return self._get_bibcode_from_arxiv(arxiv_id)
        # check if it looks like an ADS URL
        elif "ui.adsabs.harvard.edu/abs/" in identifier:
            # first get the bibcode from the URL. This is always the thing after "abs"
            # in the abstract
            split_url = identifier.split("/")
            bibcode_idx = split_url.index("abs") + 1
            bibcode = split_url[bibcode_idx]
            # sometimes there's the placeholder for the and sign in the URL
            return bibcode.replace("%26", "&")
        # next check if it looks like a plain bibcode
        # # http://adsabs.github.io/help/actions/bibcode
        # re.match only looks at the beginning of the string, where the year will be
        elif len(identifier) == 19 and re.match(year_at_front, identifier):
            return identifier  # they passed in the bibcode
        # otherwise we don't know what to do
        else:
            raise ValueError(f"Identifier {identifier} not recognized")
