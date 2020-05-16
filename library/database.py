import sqlite3
import contextlib


class Database(object):
    # When we store the authors, we can't store a list object. So we need to parse it a
    # bit to make it a string. We'll join the list of authors with this separator
    author_sep = "&&&&"

    def __init__(self, db_file):
        self.db_file = db_file

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
        # use with statements to auto-close
        with contextlib.closing(sqlite3.connect(self.db_file)) as conn:
            # using this factory makes the returned quantities easier to use
            conn.row_factory = sqlite3.Row
            with conn:  # auto commits
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(sql, parameters)
                    return cursor.fetchall()

    def add_paper(
        self, bibcode, title, authors, pubdate, journal, volume, page, abstract, bibtex
    ):
        # this takes all the parameters that ADS has, plus it should automatically set
        # the default things for a paper (e.g. not read, no tags, etc.)
        # handle the authors - this should be passed in as a list, but we can't store it
        # as a list
        authors_write = self.author_sep.join(authors)
        try:
            self._execute(
                "INSERT INTO papers (bibcode,title,authors,pubdate,journal,volume,page,abstract,bibtex) "
                "VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    bibcode,
                    title,
                    authors_write,
                    pubdate,
                    journal,
                    volume,
                    page,
                    abstract,
                    bibtex,
                ),
            )
        except sqlite3.IntegrityError:
            print("Already in Library.")

    # def update_paper_details(self, bibcode, field_name, field_value):
    #     # This probably needs some more error checking, maybe checking that the columns exist?
    #     sql = f"UPDATE papers SET {field_name} = ? WHERE bibcode = ?"
    #     try:
    #         self._execute(sql, (field_value, bibcode))
    #     except sqlite3.OperationalError:
    #         raise ValueError("Column not found")

    def get_paper_attribute(self, bibcode, attribute):
        rows = self._execute(
            f"SELECT {attribute} FROM papers WHERE bibcode=?", (bibcode,)
        )
        # if we didn't find anything, tell the user
        if len(rows) == 0:
            raise ValueError(f"Bibcode {bibcode} not found in library!")

        # We've already checked that there are no duplicates, so this should just be
        # one item, but we'll check
        assert len(rows) == 1
        r_value = rows[0][attribute]
        # we do have to do a check for the author list, since it's special
        if attribute != "authors":
            return r_value
        else:
            return r_value.split(self.author_sep)

    def num_papers(self):
        return len(self.get_all_bibcodes())

    def get_all_bibcodes(self):
        papers = self._execute("SELECT bibcode FROM papers")
        return [p["bibcode"] for p in papers]
