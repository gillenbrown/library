import sqlite3
import contextlib

class Database(object):
    def __init__(self, db_file):
        self.db_file = db_file

        self._execute("CREATE TABLE IF NOT EXISTS papers"
                      "("
                      "bibcode text PRIMARY KEY,"
                      "bibtex text"
                      ")")

    def _execute(self, sql, parameters=()):
        # use with statements to auto-close
        with contextlib.closing(sqlite3.connect(self.db_file)) as conn:
            # using this factory makes the returned quantities easier to use
            conn.row_factory = sqlite3.Row
            with conn:  # auto commits
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute(sql, parameters)
                    return cursor.fetchall()



    def add_paper(self, bibcode, bibtex):
        try:
            self._execute("INSERT INTO papers VALUES(?,?)", (bibcode, bibtex))
        except sqlite3.IntegrityError:
            print("Already in Library.")

    def get_paper(self, bibcode):
        rows = self._execute("SELECT * FROM papers WHERE bibcode=?", (bibcode,))
        # if we didn't find anything, tell the user
        if len(rows) == 0:
            raise ValueError(f"Bibcode {bibcode} not found in library!")

        # We've already checked that there are no duplicates, so this should
        # just be one item, but we'll check
        assert len(rows) == 1
        return rows[0]

    def num_papers(self):
        return  len(self._execute("SELECT * FROM papers"))