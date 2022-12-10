import sqlite3
import time
import contextlib
from pathlib import Path

from library import ads_wrapper

# set up the ADS wrapper object that will be used by the Library
ads_call = ads_wrapper.ADSWrapper()


class PaperAlreadyInDatabaseError(Exception):
    """
    Custom exception that will be raised when a paper already is in the datbase.
    """

    pass


class Database(object):
    """
    Class that handles the database access
    """

    # When we store the authors, we can't store a list object. So we need to parse it a
    # bit to make it a string. We'll join the list of authors with this separator
    _author_sep = "&&&&"

    # store the columns that will be in the database.
    colnames_set_on_paper_add = [
        "bibcode",
        "title",
        "authors",
        "pubdate",
        "journal",
        "volume",
        "page",
        "abstract",
        "bibtex",
        "arxiv_id",
        "citation_keyword",  # the thing within the \cite{} command in LaTeX
        "update_time",  # then the paper was last updated
    ]
    # some columns won't be set when the paper is added, will be left NULL
    colnames_data = colnames_set_on_paper_add + ["local_file", "user_notes"]

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
            "page text,"
            "abstract text,"
            "bibtex text,"
            "arxiv_id text,"
            "local_file text,"
            "user_notes text,"
            "citation_keyword text UNIQUE,"
            "update_time real"
            ")"
        )

        # then update all papers, as necessary
        yesterday = time.time() - 24 * 60 * 60
        for bibcode in self.get_all_bibcodes():
            # don't simply check that the journal is set. Soemtimes there can be
            # intermediate updates to a paper, where the journal can be set but not
            # the full information. Once the page info is set, the paper will be
            # fully updated.
            # we also check that the paper has not been checked in the last 24 hours.
            # this is prevent unnecessary calls to ADS, and to let the interface
            # open faster when not checking for updates.
            if (
                self.get_paper_attribute(bibcode, "page") == -1
                and self.get_paper_attribute(bibcode, "update_time") <= yesterday
            ):
                self.update_paper(bibcode)

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

    def add_paper(self, identifier):
        """
        Add a paper to the database.

        The identifier will be parsed to get the bibcode, then the bibcode will be used
        to get all the paper details, which will then be stored. Some attributes are
        left null, such as location of the local file.

        The following things are recognized:
        - ADS bibcode
        - ADS URL that links to the paper
        - arXiv URL that links to the paper (either the abstract page or the pdf)
        - arXiv ID

        The bibcode is returned.

        :param identifier: This can be one of many things that can be used to identify
                           a paper, listed above.
        :type identifier: str
        :return: bibcode, so the user knows what was added
        :rtype: str
        :raises: PaperAlreadyInDatabaseError if paper is already in the library
        """
        # call ADS to get the details
        bibcode = ads_call.get_bibcode(identifier)
        # before we get all the info, see if the paper is already in the database. This
        # saves us from needing slow queries to ADS
        result = self._execute("SELECT 1 FROM papers WHERE bibcode = ?", [bibcode])
        # if this paper is already in the database, exit
        if len(result) > 0:
            raise PaperAlreadyInDatabaseError("Already in Library.")
        # otherwise, get the data and add the paper
        paper_data = ads_call.get_info(bibcode)

        # handle the authors - this should be passed in as a list, but we can't store it
        # as a list. Just join it all together with the unique value held above.
        authors_write = self._author_sep.join(paper_data["authors"])
        # the formatting of this is kinda ugly
        # put these into the comma separated column names
        joined_colnames = ",".join(self.colnames_set_on_paper_add)
        # also make the appropriate amount of question marks based on the number of
        # column names. This is needed for safe parameter entry
        question_marks = ",".join(["?"] * len(self.colnames_set_on_paper_add))
        # combine this together into the SQL query
        sql = f"INSERT INTO papers({joined_colnames}) VALUES({question_marks})"
        # then put the values as a tuple before passing it in, for formatting nicely
        parameters = (
            bibcode,
            paper_data["title"],
            authors_write,
            paper_data["pubdate"],
            paper_data["journal"],
            paper_data["volume"],
            paper_data["page"],
            paper_data["abstract"],
            paper_data["bibtex"],
            paper_data["arxiv_id"],
            bibcode,  # citation keyword
            time.time(),  # update time
        )
        # then run this SQL
        self._execute(sql, parameters)

        # Add the unread tag if it's in the database
        for t in self.get_all_tags():
            if t.lower() == "unread":
                self.tag_paper(bibcode, t)

        return bibcode

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
        if (attribute not in self.colnames_data) and (
            attribute not in self._get_all_tags_internal()
        ):
            raise ValueError("This attribute is not in the table")

        # get the rows from the table where the bibtex matches.
        rows = self._execute(
            f"SELECT `{attribute}` FROM papers WHERE bibcode=?", (bibcode,)
        )
        # if we didn't find anything, tell the user
        if len(rows) == 0:
            raise ValueError(f"Bibcode {bibcode} not found in library!")

        # We've already checked that there are no duplicates, so this should just be
        # one item, but we'll check
        assert len(rows) == 1
        # then get the value from this row
        r_value = rows[0][attribute]
        # we do have to do a check for a couple attributes, since they're special.
        # Authors list needs to be put back as a list
        if attribute == "authors":
            return r_value.split(self._author_sep)
        # page needs to be put back to an integer, if it is able
        elif attribute == "page":
            try:
                return int(r_value)
            except ValueError:  # strings cannot be converted
                return r_value
        # user the user's citaiton key when exporting the bibtex entry
        # we store it as the raw bibtex, then replace the value when processing
        elif attribute == "bibtex":
            # here we just need to replace the key at the beginning
            new_key = self.get_paper_attribute(bibcode, "citation_keyword")
            bibtex_rows = r_value.split("\n")
            # find the open brace that starts to specify the key
            brace_idx = bibtex_rows[0].find("{")
            bibtex_rows[0] = bibtex_rows[0][: brace_idx + 1] + new_key + ","
            return "\n".join(bibtex_rows)

        else:  # no modification needed
            return r_value

    def set_paper_attribute(self, bibcode, attribute, new_value):
        """
        Set a given attribute about a given paper.

        :param bibcode: Bibcode of the desired paper.
        :type bibcode: str
        :param attribute: Desired attribute of the paper. Needs to be one that is in the
                          table.
        :type attribute: str
        :param new_value: New value for the attribute of the paper. Should be the same
                          data type that column requires, which depends on the column.
        :return: None
        """
        # check that the attribute is in the columns
        if (attribute not in self.colnames_data) and (
            attribute not in self._get_all_tags_internal()
        ):
            raise ValueError("This attribute is not in the table")
        # and that the bibcode is in the library
        if not bibcode in self.get_all_bibcodes():
            raise ValueError("This paper is not in the table")

        # we do have to do a check for the author list, since it's special. We'll need
        # to put it back as a list.
        if attribute == "authors":
            new_value = self._author_sep.join(new_value)
        # we have to validate that spaces aren't in any citation keywords
        elif attribute == "citation_keyword":
            if " " in new_value:
                raise ValueError("Spaces not allowed in citation keywords.")
            elif len(new_value) == 0:
                raise ValueError("Empty string not allowed as citation keyword.")

        sql = f"UPDATE papers SET `{attribute}` = ? WHERE bibcode = ?"
        try:
            self._execute(sql, (new_value, bibcode))
        # two possible exceptions for bad data types
        except (sqlite3.InterfaceError, sqlite3.ProgrammingError):
            raise ValueError(f"Bad datatype for attribute {attribute}: {new_value}")
        except sqlite3.IntegrityError:  # this is raised for nonunique citation keywords
            assert attribute == "citation_keyword"
            raise RuntimeError(
                f"{attribute} needs to be unique. " f"{new_value} is already used. "
            )

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

    def get_cite_string(self, bibcode):
        """
        Get the short citation string for a given paper.

        This takes the form {authors}, {year}, {journal}, {volume}, {page}

        If there are 3 or fewer authors all are shown (just their last names), while
        if there are 4 or more the text reads {first author last name}, et al.

        :param bibcode: Bibcode to get the citation string for.
        :type bibcode: str
        :return: Cite string for this paper
        :rtype: str
        """
        authors = self.get_paper_attribute(bibcode, "authors")
        # get the author last names. The format of the names is firstname, lastname
        # so splitting by comma works
        authors_last_names = [a.split(",")[0] for a in authors]
        # if we have lot of authors, just show the first with et al.
        if len(authors_last_names) > 3:
            authors_str = f"{authors_last_names[0]} et al."
        else:  # three or less authors, show them all
            authors_str = ", ".join(authors_last_names)

        # the publication date has the year first, separated by dashes
        year = self.get_paper_attribute(bibcode, "pubdate").split("-")[0]

        # treat unpublished papers differently than published ones
        if self.get_paper_attribute(bibcode, "page") == -1:  # this is unpublished
            # Include the arXiv ID if it's there, otherwise don't include that at all
            arxiv_id = self.get_paper_attribute(bibcode, "arxiv_id")
            if arxiv_id == "Not on the arXiv":
                return f"{authors_str}, {year}"
            else:
                return f"{authors_str}, {year}, arXiv:{arxiv_id}"

        # implicit else clause here since we return inside the if loop. This handles
        # published papers
        # the journal may have an abbreviation
        journal = self.get_paper_attribute(bibcode, "journal")
        abbreviations = {
            "The Astrophysical Journal": "ApJ",
            "The Astrophysical Journal Supplement Series": "ApJS",
            "Monthly Notices of the Royal Astronomical Society": "MNRAS",
            "Astronomy and Astrophysics": "A&A",
            "Astronomy and Astrophysics Supplement Series": "A&AS",
            "The Astronomical Journal": "AJ",
            "Annual Review of Astronomy and Astrophysics": "ARA&A",
            "Publications of the Astronomical Society of the Pacific": "PASP",
            "Publications of the Astronomical Society of Japan": "PASJ",
        }
        if journal in abbreviations:
            journal = abbreviations[journal]

        # Then join everything together
        return (
            f"{authors_str}, "
            f"{year}, "
            f"{journal}, "
            f"{self.get_paper_attribute(bibcode, 'volume')}, "
            f"{self.get_paper_attribute(bibcode, 'page')}"
        )

    def get_machine_cite_string(self, bibcode):
        """
        The citation string for a paper, but formatted to be better suited for filenames

        This takes the form {authors}_{year}_{journal}_{volume}_{page}

        If there are 3 or fewer authors all are shown (just their last names), while
        if there are 4 or more the text reads {first author last name}, et al.

        :param bibcode: Bibcode to get the citation string for.
        :type bibcode: str
        :return: cite string for this paper
        :rtype: str
        """
        cite_string = self.get_cite_string(bibcode)
        for c in [",", ".", "&"]:
            cite_string = cite_string.replace(c, "")
        for c in [" ", ":"]:
            cite_string = cite_string.replace(c, "_")
        cite_string = cite_string.replace("et_al", "etal")
        return cite_string.lower()

    @staticmethod
    def _to_internal_tag_name(tag_name):
        """
        Parses a user-supplied tag name into the internal name that will be used in
        the database

        Here we replace spaces with a unique separator, and put "tag" at the beginning

        :param tag_name: User supplied tag name
        :type tag_name: str
        :return: The useful internal tag name for this tag
        :rtype: str
        """
        return f"tag_{tag_name.replace(' ', 'abcdefghijklmnopqrstuvwxyz')}"

    @staticmethod
    def _undo_internal_tag_name(internal_tag_name):
        """
        Parses the intertal tag name into a regular name that the user sees

        :param internal_tag_name: Tag in the database
        :type internal_tag_name: str
        :return: The human-friendly tag name
        :rtype: str
        """
        # first get rid of only the first instance of tag_, which is put at the
        # beginning by the internal format, then throw away the alphabet
        return internal_tag_name.replace("tag_", "", 1).replace(
            "abcdefghijklmnopqrstuvwxyz", " "
        )

    def add_new_tag(self, tag_name):
        """
        Add a new tag option to the database, but does not add it to any papers.

        :param tag_name: Name of the tag to add
        :type tag_name: str
        :return: None
        """
        # check that the tag is not just whitespace
        if tag_name.strip() == "":
            raise ValueError("Tag cannot be empty")
        # I use backticks to enclose the tag name in the SQL query (to allow other
        # punctuation to be included), so they cannot be part of the tag name. My other
        # options were single quotes, double quotes, or square brackets, but I figured
        # backticks were less likely to be included than those other choices
        # See this for more: https://www.sqlite.org/lang_keywords.html
        # I did later find that for old versions of sqlite (I specifically tested
        # 3.30.0, but I don't know what other versions this applies to), square
        # brackets didn't work in tag names, even when surrounded by backticks
        elif "`" in tag_name or "[" in tag_name or "]" in tag_name:
            raise ValueError("Tag cannot include backticks or square brackets")
        # convert the tag name
        internal_tag = self._to_internal_tag_name(tag_name)
        try:
            self._execute(
                f"ALTER TABLE papers "
                f"ADD COLUMN `{internal_tag}` INTEGER NOT NULL "
                f"DEFAULT 0;"
            )
        except sqlite3.OperationalError:  # will happen if the tag is already in there
            raise ValueError("Tag already in database!")

    def delete_tag(self, tag_name):
        """
        Remove a tag from the database

        :param tag_name: The name of the tag to be removed
        :type tag_name: str
        :return: None
        """
        # first check if the tag is valid
        if tag_name not in self.get_all_tags():
            raise ValueError("Tag does not exist!")

        # The easy way to do this is to do:
        # ALTER TABLE papers DROP COLUMN internal_tag
        # but this requires sqlite > 3.35. This came out in 2021, so some people
        # likely do not have it, especially if they're using an older version of
        # python. I won't want users to have to install their own version of sqlite
        # just for this. So instead, I'll do the long way to deleting a column.
        # Documentation found here:
        # sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes
        # first create a new tabls
        self._execute(
            "CREATE TABLE IF NOT EXISTS new_papers"
            "("
            "bibcode text PRIMARY KEY,"
            "title text,"
            "authors text,"
            "pubdate text,"
            "journal text,"
            "volume integer,"
            "page text,"
            "abstract text,"
            "bibtex text,"
            "arxiv_id text,"
            "local_file text,"
            "user_notes text,"
            "citation_keyword text UNIQUE,"
            "update_time real"
            ")"
        )

        # first add columns for all the tags. I'll also keep track of all the columns
        # that will be in the new table, so I can keep track of them. When we use these
        # later, they must be in the same order as when we added them in the previous
        # command (so we can't use the self.colnames_data, which has a different order)
        all_keys = [
            "bibcode",
            "title",
            "authors",
            "pubdate",
            "journal",
            "volume",
            "page",
            "abstract",
            "bibtex",
            "arxiv_id",
            "local_file",
            "user_notes",
            "citation_keyword",
            "update_time",
        ]
        for internal_tag in self._get_all_tags_internal():
            # don't add the tag we're trying to delete
            if self._undo_internal_tag_name(internal_tag) != tag_name:
                # add it to the table, and store it in the list of names we'll
                # transfer data
                self._execute(
                    f"ALTER TABLE new_papers "
                    f"ADD COLUMN `{internal_tag}` INTEGER NOT NULL "
                    f"DEFAULT 0;"
                )
                all_keys.append(internal_tag)
        # then transfer all the data
        # basic format is INSERT INTO new_papers SELECT col1, col2 FROM papers;
        # need to use backticks to enclose each key, to make sure nothing weird happens
        # with certain characters
        self._execute(
            f"INSERT INTO new_papers "
            f'SELECT {",".join([f"`{k}`" for k in all_keys])} '
            f"FROM papers"
        )
        # delete the original, then rename the temp to be the regular table
        self._execute("DROP TABLE papers")
        self._execute("ALTER TABLE new_papers RENAME TO papers")

    def rename_tag(self, old_tag_name, new_tag_name):
        """
        Rename a tag, while keeping it applied to the appropriate papers

        :param old_tag_name: The current name of the tag to rename. Must be a tag
                             present in the database
        :type old_tag_name: str
        :param new_tag_name: The new name of the tag
        :type new_tag_name: str
        :return: None
        """
        # first check if the new tag name is just the old tag name but different in
        # capitalization. This causes issues, as sqlite is case-insensitive. So we'll
        # need to first rename it to something unique, then rename that
        if old_tag_name.lower() == new_tag_name.lower():
            temp_colname = "abczyx" * 10
            self.rename_tag(old_tag_name, temp_colname)
            old_tag_name = temp_colname

        # add the new tag
        self.add_new_tag(new_tag_name)
        # transfer tags
        for bibcode in self.get_all_bibcodes():
            if self.paper_has_tag(bibcode, old_tag_name):
                self.tag_paper(bibcode, new_tag_name)
        # then delete the old paper
        self.delete_tag(old_tag_name)

    def paper_has_tag(self, bibcode, tag_name):
        """
        See if a paper has a given tag.

        :param bibcode: The bibcode of the paper to be searched
        :type bibcode: str
        :param tag_name: The name of the tag to check.
        :type tag_name: str
        :return: Whether or not this tag is applied to this paper/
        :rtype: bool
        """
        internal_tag = self._to_internal_tag_name(tag_name)
        return self.get_paper_attribute(bibcode, internal_tag) == 1

    def tag_paper(self, bibcode, tag_name):
        """
        Add the given tag to the given paper

        :param bibcode: Bibcode of the paper to add the tag to
        :type bibcode: str
        :param tag_name: Tag name to add to this paper
        :type tag_name: str
        :return: None
        """
        self.set_paper_attribute(bibcode, self._to_internal_tag_name(tag_name), 1)

    def untag_paper(self, bibcode, tag_name):
        """
        Remove the given tag to the given paper

        :param bibcode: Bibcode of the paper to remove the tag from
        :type bibcode: str
        :param tag_name: Tag name to remove from this paper
        :type tag_name: str
        :return: None
        """
        self.set_paper_attribute(bibcode, self._to_internal_tag_name(tag_name), 0)

    def _get_all_tags_internal(self):
        """
        Get the names of all tags in the database, in the internal format.

        :return: List of all tags stored in the database
        :rtype: list
        """
        # first we do a dummy query where we can just get the column names. We can't
        # use _execute for this because it doesn't return what we need. But this
        # duplicates part of that
        # use with statements to auto-close
        with contextlib.closing(sqlite3.connect(self.db_file)) as conn:
            with conn:  # auto commits changes to the database
                with contextlib.closing(conn.cursor()) as cursor:
                    cursor.execute("select * from papers where 1=0;")
                    return sorted(
                        [d[0] for d in cursor.description if d[0].startswith("tag_")]
                    )

    def get_all_tags(self):
        """
        Get the names of all tags in the database. This is sorted, ignoring case

        :return: List of tags that are stored in the database
        :rtype: list
        """
        return sorted(
            [self._undo_internal_tag_name(t) for t in self._get_all_tags_internal()],
            key=lambda t: t.lower(),
        )

    def get_paper_tags(self, bibcode):
        """
        Get all the tags applied to a given paper. This is sorted, ignoring case

        :param bibcode: Bibcode of the paper to get the tags of
        :type bibcode: str
        :return: List of tags that this paper has
        :rtype: list
        """
        # We don't need to sort, since get_all_tags() is already sorted.
        return [t for t in self.get_all_tags() if self.paper_has_tag(bibcode, t)]

    def delete_paper(self, bibcode):
        """
        Delete a given paper from the database.

        :param bibcode: Bibcode of the paper to delete from the database.
        :return: None
        """
        # create the SQL code with question marks as the placeholder
        sql = f"DELETE FROM papers WHERE bibcode = ?"
        self._execute(sql, (bibcode,))

    def update_paper(self, old_bibcode):
        """
        Re-ask ADS for the paper details, then update the database if necessary.

        This is useful for papers that are on the arXiv but unpublished. Once ADS gets
        their paper details, they will be added to the database.

        :param old_bibcode: the bibcode of the paper to update.
        :type old_bibcode: str
        :return: None
        """
        # note that we tried to update here, no matter what happens
        self.set_paper_attribute(old_bibcode, "update_time", time.time())
        # need to get the new bibcode. This is actually non-trivial. The best thing to
        # do is to pass the arXiv ID, which can then be sent to ADS. But some papers
        # are not on the arXiv. So we skip these papers. I only found this applied to
        # one paper, which was a PhD thesis, so it is an edge case.
        arxiv_id = self.get_paper_attribute(old_bibcode, "arxiv_id")
        if arxiv_id == "Not on the arXiv":
            return
        new_bibcode = ads_call.get_bibcode(arxiv_id)
        if old_bibcode == new_bibcode:
            # no update found, we can exit
            return

        # the easiest thing is to actually delete the original paper, then add a new
        # one with the new bibcode, keeping the data that's user-generated. Don't yet
        # update the citation keyword, since that must be unique. We instead do that
        # after deleting the paper, but have to get it first
        self.add_paper(new_bibcode)
        for field in ["user_notes", "local_file"]:
            old_attribute = self.get_paper_attribute(old_bibcode, field)
            self.set_paper_attribute(new_bibcode, field, old_attribute)
        old_citation_keyword = self.get_paper_attribute(old_bibcode, "citation_keyword")
        # also transfer the tags
        for tag in self.get_paper_tags(old_bibcode):
            self.tag_paper(new_bibcode, tag)

        # then delete the paper
        self.delete_paper(old_bibcode)
        # and set the citation keyword. If it's just the default bibcode, I'll update
        # to the new bibcode. If the user had set a custom keyword, keep that.
        if old_citation_keyword == old_bibcode:
            self.set_paper_attribute(new_bibcode, "citation_keyword", new_bibcode)
        else:
            self.set_paper_attribute(
                new_bibcode, "citation_keyword", old_citation_keyword
            )

    def export(self, tag_name, file_name):
        """
        Export the bibtex entries for all papers or all papers with a given tag.

        :param tag_name: The subset of papers to be written. Either pass "all" to write
                         all papers of the name of a tag to write only those papers.
        :type tag_name: str
        :param file_name: The location to write the output file. If this file already
                          exists, it will be overwritten
        :type file_name: pathlib.Path
        :return: None
        """
        # check that the tag exists
        if tag_name not in self.get_all_tags() + ["all"]:
            raise ValueError("This tag does not exist")
        # otherwise, write to the file
        with open(file_name, "w") as out_file:
            for bibcode in self.get_all_bibcodes():
                if tag_name == "all" or self.paper_has_tag(bibcode, tag_name):
                    out_file.write(self.get_paper_attribute(bibcode, "bibtex"))
                    out_file.write("\n")

    def import_bibtex(self, file_name, update_progress_bar=None):
        """
        Import papers from a bibtex file into the database

        :param file_name: The location of the bibtex file to import
        :type file_name: pathlib.Path
        :param update_progress_bar: A function that can be called to update a progress
                                    bar. This must be previously initialized to be the
                                    number of lines in the file. In this function, we
                                    will call the function passed in here with the line
                                    number of the current line to update the progressbar
        :type update_progress_bar: func
        :return: A tuple indicating the results of what happened. First is the number
                 of papers added successfully, then the number of papers that were
                 already in the database (this can include duplicate papers within the
                 bibtex file), then the bibtex entries I could not successfully add to
                 the database for whatever reason. The next element is the path of a
                 file where I write the failed bibtex entries for the user to inspect.
                 Finally, there is the name of the tag applied to the added papers.
        """
        bibfile = open(file_name, "r")
        # We'll create a file holding the bibtex entries that I could not identify.
        # We'll delete this later if it has nothing in it
        failure_file_loc = self._failure_file_loc(file_name)
        failure_file = open(failure_file_loc, "w")
        # write the header to this file
        header = (
            "% This file contains BibTeX entries that the library could not add.\n"
            "% The reason for the failure is given above each entry.\n"
            '% When importing a given entry, the code looks for the "doi", "ads_url",\n'
            '% or "eprint" attributes. If none of these are present, the code cannot\n'
            "% add the paper. In addition, there may be something wrong with the\n"
            "% format of the entry that breaks my code parser."
        )
        failure_file.write(header + "\n\n")

        # figure out what tag to give this paper. It will be of the format
        # "Import [import_filename] X", where X is an optional integer that will be
        # present if this file is imported more than once, and will
        base_tag = f"Import {file_name.name}"
        import_tags = [t for t in self.get_all_tags() if t.startswith(base_tag)]
        if len(import_tags) == 0:
            new_tag = base_tag
        # check the case that there's just one tag
        elif import_tags == [base_tag]:
            new_tag = base_tag + " 2"
        # there are multiple of these tags already present, so we need to increment
        else:
            tag_nums = [int(t.split()[-1]) for t in import_tags if t != base_tag]
            new_tag = base_tag + f" {max(tag_nums) + 1}"
        self.add_new_tag(new_tag)

        results = {"success": 0, "duplicate": 0, "failure": 0}
        current_entry = ""
        line_number = 0
        for line in bibfile:
            # skip comments and empty lines
            if line.startswith("%") or line.strip() == "":
                continue
            # once we get to the beginning of a new entry, add the current entry to
            # the database. Otherwise, keep track of the current entry
            if line.startswith("@") and current_entry.strip() != "":
                this_result = self._parse_bibtex_entry(
                    current_entry, new_tag, failure_file
                )
                results[this_result] += 1

                # once we have parsed the previous entry, start the new one
                current_entry = line
            else:
                current_entry += line

            if update_progress_bar is not None:
                line_number += 1
                update_progress_bar(line_number)

        # handle the final entry
        if current_entry.strip() != "":
            results[self._parse_bibtex_entry(current_entry, new_tag, failure_file)] += 1

        bibfile.close()
        failure_file.close()
        # if there were no failures, remove the failure file. I got the exact size of
        # just the header, which is what we compare to here
        if failure_file_loc.stat().st_size == 388:
            failure_file_loc.unlink()
            failure_file_loc = None

        return (
            results["success"],
            results["duplicate"],
            results["failure"],
            failure_file_loc,
            new_tag,
        )

    def _failure_file_loc(self, bibtex_file_loc):
        """
        Parse the name of the import bibtex file into the file to write the failures

        I considered writing this to the same directory as the import directory, but
        since users may not want this writing files to what could be shared directories,
        so I'll write it in this directory

        :param bibtex_file_loc: Path to the original bibtex entry
        :type: pathlib.Path
        :return: path to the place to write failures
        :rtype: pathlib.Path
        """
        directory = Path(__file__).parent.parent
        name = bibtex_file_loc.stem + ".failures" + bibtex_file_loc.suffix
        return directory / name

    def _parse_bibtex_entry(self, entry, tag_name, failure_file):
        """
        Wrapper around the function to parse a single bibtex entry and add it to the db

        This also identifies what happened with success vs failure by returning one of
        three strings: "success", "failure", or "duplicate"

        :param entry: the bibtex entry to add
        :type entry: str
        :param tag_name: tag to apply to the paper if added successfully
        :type tag_name: str
        :param failure_file: file object to write any failed bibtex entries to
        :type failure_file: io.TextIO
        :return: String indicating what happened
        :rtype: str
        """
        try:
            self._parse_bibtex_entry_inner(entry, tag_name)
            return "success"
        except PaperAlreadyInDatabaseError:
            return "duplicate"
        except Exception as e:  # any other error
            # add to failure file, with the error
            # make non useful errors more useful
            e = str(e)
            if "Bad Gateway" in e:
                e = (
                    "Connection lost when querying ADS for this paper. "
                    "This may work if you try again"
                )
            elif "Too many requests" in e:
                e = (
                    "ADS has cut you off, you have sent too many requests today. "
                    "Try again in ~24 hours"
                )
            elif "INVALID_SYNTAX_CANNOT_PARSE" in e:
                e = "something appears wrong with the format of this entry"
            failure_file.write(f"% {e}\n")
            failure_file.write(entry + "\n")
            return "failure"

    def _parse_bibtex_entry_inner(self, entry, tag_name):
        """
        Handle a single bibtex entry and add it to the database

        :param entry: the bibtex entry to add
        :type entry: str
        :param tag_name: tag to apply to the paper if added successfully
        :type tag_name: str
        :return: None
        """
        # Start by parsing the entry to get paper data. We'll then use this to find
        # the paper
        paper_data = dict()
        for line in entry.split("\n"):
            if line.startswith("@"):
                # get the citation keyword
                idx_1 = line.find("{")
                idx_2 = line.find(",")
                paper_data["cite_key"] = line[idx_1 + 1 : idx_2]
                continue
            # only look at lines that are interesting to us
            elif " = " in line:
                # the key and value are separated by an equals sign surrounded by
                # spaces. But we need to be careful, since sometimes titles can
                # have the same pattern
                split_line = line.split(" = ")
                key = split_line[0]
                value = " = ".join(split_line[1:])
                paper_data[key.strip()] = (
                    value.strip()
                    .rstrip(",")
                    .replace("{", "")
                    .replace("}", "")
                    .replace('"', "")
                )

        # now that we have the info, try to find the paper. I'll keep track of what was
        # tried, then use that to construct an error message if needed. I try the ADS
        # url first, since that results in less queries to ADS, speeding up this
        # process
        error_message = ""
        for bibcode_func in [
            self._get_bibcode_from_adsurl,
            self._get_bibcode_from_doi,
            self._get_bibcode_from_eprint,
            self._get_bibcode_from_journal,
        ]:
            try:
                bibcode = bibcode_func(paper_data)
                break
            except Exception as e:
                # add this to the error message
                if error_message != "" and str(e) != "":
                    error_message += ", "
                error_message += str(e)
        else:  # no break, so the bibcode was not found
            # the bibcode_from_journal function always gives an error message, so we
            # so not need a default error message
            raise ValueError(error_message)

        try:
            self.add_paper(bibcode)
        except PaperAlreadyInDatabaseError:
            # catch this just to add the tag, then raise it again so the parent function
            # can catch this esception
            self.tag_paper(bibcode, tag_name)
            raise PaperAlreadyInDatabaseError

        # I attempted to validate that the properties in the bibtex entry matched
        # what the query returned, but I gave up on this. The journal often has
        # abbreviations that make it very difficult to compare. And the page entry in
        # BibTeX is sometimes just the first page, while sometimes its the range. So
        # I just gave up on this. To add a paper, we need either the ADS link, the DOI,
        # or the arXiv ID from the bibtex entry. With one of those, we assume that the
        # paper details are correct.

        # if we got here, the paper was added successfully. Remove unread, if present.
        # I'm assuming that if they're importing from a bibtex file, they've already
        # read the paper, while if they're adding from ADS, that may not be the case.
        # Not that duplicates already exited, so if they were unread that stays.
        # Also add the special tag
        current_tags = self.get_paper_tags(bibcode)
        for c_tag in current_tags:
            if c_tag.lower() == "unread":
                self.untag_paper(bibcode, c_tag)
        self.tag_paper(bibcode, tag_name)

        # Also add the citation keyword for new papers. Again, if the paper is already
        # in the library, we don't mess with its cite key
        # don't bother changing it if there would be no change
        if paper_data["cite_key"] != bibcode:
            try:
                self.set_paper_attribute(
                    bibcode, "citation_keyword", paper_data["cite_key"]
                )
            except RuntimeError:  # duplicate citation key
                pass  # just leave as the bibcode

    def _get_bibcode_from_adsurl(self, paper_data):
        """
        Query ADS to get a bibcode from the adsurl, or tell if it didn't work

        This will return the bibcode, or raise an error. If the adsurl is not in
        the dictionary, this will raise an error with an empty message string, since
        the user doesn't need to know that we checked this. Otherwise, the error will
        be appropriate to send to the user

        :param paper_data: the dictionary with attributes of the bibtex entry
        :type paper_data: dict
        :return: the bibcode
        :rtype: str
        """
        if "adsurl" not in paper_data:
            raise KeyError()
        try:
            bibcode = ads_call.get_bibcode(paper_data["adsurl"])
            # validate that this bibcode is valid by querying ADS for the paper
            # details. We'd do this later, but the results are cached, so we're not
            # wasting a query
            ads_call.get_info(bibcode)
            return bibcode
        except Exception as e:  # anything else
            e = str(e)
            if e == "list index out of range" or (
                e.startswith("Identifier") and e.endswith("not recognized")
            ):
                e = "adsurl not recognized"
            raise ValueError(str(e))

    def _get_bibcode_from_doi(self, paper_data):
        """
        Query ADS to get a bibcode from the doi, or tell if it didn't work

        This will return the bibcode, or raise an error. If the doi is not in
        the dictionary, this will raise an error with an empty message string, since
        the user doesn't need to know that we checked this. Otherwise, the error will
        be appropriate to send to the user

        :param paper_data: the dictionary with attributes of the bibtex entry
        :type paper_data: dict
        :return: the bibcode
        :rtype: str
        """
        if "doi" not in paper_data:
            raise KeyError()
        try:
            return ads_call.get_bibcode(paper_data["doi"])
        except Exception as e:  # anything else
            raise ValueError(str(e))

    def _get_bibcode_from_eprint(self, paper_data):
        """
        Query ADS to get a bibcode from the eprint, or tell if it didn't work

        This will return the bibcode, or raise an error. If the eprint is not in
        the dictionary, this will raise an error with an empty message string, since
        the user doesn't need to know that we checked this. Otherwise, the error will
        be appropriate to send to the user

        :param paper_data: the dictionary with attributes of the bibtex entry
        :type paper_data: dict
        :return: the bibcode
        :rtype: str
        """
        if "eprint" not in paper_data:
            raise KeyError()
        try:
            return ads_call.get_bibcode(paper_data["eprint"])
        except Exception as e:  # anything else
            raise ValueError(str(e))

    def _get_bibcode_from_journal(self, paper_data):
        """
        Query ADS to get a bibcode from the full paper info, or tell if it didn't work

        This will return the bibcode, or raise an error. If the required details are
        not in the dictionary, this will raise an error with an empty message string,
        since the user doesn't need to know that we checked this. Otherwise, the
        error will be appropriate to send to the user

        :param paper_data: the dictionary with attributes of the bibtex entry
        :type paper_data: dict
        :return: the bibcode
        :rtype: str
        """
        # otherwise, we have the info we need. First, parse the pages attribute so that
        # it's just the first page, not the range. That makes checks easier
        if "pages" in paper_data:
            paper_data["pages"] = paper_data["pages"].split("-")[0]
        # This function may raise errors, but those
        # are good for the user to see
        return ads_call.get_bibcode_from_journal(**paper_data)
