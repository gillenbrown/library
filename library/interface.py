from pathlib import Path
import requests

import ads.exceptions
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import (
    QKeySequence,
    QFontDatabase,
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
    QTextEdit,
    QPushButton,
    QLayout,
    QFileDialog,
    QCheckBox,
    QFrame,
    QComboBox,
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


class LeftPanelTag(QWidget):
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
        QWidget.__init__(self)
        # this contains two parts: a tag name, then a button to export
        self.label = QLabel(tagName)
        self.label.setProperty("is_tag", True)
        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.export)
        self.exportButton.setProperty("export_button", True)
        # add these to a layout
        hBox = QHBoxLayout()
        hBox.addWidget(self.label)
        hBox.addWidget(self.exportButton)
        hBox.setContentsMargins(5, 5, 5, 5)
        self.setLayout(hBox)

        # also store some other info
        self.name = tagName
        self.papersList = papersList
        self.tagsList = tagsList
        # make sure the tag is unhighlighted. This first thing ensures that changes
        # are actually shown in the interface. Not sure why this is not automatically
        # set
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.unhighlight()

        # set the height to be a fixed value, so it doesn't change when highlighted
        self.setFixedHeight(self.sizeHint().height() + 2)

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
        qss_trigger(self.label, "is_highlighted", True)
        self.exportButton.show()

    def unhighlight(self):
        """
        Remove the visual highlighting for this tag

        :return: None
        """
        qss_trigger(self, "is_highlighted", False)
        qss_trigger(self.label, "is_highlighted", False)
        self.exportButton.hide()

    def export(self):
        """
        Export the papers with this tag to a bibtex file.

        The user will be prompted to pick the file, then we'll write the bibtex file
        here.

        :return: None
        """
        # the file dialog returns a two item tuple, where the first item is the
        # file name and the second is the filter. This is true whether the user
        # selects something or not. Contrary to the documentation, if the user
        # hits cancel it returns a two item tuple with two empty strings!
        local_file = QFileDialog.getSaveFileName(
            caption="Select where to save this file", dir=str(Path.home())
        )[0]
        # if the user did not select anything, return.
        if local_file == "":
            return
        # otherwise, do the export. We do need to parse the tags a bit
        if self.name == "All Papers":
            label = "all"
        else:
            label = self.name

        self.papersList.db.export(label, Path(local_file))


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
        # and let the text wrap
        self.titleText.setWordWrap(True)
        self.citeText.setWordWrap(True)

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
        self.layout().setContentsMargins(10, 10, 0, 10)

    def mousePressEvent(self, event):
        """
        Handle the clicks - single click will display details, double will open paper

        :param event: Mouse click event object
        :type event: PySide2.QtGui.QMouseEvent
        :return: None
        """
        # No matter whether we have a single or double click, show the details in the
        # right panel. If we have a double click, we'll open the paper pdf.

        # Pass the bibcode on to the right panel
        self.rightPanel.setPaperDetails(self.bibcode)
        # unhighlight all papers
        for paper in self.papersList.papers:
            paper.unhighlight()
        # then highlight this paper
        self.highlight()

        if event.type() is QEvent.Type.MouseButtonDblClick:
            self.rightPanel.validatePDFPath()
            local_file = self.db.get_paper_attribute(self.bibcode, "local_file")
            # local_file will either be None or an existing file
            # if there is no file, highlight for the user where they can add the file
            if local_file is None:
                self.rightPanel.highlightPDFButtons()
            else:
                # open the file. This function handles error checking
                self.rightPanel.openPDF()
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


class HorizontalLine(QFrame):
    def __init__(self):
        super(HorizontalLine, self).__init__()
        self.setFrameShape(QFrame.HLine)


