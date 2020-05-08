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
)

from library.lib import Library


class LeftPanel(QWidget):
    """
    Class holding the information that will go on the left sidebar.

    This will be the active tags.
    """

    def __init__(self, lib):
        QWidget.__init__(self)
        self.lib = lib

        self.layout = QVBoxLayout()
        for i in range(10):
            self.layout.addWidget(QLabel(f"Tag {i}"))

        self.setLayout(self.layout)


class CenterPanel(QWidget):
    """
    Panel that holds all the paper info
    """

    def __init__(self, lib):
        self.lib = lib
        QWidget.__init__(self)

        self.layout = QVBoxLayout()

        for b in lib.get_all_bibcodes():
            self.layout.addWidget(QLabel(b))

        self.setLayout(self.layout)


class RightPanel(QWidget):
    def __init__(self, lib):
        QWidget.__init__(self)
        self.lib = lib

        # Then right has the details on a given paper
        self.layout = QVBoxLayout()
        # We'll have many items, which we need to keep track of so we can modify them
        self.title = QLabel("Title")
        self.authors = QLabel("Authors")

        # then add them to the layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.authors)

        # add dummy junk for now
        for i in range(20):
            self.layout.addWidget(QLabel(f"Attribute {i}"))

        self.setLayout(self.layout)


class MainBodyWidget(QSplitter):
    """
    This class contains the main body, where we hold the papers and the info about them.
    """

    def __init__(self, lib):
        QSplitter.__init__(self)

        # In the place where we view papers, we want a three panel interface. The left
        # panel will show tags and other things the user can use to find papers. The
        # center panel will show a list of papers. The right panel will show info
        # about the paper the user has selected. Since these are laid out left to right,
        # we use the horizontal box layout. Splitter automatically does this.

        # get the widgets that will be put in here
        self.left = LeftPanel(lib)
        self.center = CenterPanel(lib)
        self.right = RightPanel(lib)

        # We want to add a scrollbar around all of these, so that we can scroll through
        # the tags, papers, info, etc.
        self.leftScroll = QScrollArea()
        self.leftScroll.setWidget(self.left)
        self.leftScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.centerScroll = QScrollArea()
        self.centerScroll.setWidget(self.center)
        self.centerScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.rightScroll = QScrollArea()
        self.rightScroll.setWidget(self.right)
        self.rightScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Then we can add these scroll objects to our layout
        self.addWidget(self.leftScroll)
        self.addWidget(self.centerScroll)
        self.addWidget(self.rightScroll)


class SearchWidget(QWidget):
    """
    This class is the search bar, where the use can put in URLs to search ADS
    """

    def __init__(self, lib):
        QWidget.__init__(self)
        self.lib = lib
        # This is all dummy for now. But I suspect we'll want some kind of horizontal
        # layout: the search bar and maybe a "Search" button.
        self.input = QLineEdit()
        self.input.setPlaceholderText("Default Text Here")

        self.addButton = QPushButton("Add")
        self.addButton.clicked.connect(self.addPaper)

        layout = QHBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.addButton)
        self.setLayout(layout)
        self.setFixedHeight(50)

    def addPaper(self):
        identifier = self.input.text()

        self.lib.add_paper(identifier)


class MainWindow(QMainWindow):
    def __init__(self, lib):
        QMainWindow.__init__(self)

        # Start with the layout. Our main layout is two vertical components:
        # the first is the search bar, where the user can paste URLs to add to the l
        # library, and the second is the place where we show all the papers that have
        # been added.
        layout = QVBoxLayout()

        self.searchBar = SearchWidget(lib)
        self.mainBody = MainBodyWidget(lib)
        self.title = QLabel("Library")

        # Mess around with the title formatting
        self.title.setFixedHeight(60)
        self.title.setAlignment(Qt.AlignCenter)
        newFont = QtGui.QFont("Lobster", 40)
        self.title.setFont(newFont)

        layout.addWidget(self.title)
        layout.addWidget(self.searchBar)
        layout.addWidget(self.mainBody)

        # We then have to have a dummy widget to act as the central widget. All that
        # is done here is setting the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Then let's set up a menu.
        self.menu = self.menuBar()
        # have the file option
        self.file_menu = self.menu.addMenu("File")

        # Things to go in the menu
        # Calling the Quit command can't be used, as it is caught by MacOS somehow
        # I'll use "close" instead
        exitAction = QAction("Close", self)
        exitAction.setShortcut("Ctrl+Q")
        # have to connect this to a function to actually do something
        exitAction.triggered.connect(QApplication.quit)

        # Then add all items to the menu
        self.file_menu.addAction(exitAction)

        # Set the window title
        self.setWindowTitle("")


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


if __name__ == "__main__":
    if len(sys.argv) == 1:  # no specified path
        db_path = Path("../USER_DATA_DO_NOT_DELETE.db")
    else:
        db_path = Path(sys.argv[1])
    lib = Library(db_path)

    # The application is what starts QT
    app = QApplication()

    # then add all our fonts
    fontDb = QtGui.QFontDatabase()
    # we need to initialize this list to start, as fonts found will be appended to this
    fonts = []
    get_fonts(Path(__file__).parent.parent / "fonts", fonts)
    for font in fonts:
        fontDb.addApplicationFont(font)

    # The MainWindow class holds all the structure
    window = MainWindow(lib)
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec_())
