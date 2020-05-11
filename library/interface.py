"""
interface.py

This holds the GUI that will be used when the library is run. This is the script that
should be called to initialize the program.
"""
import sys
from pathlib import Path

from PySide2.QtCore import Qt
from PySide2 import QtGui
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
)

from library.lib import Library


class Tag(QLabel):
    def __init__(self, tagName):
        QLabel.__init__(self, tagName)
        self.setFixedHeight(25)
        self.setFont(QtGui.QFont("Cabin", 14))


class ScrollArea(QScrollArea):
    """
    A wrapper around QScrollArea with a vertical layout, appropriate for lists
    """

    def __init__(self):
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

    def addWidget(self, widget):
        # add the widget to the layout
        self.layout.addWidget(widget)


class MainWindow(QMainWindow):
    def __init__(self, lib):
        QMainWindow.__init__(self)

        self.lib = lib

        self.default_font = QtGui.QFont("Cabin", 14)

        # Start with the layout. Our main layout is two vertical components:
        # the first is the search bar, where the user can paste URLs to add to the l
        # library, and the second is the place where we show all the papers that have
        # been added.
        vBoxMain = QVBoxLayout()

        # The title is first
        self.title = QLabel("Library")
        # Mess around with the title formatting
        self.title.setFixedHeight(60)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QtGui.QFont("Lobster", 40))
        vBoxMain.addWidget(self.title)

        # Then comes the search bar. This is it's own horizontal layout
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

        # The left panel of this is the list of tags the user has. We'll have dummy tags
        leftScroll = ScrollArea()
        for i in range(10):
            leftScroll.addWidget(Tag(f"Tag {i}"))

        # The central panel is the list of papers
        centerScroll = ScrollArea()
        for b in self.lib.get_all_bibcodes():
            # for now just use the Tag class, will eventually make another Paper widget
            centerScroll.addWidget(Tag(b))

        # Then the right panel is the details on a given paper
        rightScroll = ScrollArea()
        # add dummy junk for now
        for i in range(20):
            # for now just use the Tag class, will eventually make another widget
            rightScroll.addWidget(Tag(f"Attribute {i}"))

        # Then we have the main body. This is a bit more complex. We'll start by just
        # initializing the layout for this, which is three panels laid horizonatlly.
        # This is the default splitter orientation
        splitter = QSplitter()
        splitter.addWidget(leftScroll)
        splitter.addWidget(centerScroll)
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
        # I'll use "close" instead
        self.exitAction = QAction("Close", self)
        self.exitAction.setShortcut("Ctrl+Q")
        # have to connect this to a function to actually do something
        self.exitAction.triggered.connect(QApplication.quit)

        # Then add all items to the menu
        self.file_menu.addAction(self.exitAction)

        # Set the window title
        self.setWindowTitle("")

        # and the initial window size
        self.resize(800, 600)
        self.show()

    def addPaper(self):
        self.lib.add_paper(self.searchBar.text())


def get_fonts(directory, current_list):
    """
    Recursive function to get all the fonts within a directory, including all subdirs

    Note that all fonts must have the `.ttf` file extension.

    :param directory: Parent directory to search for fonts
    :param current_list: List of fonts that have been found so far. This will be
                         appended to, so that it can be modified in place, and will
                         also be returned, so the first caller of this can get the list.
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
    # then add all our fonts
    fontDb = QtGui.QFontDatabase()
    # we need to initialize this list to start, as fonts found will be appended to this
    fonts = []
    get_fonts(Path(__file__).parent.parent / "fonts", fonts)
    for font in fonts:
        fontDb.addApplicationFont(font)