class ScrollArea(QScrollArea):
    """
    A wrapper around QScrollArea with a vertical layout, appropriate for lists
    """

    def __init__(self, min_width, offset):
        """
        Setup the scroll area

        :param min_width: the minimum width for this widget, in pixels:
        :type min_width: int
        :param offset: the difference between the splitter size and the size of the
                       child widgets
        :type offset: int
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

        # have a minimum allowed width. This makes the splitter know to not decrease
        # below this size
        self.setMinimumWidth(min_width)
        # store the difference between the splitter size and what we want to set the
        # widget widths 10
        self.offset = offset

    def addWidget(self, widget):
        """
        Add a widget to the list of vertical objects

        :param widget: Widget to be added to the layout.
        :type widget: QWidget
        :return: None
        """
        # add the widget to the layout
        self.layout.addWidget(widget)

    def resizeEvent(self, resize_event):
        """
        Handle the resizing of the splitter, adjusting all child widgets too

        :param resize_event: the resizing event
        :type resize_event: QResizeEvent
        :return: None
        """
        # get the new size, and apply it to all widgets in the layout. Have some
        # padding on either size to avoid horizontal scroll bars
        new_width = resize_event.size().width() - self.offset
        self.resize_items_in_layout(self.layout, new_width)

        # Then do the normal resizing
        super().resizeEvent(resize_event)

    def resize_items_in_layout(self, layout, width):
        """
        Recursively resize all widgets within a layout

        Any widgets in this layout will be adjusted, while any other layouts will
        be sent to this function for them to be adjusted

        :param layout: The layout to be adjusted to a given width
        :type layout: QLayout
        :param width: the width to make each widget, in pixels
        :type width: int
        :return: None
        """
        for w_idx in range(0, layout.count()):
            item = layout.itemAt(w_idx)
            # if it's a layout, just adjust the width
            if item.widget() is not None:
                # leave room on the right for the padding
                item.widget().setFixedWidth(width)
            else:  # is a layout
                self.resize_items_in_layout(item.layout(), width)


class RightPanel(ScrollArea):
    """
    The right panel area for the main window, holding paper info for a single paper
    """

    def __init__(self, db):
        """
        Initialize the right panel.

        :param db: Database object this interface is using
        :type db: library.database.Database
        """
        super().__init__(min_width=250, offset=25)

        self.db = db
        self.bibcode = ""  # will be set later
        self.papersList = None  # will be set by the papersList initializer, which
        # will have this passed in to it

        # for clarity set text to empty, the default values will be set below
        self.titleText = QLabel("")
        self.citeText = QLabel("")
        self.abstractText = QLabel("")
        self.copyBibtexButton = QPushButton("Copy Bibtex entry to clipboard")
        self.adsButton = QPushButton("Open this paper in ADS")
        self.firstDeletePaperButton = QPushButton("Delete this paper")
        self.secondDeletePaperButton = QPushButton("Confirm deletion of this paper")
        self.secondDeletePaperButton.setProperty("delete_button", True)  # style
        self.secondDeletePaperCancelButton = QPushButton(
            "Oops, don't delete this paper"
        )
        self.secondDeletePaperCancelButton.setProperty("delete_cancel_button", True)
        self.tagText = QLabel("")
        self.userNotesText = QLabel("")
        self.userNotesTextEditButton = QPushButton("Edit Notes")
        self.userNotesTextEditField = QTextEdit()
        self.userNotesTextEditFinishedButton = QPushButton("Done Editing Notes")
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
        self.adsButton.clicked.connect(self.openADS)
        self.firstDeletePaperButton.clicked.connect(self.revealSecondDeleteButton)
        self.secondDeletePaperButton.clicked.connect(self.deletePaper)
        self.secondDeletePaperCancelButton.clicked.connect(self.resetDeleteButtons)
        self.userNotesTextEditButton.clicked.connect(self.editUserNotes)
        self.userNotesTextEditFinishedButton.clicked.connect(self.doneEditingUserNotes)

        # have buttons to edit the citation keyword
        self.citeKeyText = QLabel("")
        self.editCiteKeyButton = QPushButton("Edit Citation Keyword")
        self.editCiteKeyEntry = EasyExitLineEdit(
            self.resetCiteTextButtons, self.changeCiteKey
        )
        self.editCiteKeyEntry.setPlaceholderText("e.g. yourname_etal_2022")
        self.editCiteKeyErrorText = QLabel("")
        qss_trigger(self.editCiteKeyErrorText, "error_text", True)
        self.editCiteKeyButton.clicked.connect(self.revealCiteKeyEntry)

        # have buttons for the local PDF file
        self.pdfText = QLabel("")
        self.pdfOpenButton = QPushButton("Open this paper's PDF")
        self.pdfOpenButton.clicked.connect(self.openPDF)
        self.pdfChooseLocalFileButton = QPushButton("Choose a local PDF")
        self.pdfChooseLocalFileButton.clicked.connect(self.userChooseLocalPDF)
        self.pdfDownloadButton = QPushButton("Download the PDF")
        self.pdfDownloadButton.clicked.connect(self.downloadPDF)

        # have some horizontal lines to visually distinguish sections
        self.spacers = [HorizontalLine() for _ in range(5)]

        # the Tags List has a bit of setup
        self.tags = []  # store the tags that are in there
        self.vBoxTags = QVBoxLayout()
        self.populate_tags()

        # handle the initial state
        self.resetPaperDetails()

        self.titleText.setWordWrap(True)
        self.citeText.setWordWrap(True)
        self.abstractText.setWordWrap(True)
        self.tagText.setWordWrap(True)
        self.userNotesText.setWordWrap(True)
        self.pdfText.setWordWrap(True)
        self.citeKeyText.setWordWrap(True)

        # add these to the layout
        self.addWidget(self.titleText)
        self.addWidget(self.citeText)
        self.addWidget(self.abstractText)
        self.addWidget(self.spacers[0])
        self.addWidget(self.userNotesText)
        self.addWidget(self.userNotesTextEditField)
        self.addWidget(self.userNotesTextEditButton)
        self.addWidget(self.userNotesTextEditFinishedButton)
        self.addWidget(self.spacers[1])
        self.addWidget(self.pdfText)
        self.addWidget(self.pdfOpenButton)
        self.addWidget(self.pdfChooseLocalFileButton)
        self.addWidget(self.pdfDownloadButton)
        self.addWidget(self.spacers[2])
        self.addWidget(self.tagText)
        self.addWidget(self.editTagsButton)
        self.addWidget(self.doneEditingTagsButton)
        self.layout.addLayout(self.vBoxTags)
        self.addWidget(self.spacers[3])
        self.addWidget(self.citeKeyText)
        self.addWidget(self.editCiteKeyButton)
        self.addWidget(self.editCiteKeyErrorText)
        self.addWidget(self.editCiteKeyEntry)
        self.addWidget(self.copyBibtexButton)
        self.addWidget(self.spacers[4])
        self.addWidget(self.adsButton)
        self.addWidget(self.firstDeletePaperButton)
        self.addWidget(self.secondDeletePaperButton)
        self.addWidget(self.secondDeletePaperCancelButton)

    def populate_tags(self):
        """
        Reset the list of tags shown in the right panel, to account for any new ones.

        This checks checkboxes based on the paper currently shown, and hides or shows
        the checkboxes appropriately

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
            # see whether we can check this box
            if self.bibcode != "":
                if t in self.db.get_paper_tags(self.bibcode):
                    this_tag_checkbox.setChecked(True)
                else:
                    this_tag_checkbox.setChecked(False)

            # see whether to hide or show the tags
            if self.doneEditingTagsButton.isHidden():
                this_tag_checkbox.hide()
            else:
                this_tag_checkbox.show()

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
        self.pdfText.hide()
        self.pdfOpenButton.hide()
        self.pdfChooseLocalFileButton.hide()
        self.pdfDownloadButton.hide()
        self.editTagsButton.hide()
        self.doneEditingTagsButton.hide()
        self.populate_tags()  # this handles hiding the checkboxes
        self.userNotesText.hide()
        self.userNotesTextEditButton.hide()
        self.userNotesTextEditFinishedButton.hide()
        self.userNotesTextEditField.hide()
        self.copyBibtexButton.hide()
        self.adsButton.hide()
        self.firstDeletePaperButton.hide()
        self.secondDeletePaperButton.hide()
        self.secondDeletePaperCancelButton.hide()
        self.citeKeyText.hide()
        self.editCiteKeyButton.hide()
        self.editCiteKeyEntry.hide()
        self.editCiteKeyErrorText.hide()
        for spacer in self.spacers:
            spacer.hide()

    def setPaperDetails(self, bibcode):
        """
        Update the details shown in the right panel.

        :param bibcode: Bibcode of the paper. The bibcode will not appear, but it will
                        be used to query the details from the database.
        :type bibcode: str
        :return: None, but the text properties are set.
        """
        # if the user is clicking on the same paper we're already displaying, just exit
        if self.bibcode == bibcode:
            return
        self.bibcode = bibcode
        self.titleText.setText(self.db.get_paper_attribute(self.bibcode, "title"))
        self.citeText.setText(self.db.get_cite_string(self.bibcode))
        self.abstractText.setText(self.db.get_paper_attribute(self.bibcode, "abstract"))
        self.update_tag_text()
        self.updateNotesText()

        # then make all the buttons appear, since they will be hidden at the start
        self.unhighlightPDFButtons()
        self.pdfText.show()
        self.pdfDownloadButton.setText("Download the PDF")
        self.validatePDFPath()  # handles PDF buttons
        # tags
        self.editTagsButton.show()
        self.doneEditingTagsButton.hide()
        self.adsButton.show()
        self.firstDeletePaperButton.show()
        # also hide the second button if it was shown
        self.secondDeletePaperButton.hide()
        self.secondDeletePaperCancelButton.hide()
        # show the user notes
        self.userNotesText.show()
        self.userNotesTextEditButton.show()
        # and the bibtex buttons
        self.citeKeyText.show()
        cite_key = self.db.get_paper_attribute(self.bibcode, "citation_keyword")
        self.citeKeyText.setText(f"Citation Keyword: {cite_key}")
        self.editCiteKeyButton.show()
        self.copyBibtexButton.show()
        # and spacers
        for spacer in self.spacers:
            spacer.show()

        # Go through and set the checkboxes to match the tags the paper has. This
        # needs to be done after hiding everything so we can detect whether or not
        # to show the checkboxes
        self.populate_tags()

        # scroll to the top so the title is visible
        self.verticalScrollBar().setValue(0)
        self.horizontalScrollBar().setValue(0)

    def update_tag_text(self):
        """
        Put the appropriate tags in the list of tags this paper has

        :return: None
        """
        tags_list = self.db.get_paper_tags(self.bibcode)
        if len(tags_list) > 0:
            self.tagText.setText(f"Tags: {', '.join(tags_list)}")
        else:
            self.tagText.setText(f"Tags: None")

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

    def openADS(self):
        """
        Open the ADS page for this paper in the user's browser

        :return: None
        """
        QDesktopServices.openUrl(
            f"https://ui.adsabs.harvard.edu/abs/{self.bibcode}/abstract"
        )

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
        self.resetPaperDetails()  # clean up right panel
        self.papersList.deletePaper(self.bibcode)  # remove this frm the center panel
        self.db.delete_paper(self.bibcode)

    def updateNotesText(self):
        """
        Set the appropriate text for the user notes. Use default value if empty.

        :return: None
        """
        notes_text = self.db.get_paper_attribute(self.bibcode, "user_notes")
        if notes_text is None or len(notes_text.strip()) == 0:
            notes_text = "No notes yet"
        self.userNotesText.setText(notes_text)

    def editUserNotes(self):
        """
        Allow the user to edit their notes, by showing the text edit field

        :return: None
        """
        # set the text in the edit field to be the current user notes. Don't just copy
        # the text from the widget, since that may say "no notes yet" and I don't want
        # that to be in this text box
        self.userNotesTextEditField.setText(
            self.db.get_paper_attribute(self.bibcode, "user_notes")
        )
        # then show the appropriate buttons
        self.userNotesTextEditButton.hide()
        self.userNotesText.hide()
        self.userNotesTextEditField.show()
        self.userNotesTextEditFinishedButton.show()

    def doneEditingUserNotes(self):
        """
        The user is done editing text, so save their notes and reset the buttons

        :return: None
        """
        # save this info in the database
        text = self.userNotesTextEditField.toPlainText()
        self.db.set_paper_attribute(self.bibcode, "user_notes", text)
        # and put this text into the static text field
        self.updateNotesText()

        # reset buttons
        self.userNotesTextEditButton.show()
        self.userNotesText.show()
        self.userNotesTextEditField.hide()
        self.userNotesTextEditFinishedButton.hide()

    def revealCiteKeyEntry(self):
        """
        Show the entry area to change the paper's citation keyword

        :return: None
        """
        self.editCiteKeyButton.hide()
        self.editCiteKeyEntry.show()

    def resetCiteTextButtons(self):
        """
        Once the user is done editing the citation key, reset the buttons.

        :return: None
        """
        self.editCiteKeyEntry.hide()
        self.editCiteKeyEntry.setText("")
        self.editCiteKeyButton.show()
        self.editCiteKeyErrorText.hide()
        self.citeKeyText.show()

    def changeCiteKey(self):
        """
        Take the user's entry and update the citation keyword in the database

        :return: None
        """
        user_entry = self.editCiteKeyEntry.text()
        # try to add this, and then handle errors as needed
        try:
            self.db.set_paper_attribute(self.bibcode, "citation_keyword", user_entry)
        except ValueError:  # space in keyword
            self.editCiteKeyErrorText.setText("Spaces not allowed")
            self.editCiteKeyErrorText.show()
            return
        except RuntimeError:  # duplicate
            self.editCiteKeyErrorText.setText("Another paper already uses this")
            self.editCiteKeyErrorText.show()
            return

        # if it worked, reset the buttons and the text
        self.citeKeyText.setText(f"Citation Keyword: {user_entry}")
        self.resetCiteTextButtons()

    def validatePDFPath(self):
        """
        Checks that the current local_path to the PDF points to a real pdf

        Allowed values are None and existing files. If it is a non-existent pdf, the
        value will be replaced with None

        :return: None
        """
        local_file = self.db.get_paper_attribute(self.bibcode, "local_file")
        # if it does not exist, replace it
        if local_file is not None and not Path(local_file).is_file():
            self.db.set_paper_attribute(self.bibcode, "local_file", None)
            local_file = None

        # now we either have None or a valid file
        if local_file is None:
            self.pdfText.setText("No PDF location set")
            self.pdfOpenButton.hide()
            self.pdfChooseLocalFileButton.show()
            self.pdfDownloadButton.show()
        else:  # valid file
            self.pdfText.setText(f"PDF Location: {local_file}")
            self.pdfOpenButton.show()
            self.pdfChooseLocalFileButton.hide()
            self.pdfDownloadButton.hide()

    def userChooseLocalPDF(self):
        """
        Prompt the user to choose a PDF for this file

        :return: None
        """
        # unhighlight the box
        self.unhighlightPDFButtons()
        # if there is not a paper, we need to add it
        # the file dialog returns a two item tuple, where the first item is the
        # file name and the second is the filter. This is true whether the user
        # selects something or not. Contrary to the documentation, if the user
        # hits cancel it returns a two item tuple with two empty strings!
        local_file = QFileDialog.getOpenFileName(
            filter="PDF(*.pdf)",
            dir=str(Path.home()),
        )[0]
        # If the user doesn't select anything this returns the empty string.
        # Otherwise this returns a two item tuple, where the first item is the
        # absolute path to the file they picked
        if local_file != "":
            self.db.set_paper_attribute(self.bibcode, "local_file", local_file)
            self.validatePDFPath()  # handles buttons and whatnot

    def openPDF(self):
        """
        Open the local PDF set for this paper

        :return: None
        """
        # first validate
        self.validatePDFPath()
        # if it's valid, open the file
        local_file = self.db.get_paper_attribute(self.bibcode, "local_file")
        if local_file is not None:
            QDesktopServices.openUrl(f"file:{local_file}")

    def downloadPDF(self):
        """
        Download a PDF for this paper and update the database appropriately

        :return: None
        """
        # unhighlight the box
        self.unhighlightPDFButtons()
        # This is simple in principle. We'll check if we can access the publisher PDF.
        # If so, download it. If not, try the arXiv PDF. The downside of this is that
        # I found that the publishers have protections that identify this as a bot
        # (which I suppose it is), and block access. So there's a possibility that I
        # initially check a URL to see if there's a PDF there. It may be once, but the
        # next request will be blocked. If that happens, I may need to redo this
        # by just downloading the whole thing for each and see what kind of file it is.
        base_url = "https://ui.adsabs.harvard.edu/link_gateway/"
        for source in ["PUB_PDF", "EPRINT_PDF"]:
            this_url = base_url + self.bibcode + "/" + source
            r = requests.head(this_url, allow_redirects=True)
            page_type = r.headers["content-type"]
            if page_type.startswith("application/pdf"):
                break
        else:
            # no PDF found
            self.pdfDownloadButton.setText("Automatic Download Failed")
            return

        # we found the right URL, now ask the user where to download
        local_file = QFileDialog.getSaveFileName(
            caption="Select where to save this pdf", dir=str(Path.home())
        )[0]

        # the user may cancel
        if local_file == "":
            return

        # then download
        self._downloadURL(this_url, local_file)

        # and set the database attribute and show buttons
        self.db.set_paper_attribute(self.bibcode, "local_file", local_file)
        self.validatePDFPath()

    def _downloadURL(self, url, local_path):
        """
        Download a PDF from a URL to a given location

        :param url: the URL from which to download the file
        :type url: str
        :param local_path: Path at which to save the file
        :type local_path: str
        :return: None
        """
        r = requests.get(url, allow_redirects=True)
        Path(local_path).write_bytes(r.content)

    def highlightPDFButtons(self):
        """
        Visually highlight the area to specify the PDF, and scroll to the location

        :return: None
        """
        qss_trigger(self.pdfText, "pdf_highlight", True)
        qss_trigger(self.pdfChooseLocalFileButton, "pdf_highlight", True)
        qss_trigger(self.pdfDownloadButton, "pdf_highlight", True)
        # scroll down so the user can see the buttons
        self.ensureWidgetVisible(self.pdfDownloadButton)
        self.horizontalScrollBar().setValue(0)

    def unhighlightPDFButtons(self):
        """
        Remove the visual highlighting from the area to specify the PDF

        :return: None
        """
        qss_trigger(self.pdfText, "pdf_highlight", False)
        qss_trigger(self.pdfChooseLocalFileButton, "pdf_highlight", False)
        qss_trigger(self.pdfDownloadButton, "pdf_highlight", False)

    def mousePressEvent(self, event):
        """
        When clicked, reset the pdf button highlighting

        :param event: Mouse click event object
        :type event: PySide2.QtGui.QMouseEvent
        :return: None
        """
        self.unhighlightPDFButtons()


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
        super().__init__(min_width=300, offset=6)  # match offset to scrollbar width
        # add space for top sortChooser, then matching space at the bottom so the
        # last paper doesn't get cut off.
        self.layout.setContentsMargins(0, 35, 0, 35)
        self.papers = []

        self.rightPanel = rightPanel
        self.db = db
        rightPanel.papersList = self

        self.sortChooser = QComboBox()
        # set the options. By putting date first it's the default
        self.sortChooser.addItems(["Sort by Date", "Sort by First Author"])
        self.sortChooser.setFixedWidth(200)
        self.sortChooser.currentTextChanged.connect(self.changeSort)
        # Don't add the sortChooser to the layout. Instead, just set it as a child of
        # the papersList. That will allow it to float on top
        self.sortChooser.setParent(self)

        # initially sort by date
        self.changeSort()

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
        self.sortPapers()

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

    def sortPapers(self):
        """
        Rearrange the papers to be in sorted order by publication date

        :return: None
        """

        # To do this, we'll remove all the papers from the layout, sort them, then
        # add them back
        for paper in self.papers:
            self.layout.removeWidget(paper)
        # sort by publication date
        self.papers = sorted(self.papers, key=self.sortKey)
        for paper in self.papers:
            self.layout.addWidget(paper)

    def changeSort(self):
        """
        Change the sorting method used for the list of papers

        :return: None
        """
        text = self.sortChooser.currentText()
        if text == "Sort by Date":
            # Here we just sort by publication date
            self.sortKey = lambda p: self.db.get_paper_attribute(p.bibcode, "pubdate")
        elif text == "Sort by First Author":
            # Here we have to do something a bit more complex. We sort by the author's
            # last name first, then by their first name (to try to distinguish between
            # authors with the same last name. Then within each author, we sort by the
            # year. To accomplish this, we return a three item tuple, as Python sorts
            # by comparing the first item of the tuple, then the second, etc.
            def author_sort(p):
                first_author = self.db.get_paper_attribute(p.bibcode, "authors")[0]

                last_name = first_author.split(",")[0]
                rest_of_name = ",".join(first_author.split(",")[1:]).strip()
                year = self.db.get_paper_attribute(p.bibcode, "pubdate")
                return last_name, rest_of_name, year

            self.sortKey = author_sort
        self.sortPapers()

    def resizeEvent(self, resize_event):
        """
        Resize the window and move the sortChooser

        This will be called whenever the splitter is moved. Since we have the
        sortChooser at the top right, we need to keep it positioned in that spot as
        the window changes size

        :param resize_event: The event
        :type resize_event: QResizeEvent
        :return:
        """
        # first call the parent resize to adjust the window location
        super().resizeEvent(resize_event)
        # then move the sortChooser to be in the top right of the newly adjusted
        # window. We needed to adjust it first so we know its new size. We do have some
        # qss set to give there some margin around the sortChooser.
        # setting y=0 is defined to e at the top.
        self.sortChooser.move(self.size().width() - self.sortChooser.width(), 0)


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
        super().__init__(min_width=200, offset=25)
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

        # adjust the spacing between elements (i.e. tags). To compensate, increase the
        # margins around the buttons at the top, so they're not right on top of each
        # other. I do this with QSS
        self.layout.setSpacing(0)
        self.addTagButton.setProperty("is_left_panel_item", True)
        self.addTagBar.setProperty("is_left_panel_item", True)
        firstDeleteTagButton.setProperty("is_left_panel_item", True)
        secondDeleteTagEntry.setProperty("is_left_panel_item", True)
        thirdDeleteTagButton.setProperty("is_left_panel_item", True)
        thirdDeleteTagCancelButton.setProperty("is_left_panel_item", True)

    def addTag(self, new_tag):
        """
        Add a tag to the tags scroll area.

        This adds it to the internal list of tags and puts the widget in the interface

        :param tag: Tag object to be added to the list of stored tags.
        :type tag: LeftPanelTag
        :return: None
        """
        # check if this tag is already in the list. This should never happen
        assert new_tag.name not in [t.name for t in self.tags]

        # We then need to add it to the layout. We want the tags to be sorted. So what
        # we do is remove all tags from the layout, figure out the sort order, then add
        # everything back
        for tag in self.tags:
            self.layout.removeWidget(tag)
        # then add the new tag to this list. (we don't do this first because we don't
        # need to remove it
        self.tags.append(new_tag)
        # sort the tags by their name (not case sensitive)
        self.tags = sorted(self.tags, key=lambda tag: tag.name.lower())
        # then add them to the layout in this order
        for tag in self.tags:
            self.layout.addWidget(tag)


