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
)


class Tag(QLabel):
    """
    Class representing the tags that go in the left panel
    """

    def __init__(self, tagName):
        """
        Create the tab object with the given name.

        :param tagName: Name that will be displayed on the tag
        :type tagName: str
        """
        QLabel.__init__(self, tagName)
        self.setFixedHeight(25)
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

        # Then set up the layout this uses. It will be vertical with the title (for now)
        vBox = QVBoxLayout()
        self.titleText = QLabel(self.title)
        self.titleText.setFont(QFont("Cabin", 16))

        # then add these to the layout, then set this layout
        vBox.addWidget(self.titleText)
        self.setLayout(vBox)

    def mousePressEvent(self, event):
        """
        Handle the clicks - single click will display details, double will open paper

        :param event: Mouse click event object
        :type event: PySide2.QtGui.QMouseEvent
        :return: None
        """
        if event.type() is QEvent.Type.MouseButtonPress:
            self.rightPanel.setPaperDetails(self.title, self.abstract)
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
            # if we now have a path, open the file
            QDesktopServices.openUrl(f"file:{local_file}")
        # nothing should be done for other click types


class RightPanel(QWidget):
    """
    The right panel area for the main window, holding paper info for a single paper
    """

    def __init__(self):
        """
        Initialize the right panel. This is boilerplate, nothing is passed in.
        """
        QWidget.__init__(self)

        # This widget will have 2 main areas (for now): The title and abstract
        # all laid out vertically
        vBox = QVBoxLayout()

        self.titleText = QLabel("")
        self.abstractText = QLabel("")

        # set text properties
        self.titleText.setFont(QFont("Cabin", 20))
        self.abstractText.setFont(QFont("Cabin", 14))

        self.titleText.setWordWrap(True)
        self.abstractText.setWordWrap(True)

        # add these to the layout
        vBox.addWidget(self.titleText)
        vBox.addWidget(self.abstractText)

        self.setLayout(vBox)

    def setPaperDetails(self, title, abstract):
        """
        Update the details shown in the right panel.

        :param title: Title to be shown in the right panel
        :type title: str
        :param abstract: Abstract to be shown in the right panel
        :type abstract: str
        :return: None, but the text properties are set.
        """
        self.titleText.setText(title)
        self.abstractText.setText(abstract)
        self.repaint()


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
        # the widgets should have their fixed size, no modification
        self.layout.setSizeConstraint(QLayout.SetFixedSize)
        # have the spacing between them be zero. Let the widgets handle their own spaces
        self.layout.setSpacing(0)

        # Then add these layouts and widgets
        self.container.setLayout(self.layout)
        self.setWidget(self.container)
        # have the scroll bar only appear when needed
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def addWidget(self, widget):
        """
        Add a widget to the list of vertical objects

        :param widget: Widget to be added to the layout.
        :type widget: QWidget
        :return: None
        """
        # add the widget to the layout
        self.layout.addWidget(widget)


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

        self.default_font = QFont("Cabin", 14)

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
        self.searchBar.setFont(self.default_font)
        # We'll also have an add button
        self.addButton = QPushButton("Add")
        self.addButton.setFont(self.default_font)
        # Define what to do when these things are activated. The user can either hit
        # enter or hit the add button
        self.searchBar.returnPressed.connect(self.addPaper)
        self.addButton.clicked.connect(self.addPaper)
        # have both of these quantities have a fixed height
        self.searchBar.setFixedHeight(30)
        self.addButton.setFixedHeight(30)
        # Then add these to the layouts
        hBoxSearchBar.addWidget(self.searchBar)
        hBoxSearchBar.addWidget(self.addButton)
        vBoxMain.addLayout(hBoxSearchBar)

        # Then we have the main body. This is a bit more complex. We'll start by just
        # initializing the layout for this, which is three panels laid horizonatlly.
        # This is the default splitter orientation
        splitter = QSplitter()
        # then make each of these things

        # The left panel of this is the list of tags the user has.
        # We'll have dummy tags for now
        leftScroll = ScrollArea()
        for i in range(10):
            leftScroll.addWidget(Tag(f"Tag {i}"))

        # The right panel is the details on a given paper
        self.rightPanel = RightPanel()
        rightScroll = ScrollArea()
        rightScroll.addWidget(self.rightPanel)

        # The central panel is the list of papers. This has to be set up after the
        # right panel because the paper objects need it.
        centerScroll = ScrollArea()
        for b in self.db.get_all_bibcodes():
            centerScroll.addWidget(Paper(b, db, self.rightPanel))

        # then add each of these widgets to the central splitter
        splitter.addWidget(leftScroll)
        splitter.addWidget(centerScroll)
        splitter.addWidget(rightScroll)
        # set the default widths of each panel, in pixels. Below we will set the width
        # of the main window to 1000, so this should sum to that.
        splitter.setSizes([150, 550, 300])

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
        # I'll use "close" instead
        self.exitAction = QAction("Close", self)
        self.exitAction.setShortcut(QKeySequence("Ctrl+q"))
        # have to connect this to a function to actually do something
        self.exitAction.triggered.connect(QApplication.quit())

        # Then add all items to the menu
        self.file_menu.addAction(self.exitAction)

        # Set the window title
        self.setWindowTitle("")

        # and the initial window size
        self.resize(1000, 600)
        self.show()

    def addPaper(self):
        """
        Add a paper to the database, taking text from the text box

        :return: None, but the user's input is added to the database
        """
        self.db.add_paper(self.searchBar.text())


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
