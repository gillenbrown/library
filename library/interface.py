from pathlib import Path

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import (
    QKeySequence,
    QFontDatabase,
    QFont,
    QDesktopServices,
    QGuiApplication,
    QAction,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
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


def qss_trigger(object, property, value):
    """
    Trigger a change in QSS by setting a property and redrawing the object.

    :param object: Qt object to change the properties of
    :type object: QWidget
    :param property: The name of the property to set. This needs to match what is
                     set in the QSS file (e.g. Paper[is_highlighted=false]{...}
                     would use `is_highlighted` here and False for `value`
    :type property: str
    :param value: The value to set for the given property
    :return: None
    """
    object.setProperty(property, value)
    object.style().unpolish(object)
    object.style().polish(object)


class LeftPanelTag(QLabel):
    """
    Class holding a tag that goes in the left panel
    """

    def __init__(self, tagName, papersList, tagsList):
        """
        Initialize a tag that goes in the left panel.

        We need to get the papersList so that we can hide papers when a user clicks
        on a tag.

        :param tagName: Name of the tag to show.
        :type tagName: str
        :param papersList: Papers list objects
        :type papersList: PapersListScrollArea
        :param tagsList: The parent list of tags.
        :type tagsList: TagsListScrollArea
        """
        QLabel.__init__(self, tagName)
        self.name = tagName
        self.papersList = papersList
        self.tagsList = tagsList
        # this starts unhighlighted
        self.unhighlight()

    def mousePressEvent(self, _):
        """
        When the tag is clicked on, show the papers with that tag in the central panel

        :param _: Dummy parameter that contains the event type. Not used here, we do
                  the same thing for every click type.
        :return: None
        """
        for paper in self.papersList.papers:
            if self.name in paper.getTags():
                paper.show()
            else:
                paper.hide()

        # Visually highlight this tag, and remove highlighting on other tags
        for tag in self.tagsList.tags:
            tag.unhighlight()
        self.tagsList.showAllButton.unhighlight()
        self.highlight()

    def highlight(self):
        """
        Visually highlight this tag

        :return: None
        """
        qss_trigger(self, "is_highlighted", True)

    def unhighlight(self):
        """
        Remove the visual highlighting for this tag

        :return: None
        """
        qss_trigger(self, "is_highlighted", False)


class LeftPanelTagShowAll(LeftPanelTag):
    def __init__(self, papersList, tagsList):
        """
        Create the button to show all papers, regardless of tag

        :param papersList: Papers list objects
        :type papersList: PapersListScrollArea
        :param tagsList: The parent list of tags.
        :type tagsList: TagsListScrollArea
        """
        super().__init__("All Papers", papersList, tagsList)
        # this starts highlighted
        self.highlight()

    def mousePressEvent(self, _):
        """
        When this is clicked on, show all papers

        :return: None
        """
        for paper in self.papersList.papers:
            paper.show()
        # Visually highlight this tag, and remove highlighting on other tags
        for tag in self.tagsList.tags:
            tag.unhighlight()
        self.highlight()


class Paper(QWidget):
    """
    Class holding paper details that goes in the central panel
    """

    def __init__(self, bibcode, db, rightPanel, papersList):
        """
        Initialize the paper object, which will hold the given bibcode

        :param bibcode: Bibcode of this paper
        :type bibcode: str
        :param db: Database object this interface is using
        :type db: library.database.Database
        :param rightPanel: rightPanel object of this interface. This is only needed so
                           we can call the update feature when this is clicked on
        :type rightPanel: rightPanel
        :param papersList: The list of papers that this paper will be added to. This is
                           needed so we can unhighlight all other papers when one is
                           selected
        :type papersList: PapersListScrollArea
        """
        QWidget.__init__(self)

        # store the information that will be needed later
        self.bibcode = bibcode
        self.db = db
        self.rightPanel = rightPanel
        self.papersList = papersList

        # make sure this paper is actually in the database. This should never happen, but
        # might if I do something dumb in tests
        assert self.bibcode in self.db.get_all_bibcodes()

        # Then set up the layout this uses. It will be vertical with the title (for now)
        vBox = QVBoxLayout()
        self.titleText = QLabel(self.db.get_paper_attribute(self.bibcode, "title"))
        self.citeText = QLabel(self.db.get_cite_string(self.bibcode))

        # name these for stylesheets
        self.titleText.setObjectName("center_panel_paper_title")
        self.citeText.setObjectName("center_panel_cite_string")

        # make sure the paper is unhighlighted. This first thing ensures that changes
        # are actually shown in the interface. Not sure why this is not automatically
        # set
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.unhighlight()

        # then add these to the layout, then set this layout
        vBox.addWidget(self.titleText)
        vBox.addWidget(self.citeText)
        self.setLayout(vBox)
        self.layout().setSpacing(2)

    def mousePressEvent(self, event):
        """
        Handle the clicks - single click will display details, double will open paper

        :param event: Mouse click event object
        :type event: PySide2.QtGui.QMouseEvent
        :return: None
        """
        if event.type() is QEvent.Type.MouseButtonPress:
            # Pass the bibcode on to the right panel
            self.rightPanel.setPaperDetails(self.bibcode)
            # unhighlight all papers
            for paper in self.papersList.papers:
                paper.unhighlight()
            # then highlight this paper
            self.highlight()

        elif event.type() is QEvent.Type.MouseButtonDblClick:
            local_file = self.db.get_paper_attribute(self.bibcode, "local_file")
            if local_file is None:
                # if there is not a paper, we need to add it
                # the file dialog returns a two item tuple, where the first item is the
                # file name and the second is the filter. This is true whether the user
                # selects something or not. Contrary to the documentation, if the user
                # hits cancel it returns a two item tuple with two empty strings!
                local_file = QFileDialog.getOpenFileName(filter="PDF(*.pdf)")[0]
                # If the user doesn't select anything this returns the empty string.
                # Otherwise this returns a two item tuple, where the first item is the
                # absolute path to the file they picked
                if local_file != "":
                    self.db.set_paper_attribute(self.bibcode, "local_file", local_file)
                    # we'll open this file in a minute
                else:
                    # the user didn't pick anything, so don't open anything
                    return
            # if we now have a path, open the file. We get here whether we had to ask
            # the user or now
            QDesktopServices.openUrl(f"file:{local_file}")
        # nothing should be done for other click types

    def getTags(self):
        """
        Return the list of tags this paper has. This is used by the tags list.

        :return: List of tags
        :rtype: list
        """
        return self.db.get_paper_tags(self.bibcode)

    def highlight(self):
        """
        Visually highlight this paper in the interface

        :return: None
        """
        qss_trigger(self, "is_highlighted", True)
        qss_trigger(self.titleText, "is_highlighted", True)
        qss_trigger(self.citeText, "is_highlighted", True)

    def unhighlight(self):
        """
        Remove visual highlighting froom this paper in the interface

        :return: None
        """
        qss_trigger(self, "is_highlighted", False)
        qss_trigger(self.titleText, "is_highlighted", False)
        qss_trigger(self.citeText, "is_highlighted", False)


class TagCheckBox(QCheckBox):
    """
    Class for the Tag checkboxes that will go in the right panel.

    This is only needed as a separate class to implement the changeState correctly.
    """

    def __init__(self, text, rightPanel):
        """
        Create this tag Checkbox, with given text and belonging to some RightPanel.

        :param text: Label to show up next to this checkbox
        :type text: str
        :param rightPanel: Right Panel this checkbox belongs to.
        :type rightPanel: RightPanel
        """
        QCheckBox.__init__(self, text)
        self.rightPanel = rightPanel
        self.stateChanged.connect(self.changeState)

    def changeState(self):
        """
        Changes the tags of a paper by calling the method in the rightPanel

        :return: None
        """
        self.rightPanel.changeTags(self.text(), self.isChecked())


class RightPanel(QWidget):
    """
    The right panel area for the main window, holding paper info for a single paper
    """

    def __init__(self, db):
        """
        Initialize the right panel.

        :param db: Database object this interface is using
        :type db: library.database.Database
        """
        QWidget.__init__(self)

        self.db = db
        self.bibcode = ""  # will be set later
        self.papersList = None  # will be set by the papersList initializer, which
        # will have this passed in to it

        # This widget will have several main areas, all laid out vertically
        vBox = QVBoxLayout()

        # for clarity set text to empty, the default values will be set below
        self.titleText = QLabel("")
        self.citeText = QLabel("")
        self.abstractText = QLabel("")
        self.copyBibtexButton = QPushButton("Copy Bibtex entry to clipboard")
        self.firstDeletePaperButton = QPushButton("Delete this paper")
        self.secondDeletePaperButton = QPushButton("Confirm deletion of this paper")
        self.secondDeletePaperButton.setProperty("delete_button", True)  # style
        self.secondDeletePaperCancelButton = QPushButton(
            "Oops, don't delete this paper"
        )
        self.secondDeletePaperCancelButton.setProperty("delete_cancel_button", True)
        self.tagText = QLabel("")
        # set names for use with stylesheets
        self.titleText.setObjectName("right_panel_paper_title")
        self.citeText.setObjectName("right_panel_cite_text")
        self.abstractText.setObjectName("right_panel_abstract_text")
        self.tagText.setObjectName("right_panel_tagText")

        # have buttons to hide and show the list of tag checkboxes
        self.editTagsButton = QPushButton("Edit Tags")
        self.doneEditingTagsButton = QPushButton("Done Editing Tags")
        # then add their functionality when clicked
        self.editTagsButton.clicked.connect(self.enableTagEditing)
        self.doneEditingTagsButton.clicked.connect(self.doneTagEditing)
        self.copyBibtexButton.clicked.connect(self.copyBibtex)
        self.firstDeletePaperButton.clicked.connect(self.revealSecondDeleteButton)
        self.secondDeletePaperButton.clicked.connect(self.deletePaper)
        self.secondDeletePaperCancelButton.clicked.connect(self.resetDeleteButtons)

        # handle the initial state
        self.resetPaperDetails()

        # the Tags List has a bit of setup
        self.tags = []  # store the tags that are in there
        self.vBoxTags = QVBoxLayout()
        self.populate_tags()

        self.titleText.setWordWrap(True)
        self.citeText.setWordWrap(True)
        self.abstractText.setWordWrap(True)
        self.tagText.setWordWrap(True)

        # add these to the layout
        vBox.addWidget(self.titleText)
        vBox.addWidget(self.citeText)
        vBox.addWidget(self.abstractText)
        vBox.addWidget(self.copyBibtexButton)
        vBox.addWidget(self.tagText)
        vBox.addWidget(self.editTagsButton)
        vBox.addWidget(self.doneEditingTagsButton)
        vBox.addLayout(self.vBoxTags)
        vBox.addWidget(self.firstDeletePaperButton)
        vBox.addWidget(self.secondDeletePaperButton)
        vBox.addWidget(self.secondDeletePaperCancelButton)

        self.setLayout(vBox)

    def populate_tags(self):
        """
        Reset the list of tags shown in the right panel, to account for any new ones

        :return: None
        """
        # first clean up the current tags, make sure they're gone from the interface
        for t in self.tags:
            t.hide()
            del t
        self.tags = []
        # go through the database and add checkboxes for each tag there.
        for t in self.db.get_all_tags():
            this_tag_checkbox = TagCheckBox(t, self)
            self.tags.append(this_tag_checkbox)
            self.vBoxTags.addWidget(this_tag_checkbox)
            # hide all tags at the beginning
            this_tag_checkbox.hide()

    def resetPaperDetails(self):
        """
        Set the details in the right panel to be the default when no paper is shown

        :return: None, but the text properties are set
        """
        self.titleText.setText("")
        self.citeText.setText("")
        self.abstractText.setText("Click on a paper to show its details here")
        self.tagText.setText("")

        # all of the buttons
        self.editTagsButton.hide()
        self.doneEditingTagsButton.hide()
        self.copyBibtexButton.hide()
        self.firstDeletePaperButton.hide()
        self.secondDeletePaperButton.hide()
        self.secondDeletePaperCancelButton.hide()

    def setPaperDetails(self, bibcode):
        """
        Update the details shown in the right panel.

        :param bibcode: Bibcode of the paper. The bibcode will not appear, but it will
                        be used to query the details from the database.
        :type bibcode: str
        :return: None, but the text properties are set.
        """
        self.bibcode = bibcode
        self.titleText.setText(self.db.get_paper_attribute(self.bibcode, "title"))
        self.citeText.setText(self.db.get_cite_string(self.bibcode))
        self.abstractText.setText(self.db.get_paper_attribute(self.bibcode, "abstract"))
        self.update_tag_text()

        # Go through and set the checkboxes to match the tags the paper has
        self.populate_tags()
        for tag in self.tags:
            tag.hide()
            if tag.text() in self.db.get_paper_tags(self.bibcode):
                tag.setChecked(True)
            else:
                tag.setChecked(False)

        # then make the edit tags and copy Bibtex buttons appear, since they will be
        # hidden at the start
        self.editTagsButton.show()
        self.doneEditingTagsButton.hide()
        self.copyBibtexButton.show()
        self.firstDeletePaperButton.show()
        # also hide the second button if it was shown
        self.secondDeletePaperButton.hide()
        self.secondDeletePaperCancelButton.hide()

    def update_tag_text(self):
        """
        Put the appropriate tags in the list of tags this paper has

        :return: None
        """
        tags_list = self.db.get_paper_tags(self.bibcode)
        self.tagText.setText(f"Tags: {', '.join(tags_list)}")

    def enableTagEditing(self):
        """
        Show the tag selection boxes and the done editing button.

        Inverse of `doneTagEditing`

        :return: None
        """
        self.editTagsButton.hide()
        self.doneEditingTagsButton.show()
        for tag in self.tags:
            tag.show()

    def doneTagEditing(self):
        """
        Hide the tag selection boxes and the done editing button.

        Inverse of `enableTagEditing`

        :return: None
        """
        self.editTagsButton.show()
        self.doneEditingTagsButton.hide()
        for tag in self.tags:
            tag.hide()
        # Also update the text shown to the user
        self.update_tag_text()

    def changeTags(self, tagName, checked):
        """
        Add or remove tag to the paper in the panel right now

        :param tagName: The tag that was checked or unchecked.
        :type tagName: str
        :param checked: Whether the tag was added (True) or removed (False)
        :type checked: bool
        :return: None
        """
        if checked:
            self.db.tag_paper(self.bibcode, tagName)
        else:
            self.db.untag_paper(self.bibcode, tagName)

    def copyBibtex(self):
        """
        Put the text from the selected paper's Bibtex entry into the clipboard

        :return: None, but the text is copied to the clipboard
        :rtype: None
        """
        this_bibtex = self.db.get_paper_attribute(self.bibcode, "bibtex")
        QGuiApplication.clipboard().setText(this_bibtex)

    def revealSecondDeleteButton(self):
        """
        Hides the first delete button, reveals the second

        :return: None, but the buttons are shifted
        """
        self.firstDeletePaperButton.hide()
        self.secondDeletePaperButton.show()
        self.secondDeletePaperCancelButton.show()

    def resetDeleteButtons(self):
        """
        Returns the delete buttons to their original state

        :return:
        """
        self.firstDeletePaperButton.show()
        self.secondDeletePaperButton.hide()
        self.secondDeletePaperCancelButton.hide()

    def deletePaper(self):
        """
        Delete this paper from the database

        :return: None, but the paper is deleted and text reset
        """
        self.db.delete_paper(self.bibcode)
        self.resetPaperDetails()  # clean up right panel
        self.papersList.deletePaper(self.bibcode)  # remove this frm the center panel


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

    def __init__(self, db, rightPanel):
        """
        Set up the papers list

        Stores the database and right panel, which are used by the paper objects
        themselves

        :param db: Database object this interface is using
        :type db: library.database.Database
        :param rightPanel: rightPanel object of this interface. This is only needed so
                           we can call the update feature when this is clicked on
        :type rightPanel: rightPanel
        """
        ScrollArea.__init__(self)
        self.papers = []

        self.rightPanel = rightPanel
        self.db = db
        rightPanel.papersList = self

    def addPaper(self, bibcode):
        """
        Add a paper to the papers scroll area.

        This adds it to the internal list of papers and puts the widget in the interface

        :param bibcode: Bibcode of the paper to be added
        :type bibcode: str
        :return: None
        """
        # check if this paper is already in the list. This should never happen
        assert bibcode not in [p.bibcode for p in self.papers]

        # create the paper object, than add to the list and center panel
        paper = Paper(bibcode, self.db, self.rightPanel, self)
        self.papers.append(paper)
        self.addWidget(paper)  # calls the ScrollArea addWidget

    def deletePaper(self, bibcode):
        """
        Delete a paper from this list of papers

        :param bibcode: Bibcode of the paper to delete
        :return: None, but the paper is deleted from the list
        """
        for paper in self.papers:
            if paper.bibcode == bibcode:
                paper.hide()  # just to be safe
                self.papers.remove(paper)
                del paper


class TagsListScrollArea(ScrollArea):
    """
    The class to be used for the left hand side list of tags.

    It's just a ScrollArea that keeps track of the tags that have been added, almost
    identical to PapersListScrollArea, except that it has a text area to add tags, and
    a button to show all papers.
    """

    def __init__(
        self,
        addTagButton,
        addTagBar,
        papersList,
        firstDeleteTagButton,
        secondDeleteTagEntry,
        thirdDeleteTagButton,
        thirdDeleteTagCancelButton,
    ):
        """
        Set up the papers list, no parameters needed
        """
        ScrollArea.__init__(self)
        self.tags = []
        self.addTagButton = addTagButton
        self.addTagBar = addTagBar
        self.papersList = papersList

        # Make the button to show all the papers in the list
        self.showAllButton = LeftPanelTagShowAll(papersList, self)

        # put the tag bar at the top of the list
        self.addWidget(self.addTagButton)  # calls ScrollArea addWidget
        self.addWidget(self.addTagBar)
        self.addWidget(firstDeleteTagButton)
        self.addWidget(secondDeleteTagEntry)
        self.addWidget(thirdDeleteTagButton)
        self.addWidget(thirdDeleteTagCancelButton)
        self.addWidget(self.showAllButton)

    def addTag(self, tag):
        """
        Add a tag to the tags scroll area.

        This adds it to the internal list of tags and puts the widget in the interface

        :param tag: Tag object to be added to the list of stored tags.
        :type tag: LeftPanelTag
        :return: None
        """
        # check if this tag is already in the list. This should never happen
        assert tag.name not in [t.name for t in self.tags]

        self.tags.append(tag)
        self.addWidget(tag)  # calls the ScrollArea addWidget


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

        # Set up default stylesheets
        with open(Path(__file__).parent / "style.qss", "r") as style_file:
            self.setStyleSheet(style_file.read())

        self.db = db

        # add read and unread tags if there is nothing in the database
        if len(self.db.get_all_bibcodes()) == 0 and len(self.db.get_all_tags()) == 0:
            db.add_new_tag("Read")
            db.add_new_tag("Unread")

        # Start with the layout. Our main layout is three vertical components:
        # the first is the title, second is the search bar, where the user can paste
        # URLs to add to the database, and the third is the place where we show all
        # the papers that have been added.
        vBoxMain = QVBoxLayout()

        # The title is first
        self.title = QLabel("Library")
        self.title.setObjectName("big_title")
        # Mess around with the title formatting
        self.title.setFixedHeight(60)
        self.title.setAlignment(Qt.AlignCenter)
        vBoxMain.addWidget(self.title)

        # Then comes the search bar. This is it's own horizontal layout, with the
        # text box and the button to add
        hBoxSearchBar = QHBoxLayout()
        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Enter your paper URL or ADS bibcode here")
        self.searchBar.setProperty("error", False)
        # and have some text if there's an error
        self.searchBarErrorText = QLabel()
        self.searchBarErrorText.setObjectName("search_error_text")
        self.searchBarErrorText.hide()
        # We'll also have an add button
        self.addButton = QPushButton("Add")
        self.addButton.setObjectName("add_button")
        # Define what to do when these things are activated. The user can either hit
        # enter or hit the add button
        self.searchBar.returnPressed.connect(self.addPaper)
        self.addButton.clicked.connect(self.addPaper)
        # also allow the reset after an error
        self.searchBar.cursorPositionChanged.connect(self.resetSearchBarError)
        self.searchBar.textChanged.connect(self.resetSearchBarError)
        # have both of these quantities have a fixed height. These values are chosen to
        # make it look nice. They aren't the same size since the bounding boxes aren't
        # quite the same relative to the shown borders for whatever reason
        self.searchBar.setFixedHeight(30)
        self.addButton.setFixedHeight(35)
        # Then add these to the layouts
        hBoxSearchBar.addWidget(self.searchBar)
        hBoxSearchBar.addWidget(self.searchBarErrorText)
        hBoxSearchBar.addWidget(self.addButton)
        vBoxMain.addLayout(hBoxSearchBar)

        # Then we have the main body. This is a bit more complex. We'll start by just
        # initializing the layout for this, which is three panels laid horizonatlly.
        # This is the default splitter orientation
        splitter = QSplitter()
        # then make each of these things

        # The right panel is the details on a given paper. It holds the tags list,
        # which we need to initialize first
        self.rightPanel = RightPanel(self.db)
        rightScroll = ScrollArea()
        rightScroll.addWidget(self.rightPanel)

        # The central panel is the list of papers. This has to be set up after the
        # right panel because the paper objects need it, and before the left panel
        # because the tags need this panel
        self.papersList = PapersListScrollArea(db, self.rightPanel)
        for b in self.db.get_all_bibcodes():
            self.papersList.addPaper(b)

        # The left panel of this is the list of tags the user has, plus the button to
        # add papers, which will go at the top of that list. This has to go after the
        # center panel since the tags need to access the paper list
        self.addTagButton = QPushButton("Add a tag")
        self.addTagButton.clicked.connect(self.showAddTagBar)
        self.addTagBar = QLineEdit()
        self.addTagBar.setPlaceholderText("Tag name")
        self.addTagBar.returnPressed.connect(self.addTag)
        self.addTagBar.hide()

        # Then set up the buttons to remove tags. We'll have four buttons. The first
        # will be a button to click to start the process of deleting a tag. Next
        # will be a text entry box for the user to specify which tag to delete, then
        # a confirm and cancel button
        self.firstDeleteTagButton = QPushButton("Delete a tag")
        self.firstDeleteTagButton.clicked.connect(self.revealSecondTagDeleteEntry)

        self.secondDeleteTagEntry = QLineEdit()
        self.secondDeleteTagEntry.setPlaceholderText("Tag to delete")
        self.secondDeleteTagEntry.returnPressed.connect(
            self.revealThirdTagDeleteButtons
        )
        self.secondDeleteTagEntry.hide()

        self.thirdDeleteTagButton = QPushButton("")
        self.thirdDeleteTagButton.clicked.connect(self.confirmTagDeletion)
        self.thirdDeleteTagButton.setProperty("delete_button", True)  # for style
        self.thirdDeleteTagButton.hide()

        self.thirdDeleteTagCancelButton = QPushButton("")
        self.thirdDeleteTagCancelButton.clicked.connect(self.cancelTagDeletion)
        self.thirdDeleteTagCancelButton.setProperty("delete_cancel_button", True)
        self.thirdDeleteTagCancelButton.hide()

        # Then set up the final tagsList object
        self.tagsList = TagsListScrollArea(
            self.addTagButton,
            self.addTagBar,
            self.papersList,
            self.firstDeleteTagButton,
            self.secondDeleteTagEntry,
            self.thirdDeleteTagButton,
            self.thirdDeleteTagCancelButton,
        )
        for t in self.db.get_all_tags():
            self.tagsList.addTag(LeftPanelTag(t, self.papersList, self.tagsList))

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
            # show the error message, and change formatting. Leave the text
            self.searchBarErrorText.setText(
                "This paper was not found in ADS. "
                "If it was just added to the arXiv, "
                "ADS may not have registered it."
            )
            self.searchBarErrorText.show()
            qss_trigger(self.searchBar, "error", True)
            return
        except PaperAlreadyInDatabaseError:
            # here we do clear the search bar, but do not add the paper
            self.searchBar.clear()
            return

        # we only get here if the addition to the database worked. If so we add the
        # paper object, then clear the search bar
        self.papersList.addPaper(bibcode)
        # clear the text so another paper can be added
        self.searchBar.clear()

    def resetSearchBarError(self):
        """
        After an error, reset the search bar formatting to the original state

        :return: None
        """
        qss_trigger(self.searchBar, "error", False)
        self.searchBarErrorText.hide()

    def showAddTagBar(self):
        """
        When the add tag button is clicked, hide that and show the text entry bar

        :return: None
        """
        self.addTagButton.hide()
        self.addTagBar.show()

    def addTag(self):
        """
        Adds a tag to the database, taking the name from the text box.

        The text will be cleared if the tag was successfully added, which will only not
        be the case if the tag is already in the database.

        :return: None
        """
        #
        try:
            tagName = self.addTagBar.text()
            self.db.add_new_tag(tagName)
            self.tagsList.addTag(LeftPanelTag(tagName, self.papersList, self.tagsList))
        except ValueError:  # this tag is already in the database
            return

        # if we got here we had no error, so it was successfully added and we should
        # clear the text box and reset the buttons
        self.addTagBar.clear()
        self.addTagBar.hide()
        self.addTagButton.show()

    def revealSecondTagDeleteEntry(self):
        """
        When the tag delete button is pressed, hide the button and reveal the text entry

        :return: None
        """
        self.firstDeleteTagButton.hide()
        self.secondDeleteTagEntry.show()

    def revealThirdTagDeleteButtons(self):
        """
        When the tag deletion entry is entered, figure out what to do.

        If the entry is a valid tag, show the next two buttons. Otherwise reset it.
        :return: None
        """
        # check that the entered text is valid. If not, reset
        tag_to_delete = self.secondDeleteTagEntry.text()
        if tag_to_delete not in self.db.get_all_tags():
            self.cancelTagDeletion()
            return
        # if it is valid, show the next button and put the appropriate text on them
        self.secondDeleteTagEntry.hide()
        self.thirdDeleteTagButton.show()
        self.thirdDeleteTagButton.setText(
            f'Click to confirm deletion of tag "{tag_to_delete}"'
        )
        self.thirdDeleteTagCancelButton.show()
        self.thirdDeleteTagCancelButton.setText(
            "Oops, don't delete tag " + f'"{tag_to_delete}"'
        )

    def confirmTagDeletion(self):
        """
        Delete a tag from the database

        This assumes that the text in the secondDeleteTagEntry is a valid tag. That
        should be error checked previously, as we shouldn't let the user confirm the
        deletion of an invalid tag.

        :return: None
        """
        tag_to_delete = self.secondDeleteTagEntry.text()
        # delete from database
        self.db.delete_tag(tag_to_delete)
        # find the tag to remove it from the interface
        for tag in self.tagsList.tags:
            if tag.text() == tag_to_delete:
                tag.hide()  # just to be safe
                self.tagsList.tags.remove(tag)
                del tag
        # then reset the boxes
        self.cancelTagDeletion()

    def cancelTagDeletion(self):
        """
        Reset the tag cancel buttons.

        This can be done after deleting a tag or if that deletion is cancelled, since
        in either version we want to reset the buttons.

        :return: None
        """
        self.firstDeleteTagButton.show()
        self.secondDeleteTagEntry.hide()
        self.secondDeleteTagEntry.setText("")
        self.thirdDeleteTagButton.hide()
        self.thirdDeleteTagCancelButton.hide()


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
    # we need to initialize this list to start, as fonts found will be appended to this
    fonts = []
    get_fonts(Path(__file__).parent.parent / "fonts", fonts)
    for font in fonts:
        QFontDatabase.addApplicationFont(font)
