import sqlite3
import contextlib


class Database(object):
    """
    Class that handles the database access
    """

    # When we store the authors, we can't store a list object. So we need to parse it a
    # bit to make it a string. We'll join the list of authors with this separator
    _author_sep = "&&&&"

    # store the columns that will be in the database.
    colnames = [
        "bibcode",
        "title",
        "authors",
        "pubdate",
        "journal",
        "volume",
        "page",
        "abstract",
        "bibtex",
    ]

    def __init__(self, db_file):
        """
        Set up the database at the location specified.

        :param db_file: Location to build the database file at.
        :type db_file: str
        """
        self.db_file = db_file

        # Create the papers table, adding the paper attributes
        self._execute(
            "CREATE TABLE IF NOT EXISTS papers"
            "("
            "bibcode text PRIMARY KEY,"
            "title text,"
            "authors text,"
            "pubdate text,"
            "journal text,"
            "volume integer,"
            "page integer,"
            "abstract text,"
            "bibtex text"
            ")"
        )

    def _execute(self, sql, parameters=()):
        """
        Execute a given command to the database.

        :param sql: The SQL command, with question marks in any values, to be replaced
                    by the values in the parameters tuple.
        :type sql: str
        :param parameters: Tuple containing values to replace the ? in the sql. Should
                           be the same length as the number of ?.
        :type parameters: tuple
        :return: List of rows returned by the query, if applicable.
        :rtype: list
        """
        # use with statements to auto-close
        with contextlib.closing(sqlite3.connect(self.db_file)) as conn:
            # using this factory makes the returned quantities easier to use
            conn.row_factory = sqlite3.Row
            with conn:  # auto commits changes to the database
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(sql, parameters)
                    return cursor.fetchall()

    def add_paper(
        self, bibcode, title, authors, pubdate, journal, volume, page, abstract, bibtex
    ):
        """
        Add a paper to the database. All parameters must be passed in.

        :param bibcode: The paper bibcode.
        :type bibcode: str
        :param title: The title of the paper.
        :type title: str
        :param authors: The list of authors of the paper.
        :type authors: list
        :param pubdate: Publication date of the paper.
        :type pubdate: str
        :param journal: Journal the paper was published in.
        :type journal: str
        :param volume: Volume of the journal the paper was published in.
        :type volume: int
        :param page: Page that paper was published on.
        :type page: int
        :param abstract: The full abstract of the paper.
        :type abstract: str
        :param bibtex: The full bibtex entry of the paper.
        :type bibtex: str
        :return: None
        """
        # handle the authors - this should be passed in as a list, but we can't store it
        # as a list. Just join it all together with the unique value held above.
        authors_write = self._author_sep.join(authors)
        try:
            # the formatting of this is kinda ugly
            # put these into the comma separated column names
            joined_colnames = ",".join(self.colnames)
            # also make the appropriate amount of question marks based on the number of
            # column names. This is needed for safe parameter entry
            question_marks = ",".join(["?"] * len(self.colnames))
            # combine this together into the SQL query
            sql = f"INSERT INTO papers({joined_colnames}) VALUES({question_marks})"
            # then put the values as a tuple before passing it in, for formatting nicely
            parameters = (
                bibcode,
                title,
                authors_write,
                pubdate,
                journal,
                volume,
                page,
                abstract,
                bibtex,
            )
            # then run this SQL
            self._execute(sql, parameters)
        except sqlite3.IntegrityError:
            print("Already in Library.")

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
        # check that the attribute is in the columns
        if not attribute in self.colnames:
            raise ValueError("This attribute is not in the table")

        # get the rows from the table where the bibtex matches.
        rows = self._execute(
            f"SELECT {attribute} FROM papers WHERE bibcode=?", (bibcode,)
        )
        # if we didn't find anything, tell the user
        if len(rows) == 0:
            raise ValueError(f"Bibcode {bibcode} not found in library!")

        # We've already checked that there are no duplicates, so this should just be
        # one item, but we'll check
        assert len(rows) == 1
        # then get the value from this row
        r_value = rows[0][attribute]
        # we do have to do a check for the author list, since it's special. We'll need
        # to put it back as a list.
        if attribute != "authors":
            return r_value
        else:
            return r_value.split(self._author_sep)

    def num_papers(self):
        """
        Get the number of papers in the database.

        :return: The number of papers in the database.
        :rtype: int
        """
        return len(self.get_all_bibcodes())

    def get_all_bibcodes(self):
        """
        Get the bibcodes for all papers present in the library.

        :return: List of bibcodes for all papers in the library.
        :rtype: list
        """
        papers = self._execute("SELECT bibcode FROM papers")
        return [p["bibcode"] for p in papers]
