from library import ads_wrapper
from library import database

# set up the ADS wrapper object that will be used by the Library
ads_call = ads_wrapper.ADSWrapper()


class Library(object):
    """
    Class that holds all the data for the library.
    """

    def __init__(self, storage_location):
        """
        Initialize the library by setting up the database at the given location.

        :param storage_location: Path to the database where this library will be stored
        :type storage_location: str
        """
        self.storage_location = storage_location
        self.database = database.Database(storage_location)

    def add_paper(self, identifier):
        """
        Add a paper to the library based on one of many possible identifiers.

        The following things are recognized:
        - ADS bibcode
        - ADS URL that links to the paper
        - arXiv URL that links to the paper (either the abstract page or the pdf)
        - arXiv ID

        :param identifier: This can be one of many things that can be used to identify
                           a paper, listed above.
        :type identifier: str
        :return: None, but the paper is added to the database.
        :rtype: None
        """
        bibcode = ads_call.get_bibcode(identifier)
        paper_data = ads_call.get_info(bibcode)

        self.database.add_paper(
            bibcode,
            paper_data["title"],
            paper_data["authors"],
            paper_data["pubdate"],
            paper_data["journal"],
            paper_data["volume"],
            paper_data["page"],
            paper_data["abstract"],
            paper_data["bibtex"],
        )

    def get_paper_attribute(self, bibcode, attribute):
        """
        Get a given attribute about a given paper.

        :param bibcode: Bibcode of the desired paper.
        :type bibcode: str
        :param attribute: Desired attribute of the paper. Needs to be one that is in the
                          table.
        :type attribute: str
        :return: The value of the attribute of the requested paper.
        :rtype: list, str, or int
        """
        return self.database.get_paper_attribute(bibcode, attribute)

    def set_paper_attribute(self, bibcode, attribute, new_value):
        self.database.set_paper_attribute(bibcode, attribute, new_value)

    def get_all_bibcodes(self):
        """
        Get the bibcodes for all papers present in the library.

        :return: List of bibcodes for all papers in the library.
        :rtype: list
        """
        return self.database.get_all_bibcodes()


# follow this to generate API key https://ads.readthedocs.io/en/latest/
