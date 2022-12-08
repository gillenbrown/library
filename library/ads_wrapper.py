import re
from pathlib import Path

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
        self._bibcode_from_doi = dict()
        self.num_queries = 0  # track this for debugging/testing purposes

        # read in the file of bibcodes
        self.bibstems = dict()

    def _build_bibstems(self):
        resources_dir = Path(__file__).parent / "resources"
        with open(resources_dir / "ads_bibstems.txt", "r") as f:
            for line in f:
                if line.strip() == "" or line.startswith("#"):
                    continue
                # if we're here, we have an entry to parse
                # the first word is the bibstem, the rest is the journal name.
                split_line = line.split()
                bibstem = split_line[0]
                journal_name = " ".join(split_line[1:])
                self.bibstems[journal_name] = bibstem
        # then get the AAS macros
        with open(resources_dir / "aastex_macros.txt", "r") as f:
            for line in f:
                if line.strip() == "" or line.startswith("#"):
                    continue
                # if we're here, we have an entry to parse
                # the first word is the abbreviation, the rest is the journal name.
                # we have to match the journal name to the bibstem as given by ADS
                split_line = line.split()
                abbreviation = "\\" + split_line[0]  # need to add back backslash
                journal_name = " ".join(split_line[1:])
                self.bibstems[abbreviation] = self.bibstems[journal_name]

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
            # Some things, like PhD theses, have no page at all returned by ADS.
            # Also, the page might be an arXiv string, which means it's unpublished.
            if paper.page is None or "arXiv" in paper.page[0]:
                page = -1
            else:
                # some papers have integer pages, others have letters
                try:
                    page = int(paper.page[0])
                except ValueError:  # converting letters to an int
                    page = paper.page[0]
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

            # we do need to be careful about arXiv papers that are not yet on ADS. This
            # can be malformed arXiv IDs, but also today's set of papers that are not
            # yet on ADS
            try:
                query = ads.SearchQuery(q="arXiv:{}".format(arxiv_id), fl=["bibcode"])
                bibcode = list(query)[0].bibcode
            except IndexError:  # no papers found
                raise ValueError(f"arXiv ID {arxiv_id} not on ADS")

            # store it in the cache
            self._bibcode_from_arxiv_id[arxiv_id] = bibcode

            return bibcode

    def _get_bibcode_from_doi(self, doi):
        """
        Get the ADS bibcode of a paper based on the DOI.

        :param doi: DOIof the paper.
        :type doi: str
        :return: ADS bibcode of the paper.
        :rtype: str
        """
        # try to get it from the cache first
        try:
            return self._bibcode_from_doi[doi]
        except KeyError:
            self.num_queries += 1

            # we'll need to double check that the DOI exists
            try:
                query = ads.SearchQuery(q="doi:{}".format(doi), fl=["bibcode"])
                bibcode = list(query)[0].bibcode
            except IndexError:  # not found on ADS
                # get rid of quotes in error message
                doi = doi.replace('"', "")
                raise ValueError(f"DOI {doi} not on ADS")

            # store it in the cache
            self._bibcode_from_doi[doi] = bibcode

            return bibcode

    def _update_bibcode(self, bibcode):
        """
        Return the newest version of a given bibcode.

        This is needed because the initial bibcode of a paper uses the arXiv ID, but
        the bibcode is updated once paper details become available. If the bibcode
        contains an arXiv ID, we'll see if we can update it. If it already has journal
        information, we just return the unmodified bibcode

        :param bibcode: The bibcode to potentially update
        :type bibcode: str
        :return: an updated bibcode
        :rtype: str
        """
        # don't update ones that already have journal info
        if "arxiv" not in bibcode.lower():
            return bibcode
        # parse the bibcode to get the arXiv ID and then call ADS to see what it is.
        # For now I'll assume that these use the post 2007 arXiv system (see here:
        # https://arxiv.org/help/arxiv_identifier). But there was a change in length
        # in 2014, so I need to be a bit careful.
        # bibcodes are formatted like "2018arXiv180409819B", where the arXiv ID there
        # would be "1804.09819", so we can just grab from the appropriate indices.
        # I currently haven't tested this for pre-2007 arXiv IDs, since I can't find
        # anything about how those are formatted into ADS bibcodes
        arxiv_id = bibcode[-10:-1]
        if "." in arxiv_id:  # pre-2014, 4 characters on each side. No fix needed
            return self._get_bibcode_from_arxiv(arxiv_id)
        else:  # Uses the post-2014 5 digit ending, I need to add the "."
            arxiv_id = arxiv_id[:4] + "." + arxiv_id[4:]
            return self._get_bibcode_from_arxiv(arxiv_id)

    def get_bibcode(self, identifier):
        """
        Get the bibcode of a paper based on one of many ways to access a paper.

        The following things are recognized:
        - ADS bibcode
        - ADS URL that links to the paper
        - arXiv URL that links to the paper (either the abstract page or the pdf)
        - arXiv ID
        - DOI

        :param identifier: One of the following methods above for identifying a paper.
        :type identifier: str
        :return: The ADS bibcode of the paper referenced.
        :rtype: str
        """
        # Set up a few regular expressions to identify both arXiv IDs and things with
        # the year at the front, which is used when checking for bibcodes directly
        # https://arxiv.org/help/arxiv_identifier
        arxiv_id_re = re.compile(r"[0-9]{4}\.[0-9]{4,5}")
        arxiv_id_old_re = re.compile(r"[a-z.-]*/[0-9]{7}$")
        # http://adsabs.github.io/help/actions/bibcode
        year_at_front = re.compile(r"^[0-9]{4}")

        # When we get the bibcode, we may need to update it. If we get the bibcode by
        # querying ADS (either for the arXiv ID or DOI), it will return the updated
        # bibcode. However, if we do so by parsing the identifier, we'll call the
        # function to see if this bibcode is outdated.

        # check if it looks like an ADS URL. This is the easiest and most reliable case
        if "adsabs.harvard.edu/abs/" in identifier:
            # first get the bibcode from the URL. This is always the thing after "abs"
            # in the abstract
            split_url = identifier.split("/")
            bibcode_idx = split_url.index("abs") + 1
            bibcode = split_url[bibcode_idx]
            # sometimes there's the placeholder for the and sign in the URL
            bibcode = bibcode.replace("%26", "&")
            # make sure it's the appropriate length for a bibcode
            if len(bibcode) != 19:
                raise ValueError(f"Identifier {identifier} not recognized")
            return self._update_bibcode(bibcode)
        # see if it looks like a DOI.
        # We check DOI next since it's a simple check, and sometimes DOIs can have
        # segments that look like an arXiv ID, fooling my simple regex
        elif identifier.startswith("10.") and "/" in identifier:
            # include doi within quotes to not mess up special characters in query
            return self._get_bibcode_from_doi(f'"{identifier}"')
        # see if it's obviously an arXiv ID
        elif identifier.lower().startswith("arxiv:"):
            return self._get_bibcode_from_arxiv(identifier.split(":")[1])
        # next check if it looks like a plain bibcode
        # # http://adsabs.github.io/help/actions/bibcode
        # re.match only looks at the beginning of the string, where the year will be
        elif len(identifier) == 19 and re.match(year_at_front, identifier):
            return self._update_bibcode(identifier)  # they passed in the bibcode
        # see if it has a new-style arXiv ID
        # re.search looks anywhere in the string, so we check this only after we have
        # tried other methods that may be more clear
        elif re.search(arxiv_id_re, identifier) is not None:
            # get the part of the string that is the arXiv ID
            arxiv_id = re.search(arxiv_id_re, identifier).group()
            # then run the query
            return self._get_bibcode_from_arxiv(arxiv_id)
        # see if it looks like an old style arXiv id
        elif re.search(arxiv_id_old_re, identifier) is not None:
            # get the part of the string that is the arXiv ID
            arxiv_id = re.search(arxiv_id_old_re, identifier).group()
            # then run the query
            return self._get_bibcode_from_arxiv(arxiv_id)
        # otherwise we don't know what to do
        else:
            raise ValueError(f"Identifier {identifier} not recognized")

    def get_bibcode_from_journal(self, **kwargs):
        """
        Get the paper details from the full journal info


        :return:
        """
        # see if we need to build the bibstems
        if len(self.bibstems) == 0:
            self._build_bibstems()

        # sometimes both page and pages can be used. I'll use page as my default
        if "pages" in kwargs:
            kwargs["page"] = kwargs["pages"]

        # then create the query. We'll use the information that's available
        query = ""
        for attribute in ["year", "title", "volume", "page"]:
            if attribute in kwargs:
                query += f'{attribute}:"{kwargs[attribute]}" '
        # handle bibstem separately
        if "journal" in kwargs:
            # then use those to get the bibstem of this journal
            try:
                bibstem = self.bibstems[kwargs["journal"]]
                query += f'bibstem:"{bibstem}" '
            except KeyError:
                raise ValueError("could not match journal to an ADS bibstem")
        # authors are a bit trickier, those need to be parsed separately
        # We'll assume the author list is in BibTeX format. The list of authors is
        # separated with "and"
        if "authors" in kwargs:
            authors_list = kwargs["authors"].split("and")
            for idx, a in enumerate(authors_list):
                a = a.strip().replace("{", "").replace("}", "")
                last_name = a.split(",")[0]

                # Then add to the query. Treat the first author differently.
                if idx == 0:
                    query += f'author:"^{last_name}" '
                else:
                    query += f'author:"{last_name}" '

        # make sure there is something to query
        if query == "":
            raise ValueError(
                "not enough publication details to uniquely identify paper"
            )

        # then we can do this query. Since we included all the available information
        # in the query, there's no extra checking we need to do on the results.
        query_results = list(ads.SearchQuery(q=query, fl=["bibcode"]))

        # then see what kind of results we got
        if len(query_results) == 0:
            raise ValueError(
                "couldn't find paper with an exact match to this info on ADS"
            )
        elif len(query_results) == 1:
            return query_results[0].bibcode
        else:
            raise ValueError("multiple papers found that match this info")
