import work

class Library(object):
    def __init__(self):
        self.papers = []

    def add_paper(self, paper_url):
        self.papers.append(work.Paper(paper_url))


# follow this to generate API key https://ads.readthedocs.io/en/latest/