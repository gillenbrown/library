from pathlib import Path

from PySide2.QtCore import Qt, QEvent
from PySide2.QtGui import QKeySequence, QFontDatabase, QFont, QDesktopServices
from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QAction,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSplitter,
    QLineEdit,
    QPushButton,
    QLayout,
    QFileDialog,
    QCheckBox,
)

from library.database import PaperAlreadyInDatabaseError


class Tag(QLabel):
    """
    Class holding a tag that goes in the left panel
    """

    def __init__(self, tagName):
        QLabel.__init__(self, tagName)
        self.name = tagName
        self.setFont(QFont("Cabin", 14))


class Paper(QWidget):
    """
    Class holding paper details that goes in the central panel
    """

    def __init__(self, bibcode, db, rightPanel):
        """
        Initialize the paper object, which will hold the given bibcode

        :param bibcode: Bibcode of this paper
        :type bibcode: str
        :param db: Database object this interface is using
        :type db: library.database.Database
        :param rightPanel: rightPanel object of this interface. This is only needed so
                           we can call the update feature when this is clicked on
        :type rightPanel: rightPanel
        """
        QWidget.__init__(self)

        # store the information that will be needed later
        self.bibcode = bibcode
        self.db = db
        self.rightPanel = rightPanel

        # make sure this paper is actually in the database. This should never happen, but
        # might if I do something dumb in tests
        assert self.bibcode in self.db.get_all_bibcodes()

        # Use the database to get the details needed
        self.title = db.get_paper_attribute(self.bibcode, "title")
        self.abstract = db.get_paper_attribute(self.bibcode, "abstract")
        self.citeString = db.get_cite_string(self.bibcode)

        # Then set up the layout this uses. It will be vertical with the title (for now)
        vBox = QVBoxLayout()
        self.titleText = QLabel(self.title)
        self.titleText.setFont(QFont("Cabin", 16))

        self.citeText = QLabel(self.citeString)
        self.citeText.setFont(QFont("Cabin", 12))

        # then add these to the layout, then set this layout
        vBox.addWidget(self.titleText)
        vBox.addWidget(self.citeText)
        self.setLayout(vBox)

    def mousePressEvent(self, event):
        """
        Handle the clicks - single click will display details, double will open paper

        :param event: Mouse click event object
        :type event: PySide2.QtGui.QMouseEvent
        :return: None
        """
        if event.type() is QEvent.Type.MouseButtonPress:
            # We get the tags now, since they may change, and we don't want to store
            # them at initialization
            self.rightPanel.setPaperDetails(
                self.title,
                self.citeString,
                self.abstract,
                self.db.get_paper_tags(self.bibcode),
            )
        elif event.type() is QEvent.Type.MouseButtonDblClick:
            local_file = self.db.get_paper_attribute(self.bibcode, "local_file")
            if self.db.get_paper_attribute(self.bibcode, "local_file") is None:
                # if there is not a paper, we need to add it
                local_file = QFileDialog.getOpenFileName(filter="PDF(*.pdf)")
                # If the user doesn't select anything this returns the empty string.
                # Otherwise this returns a two item tuple, where the first item is the
                # absolute path to the file they picked
                if local_file != "":
                    local_file = local_file[0]
                    self.db.set_paper_attribute(self.bibcode, "local_file", local_file)
                    # we'll open this file in a minute
                else:
                    # the user didn't pick anything, so don't open anything
                    return
            # if we now have a path, open the file. We get here whether we had to ask
            # the user or now
            QDesktopServices.openUrl(f"file:{local_file}")
        # nothing should be done for other click types


