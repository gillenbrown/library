from library import ads_wrapper
from library import database

class Library(object):
    def __init__(self, storage_location):
        self.storage_location = storage_location
        self.database = database.Database(storage_location)


# follow this to generate API key https://ads.readthedocs.io/en/latest/