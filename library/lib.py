from library import ads_wrapper
from library import database

ads_call = ads_wrapper.ADSWrapper()


class Library(object):
    def __init__(self, storage_location):
        self.storage_location = storage_location
        self.database = database.Database(storage_location)

    def add_paper(self, identifier):
        """

        :param identifier: This can be one of many things that can be used to identify
                           a paper. Most are URLs that link to a paper, (ADS and
                           arXiv), but also the arXiv ID and ADS bibcode.
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
        return self.database.get_paper_attribute(bibcode, attribute)

    def get_all_bibcodes(self):
        return self.database.get_all_bibcodes()


# follow this to generate API key https://ads.readthedocs.io/en/latest/