class RightPanel(QWidget):
    """
    The right panel area for the main window, holding paper info for a single paper
    """

    def __init__(self, tagCheckboxes):
        """
        Initialize the right panel. Most is boilerplate, but we need the checkboxes

        :param tagCheckboxes: The checkbox object the user will select tags from.
        :type tagCheckboxes: TagsCheckboxList
        """
        QWidget.__init__(self)

        self.tagCheckboxes = tagCheckboxes

        # This widget will have several main areas, all laid out vertically
        vBox = QVBoxLayout()

        self.titleText = QLabel("")
        self.citeText = QLabel("")
        self.abstractText = QLabel("Click on a paper to show its details here")
        self.tagText = QLabel("")

        # set text properties
        self.titleText.setFont(QFont("Cabin", 20))
        self.citeText.setFont(QFont("Cabin", 16))
        self.abstractText.setFont(QFont("Cabin", 14))
        self.tagText.setFont(QFont("Cabin", 14))

        self.titleText.setWordWrap(True)
        self.citeText.setWordWrap(True)
        self.abstractText.setWordWrap(True)
        self.tagText.setWordWrap(True)

        # add these to the layout
        vBox.addWidget(self.titleText)
        vBox.addWidget(self.citeText)
        vBox.addWidget(self.abstractText)
        vBox.addWidget(self.tagText)
        vBox.addWidget(self.tagCheckboxes)

        self.setLayout(vBox)

    def setPaperDetails(self, title, citeText, abstract, tagsList):
        """
        Update the details shown in the right panel.

        :param title: Title to be shown in the right panel
        :type title: str
        :param citeText: The short citation string to show in the right panel
        :type citeText: str
        :param abstract: Abstract to be shown in the right panel
        :type abstract: str
        :param tagsList: List of tags to be shown in the right panel.
        :type tagsList: list
        :return: None, but the text properties are set.
        """
        self.titleText.setText(title)
        self.citeText.setText(citeText)
        self.abstractText.setText(abstract)
        self.tagText.setText(f"Tags: {', '.join(tagsList)}")


class ScrollArea(QScrollArea):
    """
    A wrapper around QScrollArea with a vertical layout, appropriate for lists
    """

    def __init__(self):
        """
        Setup the scroll area, no parameters needed.
        """
        QScrollArea.__init__(self)

        # Have a central widget with a vertical box layout
        self.container = QWidget()
        self.layout = QVBoxLayout()
        # the widgets should have their fixed size, no modification. This is also
        # needed to get them to show up, I believe to stop this from having zero size?
        self.layout.setSizeConstraint(QLayout.SetFixedSize)

        # Then add these layouts and widgets
        self.container.setLayout(self.layout)
        self.setWidget(self.container)

    def addWidget(self, widget):
        """
        Add a widget to the list of vertical objects

        :param widget: Widget to be added to the layout.
        :type widget: QWidget
        :return: None
        """
        # add the widget to the layout
        self.layout.addWidget(widget)


class PapersListScrollArea(ScrollArea):
    """
    The class to be used for the central list of papers.

    It's just a ScrollArea that keeps track of the papers that have been added.
    """

    def __init__(self):
        """
        Set up the papers list, no parameters needed
        """
        ScrollArea.__init__(self)
        self.papers = []

    def addPaper(self, paper):
        """
        Add a paper to the papers scroll area.

        This adds it to the internal list of papers and puts the widget in the interface

        :param paper: Paper object to be added to the list of stored papers.
        :type paper: Paper
        :return: None
        """
        # check if this paper is already in the list. This should never happen
        assert paper.bibcode not in [p.bibcode for p in self.papers]

        self.papers.append(paper)
        self.addWidget(paper)  # calls the ScrollArea addWidget


class TagsListScrollArea(ScrollArea):
    """
    The class to be used for the left hand side list of tags.

    It's just a ScrollArea that keeps track of the tags that have been added, almost
    identical to PapersListScrollArea, except that it has a text area to add tags.
    """

    def __init__(self, addTagBar):
        """
        Set up the papers list, no parameters needed
        """
        ScrollArea.__init__(self)
        self.tags = []
        self.addTagBar = addTagBar

        # put the tag bar at the top of the list
        self.addWidget(self.addTagBar)  # calls ScrollArea addWidget

    def addTag(self, tag):
        """
        Add a tag to the tags scroll area.

        This adds it to the internal list of tags and puts the widget in the interface

        :param tag: Tag object to be added to the list of stored tags.
        :type tag: Tag
        :return: None
        """
        # check if this tag is already in the list. This should never happen
        assert tag.name not in [t.name for t in self.tags]

        self.tags.append(tag)
        self.addWidget(tag)  # calls the ScrollArea addWidget