class EasyExitLineEdit(QLineEdit):
    """
    Just like a textEdit, but they can call a function (which should exit) with escape
    or backspace when all text is empty
    """

    def __init__(self, exitFunc, enterFunc):
        """
        Initialize the TextEdit.

        :param exitFunc: The function to be called if the user either hits escape or
                         hits backspace when the text is empty.
        :type exitFunc: function
        :param enterFunc: The function to be called if the user hits enter
        :type enterFunc: function
        """
        super().__init__()
        self.exitFunc = exitFunc
        self.enterFunc = enterFunc

    def keyPressEvent(self, keyPressEvent):
        """
        Either add normal text or exit under certain conditions.

        Any escape keypress exits, or a backspace when the text is empty

        :param keyPressEvent: The key press event
        :type keyPressEvent: ySide6.QtGui.QKeyEvent
        :return: None
        """
        # We overwrite the Enter, Escape, and Backspace keys, but let everything
        # else be handled normally
        if keyPressEvent.key() == Qt.Key_Enter or keyPressEvent.key() == Qt.Key_Return:
            # call the function specified
            self.enterFunc()
        elif keyPressEvent.key() == Qt.Key_Escape:
            # exit emmediately
            self.exitFunc()
        elif keyPressEvent.key() == Qt.Key_Backspace:
            # if there is text still there, just do a normal backspace. If there's
            # nothing there, exit.
            if self.text() != "":
                super().keyPressEvent(keyPressEvent)
            else:
                self.exitFunc()
        else:  # all other chanracters are handled normally
            super().keyPressEvent(keyPressEvent)


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
        qss_trigger(self.searchBarErrorText, "error_text", True)
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
        # make it look nice.
        self.searchBar.setFixedHeight(30)
        self.searchBarErrorText.setFixedHeight(30)
        self.addButton.setFixedHeight(30)
        # Then add these to the layouts
        hBoxSearchBar.addWidget(self.searchBar)
        hBoxSearchBar.addWidget(self.searchBarErrorText)
        hBoxSearchBar.addWidget(self.addButton)
        vBoxMain.addLayout(hBoxSearchBar)

        # Then we have the main body. This is a bit more complex. We'll start by just
        # initializing the layout for this, which is three panels laid horizonatlly.
        # This is the default splitter orientation
        self.splitter = QSplitter()
        # then make each of these things

        # The right panel is the details on a given paper. It holds the tags list,
        # which we need to initialize first
        self.rightPanel = RightPanel(self.db)

        # The central panel is the list of papers. This has to be set up after the
        # right panel because the paper objects need it, and before the left panel
        # because the tags need this panel. In the big picture, we have a main
        # wrapper so that we can keep the sort button at the top
        self.papersList = PapersListScrollArea(db, self.rightPanel)
        for b in self.db.get_all_bibcodes():
            self.papersList.addPaper(b)

        # The left panel of this is the list of tags the user has, plus the button to
        # add papers, which will go at the top of that list. This has to go after the
        # center panel since the tags need to access the paper list
        self.addTagButton = QPushButton("Add a tag")
        self.addTagButton.clicked.connect(self.showAddTagBar)
        self.addTagBar = EasyExitLineEdit(self.resetAddTag, self.addTag)
        self.addTagBar.setPlaceholderText("Tag name")
        self.addTagBar.hide()

        # Then set up the buttons to remove tags. We'll have four buttons. The first
        # will be a button to click to start the process of deleting a tag. Next
        # will be a text entry box for the user to specify which tag to delete, then
        # a confirm and cancel button
        self.firstDeleteTagButton = QPushButton("Delete a tag")
        self.firstDeleteTagButton.clicked.connect(self.revealSecondTagDeleteEntry)
        self.secondDeleteTagEntry = EasyExitLineEdit(
            self.cancelTagDeletion, self.revealThirdTagDeleteButtons
        )
        self.secondDeleteTagEntry.setPlaceholderText("Tag to delete")
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
        self.splitter.addWidget(self.tagsList)
        self.splitter.addWidget(self.papersList)
        self.splitter.addWidget(self.rightPanel)

        # Add this to the main layout
        vBoxMain.addWidget(self.splitter)

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
        self.resize(1100, 600)
        # set the splitter
        self.splitter.setSizes([200, 550, 350])
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
            self.formatSearchBarError(
                "This paper was not found in ADS. "
                "If it was just added to the arXiv, "
                "ADS may not have registered it."
            )
            return
        except PaperAlreadyInDatabaseError:
            self.formatSearchBarError("This paper is already in the library.")
            return
        except ads.exceptions.APIResponseError:
            # ADS key not set
            self.formatSearchBarError(
                "You don't have an ADS key set. "
                "See this repository readme for more, then restart this application."
            )
            return

        # we only get here if the addition to the database worked. If so we add the
        # paper object, then clear the search bar
        self.papersList.addPaper(bibcode)
        # clear the text so another paper can be added
        self.searchBar.clear()

    def formatSearchBarError(self, error_text):
        """
        When an error with the ADS library happens, change the formatting.

        :param error_text: The text to display in the error message.
        :type error_text: str
        :return: None
        """
        self.searchBarErrorText.setText(error_text)
        self.searchBarErrorText.show()
        self.addButton.hide()
        qss_trigger(self.searchBar, "error", True)

    def resetSearchBarError(self):
        """
        After an error, reset the search bar formatting to the original state

        :return: None
        """
        qss_trigger(self.searchBar, "error", False)
        self.searchBarErrorText.hide()
        self.addButton.show()

    def showAddTagBar(self):
        """
        When the add tag button is clicked, hide that and show the text entry bar

        :return: None
        """
        self.addTagButton.hide()
        self.addTagBar.show()
        self.addTagBar.setFocus()

    def resetAddTag(self):
        """
        Reset the add tag buttons to be the original state.

        This can either happen after successfull entry or cancellation

        :return: None
        """
        self.addTagBar.clear()
        self.addTagBar.hide()
        self.addTagButton.show()

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
            # add this checkbox to the right panel
            self.rightPanel.populate_tags()
        except ValueError:  # this tag is already in the database
            return

        # if we got here we had no error, so it was successfully added and we should
        # clear the text box and reset the buttons
        self.resetAddTag()

    def revealSecondTagDeleteEntry(self):
        """
        When the tag delete button is pressed, hide the button and reveal the text entry

        :return: None
        """
        self.firstDeleteTagButton.hide()
        self.secondDeleteTagEntry.show()
        self.secondDeleteTagEntry.setFocus()

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
        self.thirdDeleteTagButton.setText(f'Confirm deletion of tag "{tag_to_delete}"')
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
            if tag.label.text() == tag_to_delete:
                tag.hide()  # just to be safe
                self.tagsList.tags.remove(tag)
                del tag
        # then reset the boxes
        self.cancelTagDeletion()
        # and reset the checkboxes in the rightPanel
        self.rightPanel.populate_tags()

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