class TagsCheckboxList(QWidget):
    """
    Class holding the list of tag checkboxes that will go in the right panel
    """

    def __init__(self, db):
        """
        Initialize the list, getting the tags from the database

        :param db: Database object this interface is using
        :type db: library.database.Database
        """
        QWidget.__init__(self)

        # store a list of tags that are in the list
        self.tags = []
        vBox = QVBoxLayout()
        # go through the database and add checkboxes for each tag there.
        for t in db.get_all_tags():
            this_tag_checkbox = QCheckBox(t)
            self.tags.append(this_tag_checkbox)
            vBox.addWidget(this_tag_checkbox)
        # then add this so it shows up
        self.setLayout(vBox)


class MainWindow(QMainWindow):
    """
    Main window object holding everything needed in the interface.
    """

    def __init__(self, db):
        """
        Create the interface around the database passed in.

        :param db: database object that will be displayed in this interface.
        :type db: library.database.Database
        """
        QMainWindow.__init__(self)

        self.db = db

        # Start with the layout. Our main layout is three vertical components:
        # the first is the title, second is the search bar, where the user can paste
        # URLs to add to the database, and the third is the place where we show all
        # the papers that have been added.
        vBoxMain = QVBoxLayout()

        # The title is first
        self.title = QLabel("Library")
        # Mess around with the title formatting
        self.title.setFixedHeight(60)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Lobster", 40))
        vBoxMain.addWidget(self.title)

        # Then comes the search bar. This is it's own horizontal layout, with the
        # text box and the button to add
        hBoxSearchBar = QHBoxLayout()
        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Enter your paper URL or ADS bibcode here")
        self.searchBar.setFont(QFont("Cabin", 14))
        # We'll also have an add button
        self.addButton = QPushButton("Add")
        self.addButton.setFont(QFont("Cabin", 14))
        # Define what to do when these things are activated. The user can either hit
        # enter or hit the add button
        self.searchBar.returnPressed.connect(self.addPaper)
        self.addButton.clicked.connect(self.addPaper)
        # have both of these quantities have a fixed height. These values are chosen to
        # make it look nice. They aren't the same size since the bounding boxes aren't
        # quite the same relative to the shown borders for whatever reason
        self.searchBar.setFixedHeight(30)
        self.addButton.setFixedHeight(35)
        # Then add these to the layouts
        hBoxSearchBar.addWidget(self.searchBar)
        hBoxSearchBar.addWidget(self.addButton)
        vBoxMain.addLayout(hBoxSearchBar)

        # Then we have the main body. This is a bit more complex. We'll start by just
        # initializing the layout for this, which is three panels laid horizonatlly.
        # This is the default splitter orientation
        splitter = QSplitter()
        # then make each of these things

        # The left panel of this is the list of tags the user has, plus the button to
        # add papers, which will go at the top of that list
        addTagBar = QLineEdit()
        addTagBar.setFont(QFont("Cabin", 14))
        addTagBar.setPlaceholderText("Add a new tag here")
        addTagBar.returnPressed.connect(self.addTag)
        self.tagsList = TagsListScrollArea(addTagBar)
        for t in self.db.get_all_tags():
            self.tagsList.addTag(Tag(t))

        # The right panel is the details on a given paper. It holds the tags list,
        # which we need to initialize first
        self.tagsCheckboxList = TagsCheckboxList(self.db)
        self.rightPanel = RightPanel(self.tagsCheckboxList)
        rightScroll = ScrollArea()
        rightScroll.addWidget(self.rightPanel)

        # The central panel is the list of papers. This has to be set up after the
        # right panel because the paper objects need it.
        self.papersList = PapersListScrollArea()
        for b in self.db.get_all_bibcodes():
            self.papersList.addPaper(Paper(b, db, self.rightPanel))

        # then add each of these widgets to the central splitter
        splitter.addWidget(self.tagsList)
        splitter.addWidget(self.papersList)
        splitter.addWidget(rightScroll)

        # Add this to the main layout
        vBoxMain.addWidget(splitter)

        # We then have to have a dummy widget to act as the central widget. All that
        # is done here is setting the layout
        container = QWidget()
        container.setLayout(vBoxMain)
        self.setCentralWidget(container)

        # Then let's set up a menu.
        self.menu = self.menuBar()
        # have the file option
        self.file_menu = self.menu.addMenu("File")

        # Things to go in the menu
        # Calling the Quit command can't be used, as it is caught by MacOS somehow
        # I'll use "close" instead. This does automatically use the keyboard shortcut
        # ctrl+q to exit
        self.exitAction = QAction("Close", self)
        self.exitAction.setShortcut(QKeySequence("Ctrl+q"))  # to be clear
        # have to connect this to a function to actually do something
        self.exitAction.triggered.connect(QApplication.quit())

        # Then add all items to the menu
        self.file_menu.addAction(self.exitAction)

        # and the initial window size
        self.resize(1000, 600)
        self.show()

    def addPaper(self):
        """
        Add a paper to the database, taking text from the text box.

        If what is in the text box is not recognized, the text will not be cleared, and
        nothing will be added (obviously). If the paper is already in the library,
        the paper will not be added but the text will be cleared.

        :return: None
        """
        try:  # see if the user put something good
            bibcode = self.db.add_paper(self.searchBar.text())
        except ValueError:  # will be raised if the value isn't recognized
            return  # don't clear the text or add anything
        except PaperAlreadyInDatabaseError:
            # here we do clear the search bar, but do not add the paper
            self.searchBar.clear()
            return

        # we only get here if the addition to the database worked. If so we add the
        # paper object, then clear the search bar
        self.papersList.addPaper(Paper(bibcode, self.db, self.rightPanel))
        # clear the text so another paper can be added
        self.searchBar.clear()

    def addTag(self):
        """
        Adds a tag to the database, taking the name from the text box.

        The text will be cleared if the tag was successfully added, which will only not
        be the case if the tag is already in the database.

        :return: None
        """
        #
        try:
            tagName = self.tagsList.addTagBar.text()
            self.db.add_new_tag(tagName)
            self.tagsList.addTag(Tag(tagName))
        except ValueError:  # this tag is already in the database
            return

        # if we got here we had no error, so it was successfully added and we should
        # clear the text box
        self.tagsList.addTagBar.clear()


def get_fonts(directory, current_list):
    """
    Recursive function to get all the fonts within a directory, including all subdirs

    Note that all fonts must have the `.ttf` file extension.

    :param directory: Parent directory to search for fonts
    :type directory: pathlib.Path
    :param current_list: List of fonts that have been found so far. This will be
                         appended to, so that it can be modified in place, and will
                         also be returned, so the first caller of this can get the list.
    :type current_list: list
    :return: None
    """
    # go through everything in this directory
    for item in directory.iterdir():
        # if it's a directory, recursively call this function on that directory.
        if item.is_dir():
            get_fonts(item, current_list)
            # current_list will be modified in place, so we don't need to keep
            # the returned value
        # otherwise look for ttf files.
        if str(item).endswith(".ttf"):
            current_list.append(str(item))


def set_up_fonts():
    """
    Add all the found fonts to the Qt font database

    :return: None, but the fonts are added to the Qt font database
    """
    fontDb = QFontDatabase()
    # we need to initialize this list to start, as fonts found will be appended to this
    fonts = []
    get_fonts(Path(__file__).parent.parent / "fonts", fonts)
    for font in fonts:
        fontDb.addApplicationFont(font)
