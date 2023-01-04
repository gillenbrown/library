"""
test_interface.py

Perform tests on the GUI using pytest-qt
"""
import os
import sys
from pathlib import Path
import random
import requests
import shutil
import subprocess

# make sure tests do not appear on screen
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
import pytestqt
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QDesktopServices, QGuiApplication, QPalette
from PySide6.QtWidgets import QFileDialog, QLineEdit, QTextEdit, QScrollArea
import darkdetect
import ads

from library.interface import MainWindow, get_fonts, set_up_fonts, Paper
from library.database import Database
import test_utils as u


# ======================================================================================
#
# Database fixtures
#
# ======================================================================================
@pytest.fixture(name="db_empty")
def temporary_database():
    """
    Fixture to get a database at a temporary path in the current directory. This will be
    removed once the test is done
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db_temp")
def temporary_database_with_papers():
    """
    Fixture to get a database at a temporary path in the current directory. This will be
    removed once the test is done
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    db.add_new_tag("Read")
    db.add_new_tag("Unread")
    db.add_paper(u.mine.bibcode)
    db.add_paper(u.tremonti.bibcode)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db_no_tags")
def temporary_database_with_papers_no_tags():
    """
    Fixture to get a database at a temporary path in the current directory. This will be
    removed once the test is done
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    db.add_paper(u.mine.bibcode)
    db.add_paper(u.tremonti.bibcode)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db_empty_bad_ads")
def temporary_database_with_changed_ads_key():
    """
    Fixture to get a database at a temporary path in the current directory. This will be
    removed once the test is done. It also changes the ADS key to something bad, then
    resets it at the end of the test
    """
    # set the key to something bad
    original_key = os.environ["ADS_DEV_KEY"]
    os.environ["ADS_DEV_KEY"] = "junk"

    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    yield db
    file_path.unlink()  # removes this file

    # reset the key
    os.environ["ADS_DEV_KEY"] = original_key


@pytest.fixture(name="db_notes")
def temporary_database_with_papers_and_notes():
    """
    Fixture to get a database at a temporary path in the current directory. This will be
    removed once the test is done
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    db.add_new_tag("Read")
    db.add_paper(u.mine.bibcode)
    db.set_paper_attribute(u.mine.bibcode, "user_notes", "abc123")
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db_update")
def temporary_db_with_old_arxiv_paper():
    """
    Fixture to get a database I've prefilled with one paper with arXiv only details.
    This paper has since been published in a journal, so this is designed to check
    whether the database can update papers to include this information.

    Note that this provides a temporary database that's a copy of the original, since
    I don't want that one to be modified
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    shutil.copy2(Path(__file__).parent / "testing_update.db", file_path)
    db = Database(file_path)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db")
def testing_database():
    """
    Fixture to get the testing database, which has some prefilled info. This avoids
    lots of unnecessary ADS calls
    """
    return Database(Path(__file__).parent / "testing.db")


# ======================================================================================
#
# Convenience functions
#
# ======================================================================================
# All convenience functions will have "c" at the beginning, just for clarity
def cInitialize(qtbot, db):
    """
    Initialize the interface and make sure qtbot knows about it

    :param qtbot: the qtbot instance used in a given test
    :param db: The database to use for the interface
    :type db: Database
    :return: the main window widget
    :rtype: MainWindow
    """
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    return widget


def cClick(widget, qtbot):
    """
    Click on a given widget

    :param widget: The widget to click on
    :type widget: QWidget
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    qtbot.mouseClick(widget, Qt.LeftButton)


def cDoubleClick(widget, qtbot):
    """
    Double click on a given widget

    :param widget: The widget to double click
    :type widget: QWidget
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    qtbot.mouseDClick(widget, Qt.LeftButton)


def cEnterText(widget, text, qtbot):
    """
    Type some text into a widget

    :param widget: The widget to enter text into
    :type widget: QWidget
    :param text: The text to enter
    type text: str
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    qtbot.keyClicks(widget, text)


def cPressEnter(widget, qtbot):
    """
    Press the enter key in a given text entry area

    :param widget: The text entry area in which to press enter
    :type widget: QWidget
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    qtbot.keyPress(widget, Qt.Key_Enter)


def cPressEscape(widget, qtbot):
    """
    Press the escape key in a given text entry area

    :param widget: The text entry area in which to press escape
    :type widget: QWidget
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    qtbot.keyPress(widget, Qt.Key_Escape)


def cPressBackspace(widget, qtbot):
    """
    Press backspace in a given text entry area

    :param widget: The text entry area in which to press backspace
    :type widget: QWidget
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    qtbot.keyPress(widget, Qt.Key_Backspace)


def cAddPaper(mainWidget, identifier, qtbot):
    """
    Add a paper through the interface

    :param mainWidget: The main window widget
    :type mainWidget: MainWindow
    :param identifier: the identifier for this paper (URL, bibcode)
    :type identifier: str
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    cEnterText(mainWidget.searchBar, identifier, qtbot)
    cPressEnter(mainWidget.searchBar, qtbot)


def cAddTag(mainWidget, tagName, qtbot):
    """
    Add a tag through the interface

    :param mainWidget: The main window widget
    :type mainWidget: MainWindow
    :param tagName: the name of the tag to add
    :type tagName: str
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    cClick(mainWidget.tagsList.addTagButton, qtbot)
    cEnterText(mainWidget.tagsList.addTagBar, tagName, qtbot)
    cPressEnter(mainWidget.tagsList.addTagBar, qtbot)


def cDeleteTag(mainWidget, tagName, qtbot):
    """
    Delete a tag through the interface

    :param mainWidget: The main window widget
    :type mainWidget: MainWindow
    :param tagName: The name of the tag to delete
    :type tagName: str
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    cClick(mainWidget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(mainWidget.tagsList.secondDeleteTagEntry, tagName, qtbot)
    cPressEnter(mainWidget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(mainWidget.tagsList.thirdDeleteTagButton, qtbot)


def cRenameTag(mainWidget, oldTagName, newTagName, qtbot):
    """
    Rename a tag through the interface

    :param mainWidget: The main window widget
    :type mainWidget: MainWindow
    :param oldTagName: The name of the tag to rename
    :type oldTagName: str
    :param newTagName: The new name of the tag
    :type newTagName: str
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    cClick(mainWidget.tagsList.renameTagButton, qtbot)
    cEnterText(mainWidget.tagsList.renameTagOldEntry, oldTagName, qtbot)
    cPressEnter(mainWidget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(mainWidget.tagsList.renameTagNewEntry, newTagName, qtbot)
    cPressEnter(mainWidget.tagsList.renameTagNewEntry, qtbot)


def cDeleteFirstPaper(mainWidget, qtbot):
    """
    Delete the first paper in the interface

    :param mainWidget: The main window widget
    :type mainWidget: MainWindow
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    cClick(mainWidget.papersList.getPapers()[0], qtbot)
    cClick(mainWidget.rightPanel.firstDeletePaperButton, qtbot)
    cClick(mainWidget.rightPanel.secondDeletePaperButton, qtbot)


def cEditCiteKey(mainWidget, citeKey, qtbot):
    """
    Edit the citation key of a paper using the interface

    Note that a paper must be clicked before this can work

    :param mainWidget: The main window widget
    :type mainWidget: MainWindow
    :param citeKey: The new citation key to give this paper
    :type citeKey: str
    :param qtbot: the qtbot instance used in a given test
    :return: None
    """
    # paper must already be clicked
    assert mainWidget.rightPanel.bibcode is not None
    cClick(mainWidget.rightPanel.editCiteKeyButton, qtbot)
    # since there may be text there already, clear it for clarity
    mainWidget.rightPanel.editCiteKeyEntry.clear()
    cEnterText(mainWidget.rightPanel.editCiteKeyEntry, citeKey, qtbot)
    cPressEnter(mainWidget.rightPanel.editCiteKeyEntry, qtbot)


def cGetTextAlpha(widget):
    """
    Get the alpha value of the text in a widget (0=clear, 255=opaque)

    :param widget: The widget to check
    :type widget: QWidget
    :return: the alpha value
    :rtype: int
    """
    return widget.palette().color(QPalette.Text).toRgb().toTuple()[-1]


# ======================================================================================
#
# mock functions for use with monkeypatch
#
# ======================================================================================
# when we open an existing file, we have filter and dir kwargs, then return the filename
# and some filter info, which my code ignores
def mOpenFileNoResponse(filter="", dir=""):
    """
    Mock the response if the user exists the file chooser window
    """
    # if the user cancels the real function, it returns an empty string
    return "", ""


def mOpenFileNonexistent(filter="", dir=""):
    """
    Mock a response if the user chooses a file that does not exist
    """
    return "nonexistent_file.pdf", ""


def mOpenFileExists(filter="", dir=""):
    """
    Mock a response if the user chooses a file that exists, namely this file
    """
    return __file__, ""


# When saving a file, we have the filter and dir kwargs, but also a caption. We return
# the same things we did when we open an existing file.
mSaveLocPDF = Path(__file__).parent / "test.pdf"
mSaveLocTXT = mSaveLocPDF.parent / "test.txt"


def mSaveFileValidPDF(filter="", dir="", caption=""):
    """
    Mock a response if the user chooses a pdf file
    """
    return str(mSaveLocPDF), ""


def mSaveFileValidNoSuffix(filter="", dir="", caption=""):
    """
    Mock a response if the user chooses a file with no extension
    """
    return str(mSaveLocPDF).replace(".pdf", ""), ""


def mSaveFileValidTXT(filter="", dir="", caption=""):
    """
    Mock a response if the user chooses a txt file
    """
    return str(mSaveLocTXT), ""


def mSaveFileNoResponse(filter="", dir="", caption=""):
    """
    Mock a response if the user exits the file chooser without choosing anything
    """
    return "", ""


# ======================================================================================
#
# functions to create bibtex files for import -- copied from test_database.py
#
# ======================================================================================
def create_bibtex_monkeypatch(*args):
    """
    Write bibtex entries into a random bibtex file, and return the file location

    :param args: bibtex entries to write to the file
    :type args: str
    :return: path to the file location and a function to use with monkeypatch
    :rtype: (pathlib.Path, func)
    """
    text = "\n\n".join(args)
    file_path = Path(f"{random.randint(0, 1000000000)}.bib").resolve()
    with open(file_path, "w") as bibfile:
        bibfile.write(text)
    monkeypatch_func = lambda filter, dir: (str(file_path), "dummy_filter")
    return file_path, monkeypatch_func


# ======================================================================================
#
# test premade databases
#
# ======================================================================================
def test_testing_database_was_premade_with_some_papers(db):
    assert len(db.get_all_bibcodes()) > 0


def test_testing_database_was_premade_with_some_tags(db):
    assert len(db.get_all_tags()) > 0


def test_testing_database_has_at_least_one_tag_on_each_paper(db):
    for b in db.get_all_bibcodes():
        assert len(db.get_paper_tags(b)) > 0


def test_testing_database_has_each_tag_on_at_least_one_paper(db):
    for t in db.get_all_tags():
        tag_used = False
        for b in db.get_all_bibcodes():
            if t in db.get_paper_tags(b):
                tag_used = True
        assert tag_used


# ======================================================================================
#
# test main window and similar
#
# ======================================================================================
def test_all_fonts_are_found_by_get_fonts():
    font_dir = (
        Path(__file__).parent.parent / "library" / "resources" / "fonts"
    ).absolute()
    true_fonts = [
        font_dir / "Bungee_Shade" / "BungeeShade-Regular.ttf",
        font_dir / "Cabin" / "Cabin-Bold.ttf",
        font_dir / "Cabin" / "Cabin-BoldItalic.ttf",
        font_dir / "Cabin" / "Cabin-Italic.ttf",
        font_dir / "Cabin" / "Cabin-Medium.ttf",
        font_dir / "Cabin" / "Cabin-MediumItalic.ttf",
        font_dir / "Cabin" / "Cabin-Regular.ttf",
        font_dir / "Cabin" / "Cabin-SemiBold.ttf",
        font_dir / "Cabin" / "Cabin-SemiBoldItalic.ttf",
        font_dir / "Lobster" / "Lobster-Regular.ttf",
    ]
    true_fonts_str = [str(f) for f in true_fonts]

    test_fonts = []
    get_fonts(font_dir, test_fonts)

    # order doesn't matter, so sort them both
    assert sorted(true_fonts_str) == sorted(test_fonts)


def test_fonts_are_actually_in_the_font_database_after_set_up_fonts(qtbot):
    # qtbot is needed to initialize the application
    assert not QFontDatabase.hasFamily("Lobster")
    assert not QFontDatabase.hasFamily("Cabin")

    set_up_fonts()

    assert QFontDatabase.hasFamily("Lobster")
    assert QFontDatabase.hasFamily("Cabin")


def test_window_initial_width(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.size().width() == 1100


def test_window_initial_height(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.size().height() == 600


def test_title_is_has_text_saying_library(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.title.text() == "Library"


def test_title_is_lobster_font(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.title.font().family() == "Lobster"


def test_title_is_correct_font_size(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.title.font().pointSize() == 40


# ===================
# update notification
# ===================
def test_import_notification_normally_disabled(qtbot, db, monkeypatch):
    # I'm not exactly sure of the state of the git repository when doing the GitHub
    # actions tests, but the git fetch was returning something. So it looks like I
    # can't assume that the repo is in the most recent state. So monkeypatch this to
    # make sure it works as expected.
    class dummy(object):
        stdout = (
            b"On branch master\nYour branch is up to date with 'origin/master'."
            b"\n\nnothing to commit (use -u to show untracked files)"
        )

    monkeypatch.setattr(subprocess, "run", lambda cmd, capture_output: dummy())
    widget = cInitialize(qtbot, db)
    assert widget.updateText.isHidden() is True


def test_import_notification_shown_when_needed(qtbot, db, monkeypatch):
    class dummy(object):
        stdout = (
            b"On branch master\n"
            b"Your branch is behind 'origin/master' by 1 commit, "
            b"and can be fast-forwarded.\n"
            b'    (use "git pull" to update your local branch)\n\n'
            b"nothing to commit (use -u to show untracked files)"
        )

    monkeypatch.setattr(subprocess, "run", lambda cmd, capture_output: dummy())
    widget = cInitialize(qtbot, db)
    assert widget.updateText.isHidden() is False


def test_import_notification_text(qtbot, db, monkeypatch):
    class dummy(object):
        stdout = (
            b"On branch master\n"
            b"Your branch is behind 'origin/master' by 1 commit, "
            b"and can be fast-forwarded.\n"
            b'    (use "git pull" to update your local branch)\n\n'
            b"nothing to commit (use -u to show untracked files)"
        )

    monkeypatch.setattr(subprocess, "run", lambda cmd, capture_output: dummy())
    widget = cInitialize(qtbot, db)
    assert widget.updateText.text().startswith(
        "An update is available! To update, navigate to "
    )
    assert widget.updateText.text().endswith(
        "in the terminal, run `git pull`, then restart this application."
    )


def test_import_notification_text_path(qtbot, db, monkeypatch):
    class dummy(object):
        stdout = (
            b"On branch master\n"
            b"Your branch is behind 'origin/master' by 1 commit, "
            b"and can be fast-forwarded.\n"
            b'    (use "git pull" to update your local branch)\n\n'
            b"nothing to commit (use -u to show untracked files)"
        )

    monkeypatch.setattr(subprocess, "run", lambda cmd, capture_output: dummy())
    widget = cInitialize(qtbot, db)
    shown_path = widget.updateText.text().split()[8]
    # ~ isn't part of Windows, so we need to be careful about how we check
    if sys.platform != "win32":
        assert shown_path.startswith("~/")
    assert Path(shown_path).expanduser() == Path(__file__).parent.parent.resolve()


def test_import_notification_disabled_if_no_internet(qtbot, db, monkeypatch):
    class dummy(object):
        stderr = (
            b"fatal: unable to access "
            b"'https://github.com/gillenbrown/library.git/': "
            b"Could not resolve host: github.com\n"
        )
        stdout = b"dummy"

    monkeypatch.setattr(subprocess, "run", lambda cmd, capture_output: dummy())
    widget = cInitialize(qtbot, db)
    assert widget.updateText.isHidden() is True


# ==========================
# sizing of the three panels
# ==========================
def test_widgets_are_sized_appropriately_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # get the original positions
    o_sizes = widget.splitter.sizes()
    # check examples in each panel
    assert o_sizes[0] < o_sizes[2] < o_sizes[1]


def test_widgets_dont_go_outside_of_splitter(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # get the original positions
    o_sizes = widget.splitter.sizes()
    # check examples in each panel
    assert widget.tagsList.addTagBar.size().width() <= o_sizes[0]
    assert widget.papersList.getPapers()[0].size().width() <= o_sizes[1]
    assert widget.rightPanel.titleText.size().width() <= o_sizes[2]


def test_resizing_splitter_resizes_widgets(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # get the original positions
    o_sizes = widget.splitter.sizes()
    assert sum(o_sizes) > 600
    new_sizes = [250, 350, sum(o_sizes) - 500]
    widget.splitter.setSizes(new_sizes)
    # check examples in each panel. They won't be exact, but should be close
    assert (
        new_sizes[0] * 0.7 <= widget.tagsList.addTagBar.size().width() <= new_sizes[0]
    )
    assert (
        new_sizes[1] * 0.7
        <= widget.papersList.getPapers()[0].size().width()
        <= new_sizes[1]
    )
    assert (
        new_sizes[2] * 0.7 <= widget.rightPanel.titleText.size().width() <= new_sizes[2]
    )


def test_sortchooser_starts_at_top_right(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    position = widget.papersList.sortChooser.pos()
    expected_x = widget.papersList.width() - widget.papersList.sortChooser.width()
    assert position.x() == expected_x
    assert position.y() == 0


def test_resizing_splitter_keeps_sortchooser_at_top_right(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    position = widget.papersList.sortChooser.pos()
    new_sizes = [250, 350, sum(widget.splitter.sizes()) - 500]
    widget.splitter.setSizes(new_sizes)
    new_position = widget.papersList.sortChooser.pos()
    assert new_position.x() != position.x()
    expected_x = widget.papersList.width() - widget.papersList.sortChooser.width()
    assert new_position.x() == expected_x
    assert new_position.y() == 0


def test_adding_long_tag_resizes_splitter(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    original_sizes = widget.splitter.sizes()
    cAddTag(widget, "this is a very long tag, too long to realistically use", qtbot)
    new_sizes = widget.splitter.sizes()
    assert new_sizes[0] > original_sizes[0]


def test_db_with_long_tag_has_wide_tag_bar_at_beginning(qtbot, db_temp):
    db_temp.add_new_tag("this is a very long tag, too long really")
    widget = cInitialize(qtbot, db_temp)
    original_sizes = widget.splitter.sizes()
    assert original_sizes[0] > 200
    for tag in widget.tagsList.tags:
        assert tag.width() >= tag.sizeHint().width()


def test_deleting_long_tag_resizes_splitter(qtbot, db_temp):
    tag_name = "this is a very long tag, too long to realistically use"
    db_temp.add_new_tag(tag_name)
    widget = cInitialize(qtbot, db_temp)
    original_sizes = widget.splitter.sizes()
    cDeleteTag(widget, tag_name, qtbot)
    new_sizes = widget.splitter.sizes()
    assert new_sizes[0] < original_sizes[0]
    assert new_sizes[0] == max(
        widget.tagsList.default_min_width,
        max([tag.sizeHint().width() for tag in widget.tagsList.tags]),
    )


def test_renaming_long_tag_resizes_splitter(qtbot, db_temp):
    tag_name = "this is a very long tag, too long to realistically use"
    db_temp.add_new_tag(tag_name)
    widget = cInitialize(qtbot, db_temp)
    original_sizes = widget.splitter.sizes()
    cRenameTag(widget, tag_name, "short", qtbot)
    new_sizes = widget.splitter.sizes()
    assert new_sizes[0] < original_sizes[0]
    assert new_sizes[0] == max(
        widget.tagsList.default_min_width,
        max([tag.sizeHint().width() for tag in widget.tagsList.tags]),
    )


def test_showing_delete_tag_confirm_resizes_splitter(qtbot, db_temp):
    tag_name = "this is a very long tag"
    db_temp.add_new_tag(tag_name)
    widget = cInitialize(qtbot, db_temp)
    original_sizes = widget.splitter.sizes()
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, tag_name, qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    new_sizes = widget.splitter.sizes()
    assert new_sizes[0] > original_sizes[0]


def test_confirming_tag_delete_resizes_splitter(qtbot, db_temp):
    tag_name = "this is a very long tag, too long to realistically use"
    db_temp.add_new_tag(tag_name)
    widget = cInitialize(qtbot, db_temp)
    # don't use convenience function, since we need size at intermediate steps
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, tag_name, qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    original_sizes = widget.splitter.sizes()
    cClick(widget.tagsList.thirdDeleteTagButton, qtbot)
    new_sizes = widget.splitter.sizes()
    assert new_sizes[0] < original_sizes[0]
    assert new_sizes[0] == max(
        widget.tagsList.default_min_width,
        max([tag.sizeHint().width() for tag in widget.tagsList.tags]),
    )


def test_first_paper_takes_up_full_splitter_width(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    paper_width = widget.papersList.getPapers()[0].width()
    splitter_width = widget.splitter.sizes()[1]
    assert paper_width == splitter_width


def test_first_import_paper_takes_up_full_splitter_width(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    paper_width = widget.papersList.getPapers()[0].width()
    splitter_width = widget.splitter.sizes()[1]
    # sometimes this is very close but not exact, so I'll just check for closeness. I
    # think this has something to do with how the new long tag name from the import
    # changes the splitter. But I tested this in acutual use, and everything is fine
    assert abs(paper_width - splitter_width) < 10


# ====================
# light and dark theme
# ====================
def test_initial_theme_matches_os_theme_light(qtbot, db, monkeypatch):
    monkeypatch.setattr(darkdetect, "theme", lambda: "Light")
    widget = cInitialize(qtbot, db)
    color = widget.title.palette().color(QPalette.WindowText).toRgb().toTuple()
    assert color == (0, 0, 0, 255)


def test_initial_theme_matches_os_theme_dark(qtbot, db, monkeypatch):
    monkeypatch.setattr(darkdetect, "theme", lambda: "Dark")
    widget = cInitialize(qtbot, db)
    color = widget.title.palette().color(QPalette.WindowText).toRgb().toTuple()
    assert color == (238, 238, 238, 255)


def test_dark_theme_activated_when_title_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.title, qtbot)
    color = widget.title.palette().color(QPalette.WindowText).toRgb().toTuple()
    assert color == (238, 238, 238, 255)


def test_theme_switches_each_click(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.title, qtbot)
    cClick(widget.title, qtbot)
    color = widget.title.palette().color(QPalette.WindowText).toRgb().toTuple()
    assert color == (0, 0, 0, 255)


# ======================================================================================
#
# test search bar and adding papers from it
#
# ======================================================================================
# =============
# initial state
# =============
def test_textedit_error_message_hidden_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.searchBarErrorText.isHidden() is True


def test_add_paper_button_shown_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.addButton.isHidden() is False


def test_import_button_shown_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.importButton.isHidden() is False


def test_import_progress_bar_not_shown_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.importProgressBar.isHidden() is True


def test_import_result_text_not_shown_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.importResultText.isHidden() is True


def test_import_result_text_dismiss_not_shown_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.importResultDismissButton.isHidden() is True


def test_import_result_text_is_copyable(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.importResultText.textInteractionFlags() == Qt.TextSelectableByMouse


def test_textedit_is_not_in_error_state_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.searchBar.property("error") is False


def test_search_bar_has_placeholder_text(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    text = "Enter your paper URL or ADS bibcode here"
    assert widget.searchBar.placeholderText() == text


def test_search_bar_has_correct_font_family(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.searchBar.font().family() == "Cabin"


def test_search_bar_has_correct_font_size(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.searchBar.font().pointSize() == 14


def test_add_button_has_correct_font_family(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.addButton.font().family() == "Cabin"


def test_add_button_has_correct_font_size(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.addButton.font().pointSize() == 14


def test_add_button_and_search_bar_have_almost_same_height(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    height_ratio = widget.addButton.height() / widget.searchBar.height()
    assert 0.8 < height_ratio < 1.3


def test_add_button_and_import_button_have_same_height(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.addButton.height() == widget.importButton.height()


def test_add_button_and_search_bar_are_much_shorter_than_title(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.addButton.height() < 0.6 * widget.title.height()
    assert widget.searchBar.height() < 0.6 * widget.title.height()


# ==========================
# colors of placeholder text
# ==========================
def test_searchbar_placeholder_text_starts_transparent(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert cGetTextAlpha(widget.searchBar) == 100


def test_searchbar_text_is_not_transparent_once_modified(qtbot, db):
    widget = cInitialize(qtbot, db)
    cEnterText(widget.searchBar, "g", qtbot)
    assert cGetTextAlpha(widget.searchBar) == 255


def test_searchbar_text_is_transparent_once_cleared(qtbot, db):
    widget = cInitialize(qtbot, db)
    cEnterText(widget.searchBar, "g", qtbot)
    cPressBackspace(widget.searchBar, qtbot)
    assert cGetTextAlpha(widget.searchBar) == 100


def test_add_tag_placeholder_text_starts_transparent(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.addTagButton, qtbot)
    assert cGetTextAlpha(widget.tagsList.addTagBar) == 100


def test_add_tag_text_is_not_transparent_once_modified(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.addTagButton, qtbot)
    cEnterText(widget.tagsList.addTagBar, "g", qtbot)
    assert cGetTextAlpha(widget.tagsList.addTagBar) == 255


def test_add_tag_text_is_transparent_once_cleared(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.addTagButton, qtbot)
    cEnterText(widget.tagsList.addTagBar, "g", qtbot)
    cPressBackspace(widget.tagsList.addTagBar, qtbot)
    assert cGetTextAlpha(widget.tagsList.addTagBar) == 100


def test_delete_tag_placeholder_text_starts_transparent(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    assert cGetTextAlpha(widget.tagsList.secondDeleteTagEntry) == 100


def test_delete_tag_text_is_not_transparent_once_modified(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "g", qtbot)
    assert cGetTextAlpha(widget.tagsList.secondDeleteTagEntry) == 255


def test_delete_tag_text_is_transparent_once_cleared(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "g", qtbot)
    cPressBackspace(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert cGetTextAlpha(widget.tagsList.secondDeleteTagEntry) == 100


def test_rename_tag_first_placeholder_text_starts_transparent(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.renameTagButton, qtbot)
    assert cGetTextAlpha(widget.tagsList.renameTagOldEntry) == 100


def test_rename_tag_first_text_is_not_transparent_once_modified(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "g", qtbot)
    assert cGetTextAlpha(widget.tagsList.renameTagOldEntry) == 255


def test_rename_tag_first_text_is_transparent_once_cleared(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "g", qtbot)
    cPressBackspace(widget.tagsList.renameTagOldEntry, qtbot)
    assert cGetTextAlpha(widget.tagsList.renameTagOldEntry) == 100


def test_rename_tag_second_placeholder_text_starts_transparent(qtbot, db_empty):
    db_empty.add_new_tag("old")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "old", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert cGetTextAlpha(widget.tagsList.renameTagNewEntry) == 100


def test_rename_tag_second_text_is_not_transparent_once_modified(qtbot, db_empty):
    db_empty.add_new_tag("old")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "old", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "g", qtbot)
    assert cGetTextAlpha(widget.tagsList.renameTagNewEntry) == 255


def test_rename_tag_second_text_is_transparent_once_cleared(qtbot, db_empty):
    db_empty.add_new_tag("old")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "old", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "g", qtbot)
    cPressBackspace(widget.tagsList.renameTagNewEntry, qtbot)
    assert cGetTextAlpha(widget.tagsList.renameTagNewEntry) == 100


def test_cite_key_placeholder_text_is_transparent(qtbot, db_temp):
    # click on a paper with no cite key set
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert cGetTextAlpha(widget.rightPanel.editCiteKeyEntry) == 100


def test_cite_key_placeholder_text_is_not_transparent_when_modified(qtbot, db_temp):
    # click on a paper with no cite key set
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "g", qtbot)
    assert cGetTextAlpha(widget.rightPanel.editCiteKeyEntry) == 255


def test_cite_key_placeholder_text_is_transparent_when_cleared(qtbot, db_temp):
    # click on a paper with no cite key set
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "g", qtbot)
    cPressBackspace(widget.rightPanel.editCiteKeyEntry, qtbot)
    assert cGetTextAlpha(widget.rightPanel.editCiteKeyEntry) == 100


def test_cite_key_not_transparent_if_set(qtbot, db_empty):
    # click on a paper with a cite key set
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "citation_keyword", "test")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert cGetTextAlpha(widget.rightPanel.editCiteKeyEntry) == 255


def test_cite_key_transparent_correct_new_paper_clear_to_clear(qtbot, db_temp):
    # test when transitioning from one paper without a key to another without a key
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert cGetTextAlpha(widget.rightPanel.editCiteKeyEntry) == 100


def test_cite_key_transparent_correct_new_paper_clear_to_full(qtbot, db_temp):
    # test when transitioning from one paper without a key to another with a key
    db_temp.set_paper_attribute(u.tremonti.bibcode, "citation_keyword", "test")
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[1], qtbot)  # mine
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cClick(widget.papersList.getPapers()[0], qtbot)  # tremonti
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert cGetTextAlpha(widget.rightPanel.editCiteKeyEntry) == 255


def test_cite_key_transparent_correct_new_paper_full_to_clear(qtbot, db_temp):
    # test when transitioning from one paper with a key to another without a key
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "sdf", qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert cGetTextAlpha(widget.rightPanel.editCiteKeyEntry) == 100


def test_cite_key_transparent_correct_new_paper_full_to_full(qtbot, db_temp):
    # test when transitioning from one paper with a key to another with a key
    db_temp.set_paper_attribute(u.tremonti.bibcode, "citation_keyword", "test")
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[1], qtbot)  # mine
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "sdf", qtbot)
    cClick(widget.papersList.getPapers()[0], qtbot)  # tremonti
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert cGetTextAlpha(widget.rightPanel.editCiteKeyEntry) == 255


# =============
# adding papers
# =============
def test_can_add_paper_by_filling_bibcode_then_clicking_button(qtbot, db_empty):
    assert len(db_empty.get_all_bibcodes()) == 0
    widget = cInitialize(qtbot, db_empty)
    cEnterText(widget.searchBar, u.mine.bibcode, qtbot)
    cClick(widget.addButton, qtbot)
    assert len(db_empty.get_all_bibcodes()) == 1
    assert u.mine.bibcode in db_empty.get_all_bibcodes()


def test_can_add_paper_by_filling_bibcode_then_pressing_enter(qtbot, db_empty):
    assert len(db_empty.get_all_bibcodes()) == 0
    widget = cInitialize(qtbot, db_empty)
    cEnterText(widget.searchBar, u.mine.bibcode, qtbot)
    cPressEnter(widget.searchBar, qtbot)
    assert len(db_empty.get_all_bibcodes()) == 1
    assert u.mine.bibcode in db_empty.get_all_bibcodes()


def test_adding_paper_adds_paper_to_interface(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert len(widget.papersList.getPapers()) == 0
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert len(widget.papersList.getPapers()) == 1


def test_adding_paper_adds_correct_paper_to_interface(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert widget.papersList.getPapers()[0].bibcode == u.mine.bibcode


def test_adding_paper_clears_search_bar_if_successful(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert widget.searchBar.text() == ""


def test_adding_paper_does_not_clear_search_bar_if_not_successful(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    assert widget.searchBar.text() == "nonsense"


def test_adding_paper_highlights_it_in_center_panel(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cAddPaper(widget, u.forbes.bibcode, qtbot)
    for paper in widget.papersList.getPapers():
        if paper.bibcode == u.forbes.bibcode:
            assert paper.property("is_highlighted") is True
        else:
            assert paper.property("is_highlighted") is False


def test_adding_paper_puts_details_in_right_panel(qtbot, db_temp):
    # this is a cursory test. Full right panel details are tested elsewhere. I'm
    # assuming that if the title is correct, the rest will be too
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cAddPaper(widget, u.forbes.bibcode, qtbot)
    assert widget.rightPanel.titleText.text() == u.forbes.title


def test_adding_paper_initial_highlights_it_in_center_panel(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddPaper(widget, u.forbes.bibcode, qtbot)
    for paper in widget.papersList.getPapers():
        if paper.bibcode == u.forbes.bibcode:
            assert paper.property("is_highlighted") is True
        else:
            assert paper.property("is_highlighted") is False


def test_adding_paper_initial_puts_details_in_right_panel(qtbot, db_temp):
    # this is a cursory test. Full right panel details are tested elsewhere. I'm
    # assuming that if the title is correct, the rest will be too
    widget = cInitialize(qtbot, db_temp)
    cAddPaper(widget, u.forbes.bibcode, qtbot)
    assert widget.rightPanel.titleText.text() == u.forbes.title


def test_adding_paper_after_delete_highlights_it_in_center_panel(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    bibcode = widget.papersList.getPapers()[0].bibcode
    cDeleteFirstPaper(widget, qtbot)
    cAddPaper(widget, bibcode, qtbot)
    for paper in widget.papersList.getPapers():
        if paper.bibcode == bibcode:
            assert paper.property("is_highlighted") is True
        else:
            assert paper.property("is_highlighted") is False


def test_adding_paper_after_delete_puts_details_in_right_panel(qtbot, db_temp):
    # this is a cursory test. Full right panel details are tested elsewhere. I'm
    # assuming that if the title is correct, the rest will be too
    widget = cInitialize(qtbot, db_temp)
    bibcode = widget.papersList.getPapers()[0].bibcode
    title = widget.papersList.getPapers()[0].titleText.text()
    cDeleteFirstPaper(widget, qtbot)
    cAddPaper(widget, bibcode, qtbot)
    assert widget.rightPanel.titleText.text() == title


def test_adding_paper_scrolls_to_show_paper(qtbot, db_empty, monkeypatch):
    # add a bunch of papers, to fill the available area, then add the last in
    # chronological order (so it will be  at the bottom), then see where the bar is.
    # I had problems getting this test to actually pass. The scroll.value() is sometimes
    # zero even when the scroll is not at the top (tested via interface). So we need
    # to add a lot of papers to make sure we have enough margin to make the end
    # significantly nonzero. But this takes forever (and still failed on remote tests),
    # so I'll just check that the correct attribute gets called
    calls = []
    monkeypatch.setattr(
        QScrollArea, "ensureWidgetVisible", lambda x, y: calls.append(1)
    )
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, u.mine_recent.bibcode, qtbot)
    # scroll = widget.papersList.verticalScrollBar()
    # assert scroll.value() > 0
    assert calls == [1]


def test_adding_paper_includes_tag_selected_in_left_panel(qtbot, db_empty):
    db_empty.add_new_tag("test")
    db_empty.add_paper(u.mine.bibcode)
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.tags[0].label.text() == "test"
    cClick(widget.tagsList.tags[0], qtbot)
    cAddPaper(widget, u.tremonti.bibcode, qtbot)
    assert db_empty.get_paper_tags(u.tremonti.bibcode) == ["test"]
    assert widget.rightPanel.tagText.text() == "Tags: test"


def test_adding_bad_paper_shows_error_formatting_of_textedit(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    assert widget.searchBar.property("error") is True


def test_adding_bad_paper_shows_error_text(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    assert widget.searchBarErrorText.isHidden() is False
    assert (
        widget.searchBarErrorText.text() == "This paper was not found in ADS. "
        "If it was just added to the arXiv, ADS may not have registered it."
    )


def test_adding_bad_paper_hides_add_button(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    assert widget.addButton.isHidden() is True


def test_adding_bad_paper_hides_import_button(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    assert widget.importButton.isHidden() is True


def test_adding_bad_arXiv_paper_shows_error_text(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    # Use future arXiv paper from 2035
    cAddPaper(widget, "https://arxiv.org/abs/3501.00001", qtbot)
    assert widget.searchBarErrorText.isHidden() is False
    assert (
        widget.searchBarErrorText.text() == "This paper was not found in ADS. "
        "If it was just added to the arXiv, ADS may not have registered it."
    )


def test_search_bar_and_error_text_have_almost_same_height(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    # add a bad paper, which is when this situation arises
    cAddPaper(widget, "nonsense", qtbot)
    height_ratio = widget.searchBarErrorText.height() / widget.searchBar.height()
    assert 0.8 < height_ratio < 1.3


def test_search_bar_and_error_text_are_much_shorter_than_title(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    # add a bad paper, which is when this situation arises
    cAddPaper(widget, "nonsense", qtbot)
    assert widget.searchBar.height() < 0.6 * widget.title.height()
    assert widget.searchBarErrorText.height() < 0.6 * widget.title.height()


def test_import_button_height_during(qtbot, db_empty, monkeypatch):
    # when I first tested this it took up the whole screen for some reason
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.importResultText.height() < 50
    file_loc.unlink()


def test_bad_paper_error_formatting_of_textedit_reset_after_clicking(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBar.property("error") is False


def test_bad_paper_error_message_of_textedit_reset_after_any_clicking(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBarErrorText.isHidden() is True


def test_bad_paper_add_button_reshown_after_any_clicking(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.addButton.isHidden() is False


def test_bad_paper_import_button_reshown_after_any_clicking(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.importButton.isHidden() is False


def test_bad_paper_error_textedit_formatting_reset_after_editing_text(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    cEnterText(widget.searchBar, "nonsens", qtbot)
    assert widget.searchBar.property("error") is False


def test_bad_paper_error_message_of_textedit_reset_after_editing_text(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    cEnterText(widget.searchBar, "nonsens", qtbot)
    assert widget.searchBarErrorText.isHidden() is True


def test_bad_paper_buttons_reshown_after_editing_text(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cAddPaper(widget, "nonsense", qtbot)
    cEnterText(widget.searchBar, "nonsens", qtbot)
    assert widget.addButton.isHidden() is False
    assert widget.importButton.isHidden() is False


def test_adding_paper_does_not_clear_search_bar_if_already_in_library(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert widget.searchBar.text() == u.mine.bibcode


def test_adding_duplicate_paper_shows_error_formatting_of_textedit(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert widget.searchBar.property("error") is True


def test_adding_duplicate_paper_shows_error_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert widget.searchBarErrorText.isHidden() is False
    assert widget.searchBarErrorText.text() == "This paper is already in the library."


def test_adding_duplicate_paper_hides_buttons(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert widget.addButton.isHidden() is True
    assert widget.importButton.isHidden() is True


def test_duplicate_error_formatting_of_textedit_reset_after_any_clicking(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBar.property("error") is False


def test_duplicate_error_message_of_textedit_reset_after_any_clicking(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBarErrorText.isHidden() is True


def test_duplicate_buttons_reshown_after_any_clicking(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.addButton.isHidden() is False
    assert widget.importButton.isHidden() is False


def test_duplicate_error_formatting_of_textedit_reset_after_editing_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    cEnterText(widget.searchBar, "s", qtbot)
    assert widget.searchBar.property("error") is False


def test_duplicate_error_message_of_textedit_reset_after_editing_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    cEnterText(widget.searchBar, "s", qtbot)
    assert widget.searchBarErrorText.isHidden() is True


def test_duplicate_buttons_reshown_after_editing_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cAddPaper(widget, u.mine.bibcode, qtbot)
    cEnterText(widget.searchBar, "s", qtbot)
    assert widget.addButton.isHidden() is False
    assert widget.importButton.isHidden() is False


def test_adding_paper_does_not_clear_search_bar_if_bad_ads_key(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    # need to use a paper that's not already stored in my ADS cache
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.searchBar.text() == u.used_for_no_ads_key.url


def test_adding_paper_bad_ads_key_shows_error_in_textedit(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.searchBar.property("error") is True


def test_adding_paper_bad_ads_key_shows_error_text(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.searchBarErrorText.isHidden() is False
    assert (
        widget.searchBarErrorText.text() == "You don't have an ADS key set. "
        "See this repository readme for more, then restart this application"
    )


def test_adding_paper_no_ads_key_hides_buttons(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.addButton.isHidden() is True
    assert widget.importButton.isHidden() is True


def test_bad_ads_key_error_reset_after_any_clicking(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBar.property("error") is False


def test_bad_ads_key_error_hidden_after_any_clicking(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBarErrorText.isHidden() is True


def test_no_ads_key_buttons_reshown_after_clicking(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    widget.searchBar.setCursorPosition(0)
    assert widget.addButton.isHidden() is False
    assert widget.importButton.isHidden() is False


def test_bad_ads_key_error_formatting_reset_after_editing_text(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    cEnterText(widget.searchBar, "s", qtbot)
    assert widget.searchBar.property("error") is False


def test_bad_ads_key_error_message_reset_after_editing_text(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    cEnterText(widget.searchBar, "s", qtbot)
    assert widget.searchBarErrorText.isHidden() is True


def test_no_ads_key_add_button_reshown_after_editing_text(qtbot, db_empty_bad_ads):
    widget = cInitialize(qtbot, db_empty_bad_ads)
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    cEnterText(widget.searchBar, "s", qtbot)
    assert widget.addButton.isHidden() is False
    assert widget.importButton.isHidden() is False


def test_adding_paper_doesnt_clear_search_bar_no_queries(qtbot, db_empty, monkeypatch):
    def out_of_queries_dummy(**kwargs):
        raise ads.exceptions.APIResponseError("Too many requests")

    monkeypatch.setattr(ads, "SearchQuery", out_of_queries_dummy)
    widget = cInitialize(qtbot, db_empty)
    # need to use a paper that's not already stored in my ADS cache
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.searchBar.text() == u.used_for_no_ads_key.url


def test_adding_paper_no_queries_shows_error_in_textedit(qtbot, db_empty, monkeypatch):
    def out_of_queries_dummy(**kwargs):
        raise ads.exceptions.APIResponseError("Too many requests")

    monkeypatch.setattr(ads, "SearchQuery", out_of_queries_dummy)
    widget = cInitialize(qtbot, db_empty)
    # need to use a paper that's not already stored in my ADS cache
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.searchBar.property("error") is True


def test_adding_paper_no_queries_shows_error_text(qtbot, db_empty, monkeypatch):
    def out_of_queries_dummy(**kwargs):
        raise ads.exceptions.APIResponseError("Too many requests")

    monkeypatch.setattr(ads, "SearchQuery", out_of_queries_dummy)
    widget = cInitialize(qtbot, db_empty)
    # need to use a paper that's not already stored in my ADS cache
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.searchBarErrorText.isHidden() is False
    assert (
        widget.searchBarErrorText.text()
        == "ADS has cut you off, you have sent too many requests today. "
        "Try again in ~24 hours"
    )


def test_adding_paper_other_ads_error_shows_error_text(qtbot, db_empty, monkeypatch):
    def error_dummy(**kwargs):
        raise ads.exceptions.APIResponseError("Something weird")

    monkeypatch.setattr(ads, "SearchQuery", error_dummy)
    widget = cInitialize(qtbot, db_empty)
    # need to use a paper that's not already stored in my ADS cache
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.searchBarErrorText.isHidden() is False
    assert (
        widget.searchBarErrorText.text()
        == "Something has gone wrong with the connection to ADS. Full error:\n"
        "'Something weird'"
    )


def test_adding_paper_no_internet_shows_error_text(qtbot, db_empty, monkeypatch):
    def error_dummy(**kwargs):
        raise requests.exceptions.ConnectionError("Max retries exceeded with url")

    monkeypatch.setattr(ads, "SearchQuery", error_dummy)
    widget = cInitialize(qtbot, db_empty)
    # need to use a paper that's not already stored in my ADS cache
    cAddPaper(widget, u.used_for_no_ads_key.url, qtbot)
    assert widget.searchBarErrorText.isHidden() is False
    assert widget.searchBarErrorText.text() == "No internet connection"


def test_paper_cannot_be_added_twice(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert len(widget.papersList.getPapers()) == 0
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert len(widget.papersList.getPapers()) == 1
    # add it again
    cAddPaper(widget, u.mine.bibcode, qtbot)
    assert len(widget.papersList.getPapers()) == 1


# =============
# update system
# =============
def test_db_update_reflected_in_interface(qtbot, db_update):
    widget = cInitialize(qtbot, db_update)
    cite_strings = [paper.citeText.text() for paper in widget.papersList.getPapers()]
    assert "Brown, Gnedin, Li, 2018, ApJ, 864, 94" in cite_strings
    assert "Brown, Gnedin, Li, 2022, arXiv:1804.09819" not in cite_strings
    assert "Brown, Gnedin, 2022, MNRAS, 514, 280" in cite_strings
    assert "Brown, Gnedin, 2022, arXiv:2203.00559" not in cite_strings


# =============
# import system
# =============
def test_clicking_import_button_asks_user(qtbot, db_empty, monkeypatch):
    get_file_calls = []

    def mock_get_file(filter="", dir=""):
        get_file_calls.append(1)
        return __file__, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    assert get_file_calls == [1]
    db_empty._failure_file_loc(Path(__file__)).unlink()  # remove failure files


def test_clicking_import_and_cancelling_does_no_import(qtbot, db_empty, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileNoResponse)
    calls = []
    monkeypatch.setattr(Database, "import_bibtex", lambda s, b: calls.append(b))
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.importButton, qtbot)
    assert calls == []


def test_import_disables_main_window_during(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.splitter.isEnabled() is False
    file_loc.unlink()  # delete before tests may fail
    assert widget.splitter.isEnabled() is True


def test_import_disables_theme_switcher(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.title.isEnabled() is False
    file_loc.unlink()  # delete before tests may fail
    assert widget.title.isEnabled() is True


def test_import_changes_qss_main_window_during(qtbot, db_empty, monkeypatch):
    # add some papers and tags to check that they're faded
    db_empty.add_new_tag("test")
    db_empty.add_paper(u.juan.bibcode)
    db_empty.add_paper(u.tremonti.bibcode)
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.splitter.property("faded") is True
        for t in widget.tagsList.tags:
            assert t.property("faded") is True
        for p in widget.papersList.getPapers():
            assert p.property("faded") is True
    file_loc.unlink()  # delete before tests may fail
    assert widget.splitter.property("faded") is False
    for t in widget.tagsList.tags:
        assert t.property("faded") is False
    for p in widget.papersList.getPapers():
        assert p.property("faded") is False


def test_import_shows_progress_bar_during(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.importProgressBar.isHidden() is False
    file_loc.unlink()  # delete before tests may fail
    assert widget.importProgressBar.isHidden() is True


def test_import_shows_explanatory_text_during(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.importResultText.isHidden() is False
        assert widget.importResultText.text() == "Please wait until the import finishes"
    file_loc.unlink()


def test_import_hides_search_bar_buttons_during(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.searchBar.isHidden() is True
        assert widget.addButton.isHidden() is True
        assert widget.importButton.isHidden() is True
    file_loc.unlink()  # delete before tests may fail


def test_import_progressbar_starts_at_zero(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.importProgressBar.value() == 0
    file_loc.unlink()  # delete before tests may fail


def test_import_progressbar_has_correct_max_value(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    n_lines = len(open(file_loc, "r").readlines())
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
        assert widget.importProgressBar.value() == 0
        assert widget.importProgressBar.maximum() == n_lines
    file_loc.unlink()  # delete before tests may fail


def test_import_progressbar_ends_at_number_of_lines(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    # I don't want to end at the maximum since after this finishes we still need to
    # add papers to the interface and such.
    assert widget.importProgressBar.value() == widget.importProgressBar.maximum()


def test_import_shows_results_text_after(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert widget.importResultText.isHidden() is False


def test_import_shows_results_dismiss_button_after(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert widget.importResultDismissButton.isHidden() is False


def test_import_hides_search_bar_and_buttons_after(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert widget.searchBar.isHidden() is True
    assert widget.addButton.isHidden() is True
    assert widget.importButton.isHidden() is True


def test_import_dismiss_button_restores_default_state(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    cClick(widget.importResultDismissButton, qtbot)
    assert widget.searchBar.isHidden() is False
    assert widget.addButton.isHidden() is False
    assert widget.importButton.isHidden() is False
    assert widget.importResultText.isHidden() is True
    assert widget.importResultDismissButton.isHidden() is True


def test_clicking_import_button_adds_paper_to_database(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert widget.db.get_all_bibcodes() == [u.mine.bibcode]


def test_import_finish_adds_paper_to_interface(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert widget.papersList.getPapers()[0].bibcode == u.mine.bibcode


def test_import_results_text_no_papers_found(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch("   ")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert widget.importResultText.text() == "Import results: No papers found"


def test_import_results_text_one_success(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert (
        widget.importResultText.text()
        == "Import results: 1 paper found, 1 added successfully"
    )


def test_import_results_text_one_duplicate(qtbot, db_empty, monkeypatch):
    db_empty.add_paper(u.mine.bibcode)
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert (
        widget.importResultText.text()
        == "Import results: 1 paper found, 1 duplicate skipped"
    )


def test_import_results_text_two_duplicates(qtbot, db_temp, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex, u.tremonti.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_temp)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert (
        widget.importResultText.text()
        == "Import results: 2 papers found, 2 duplicates skipped"
    )


def test_import_results_text_one_error(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(
        "@ARTICLE{1957RvMP...29..547B,\n"
        " author = {{Burbidge}, E. Margaret},\n"
        '  title = "{Synthesis of the Elements in Stars}",\n'
        "journal = {Reviews of Modern Physics},\n"
        "   year = 1959,\n"  # edited to be incorrect
        "}"
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    fail_file = db_empty._failure_file_loc(file_loc)
    fail_file.unlink()  # remove failure files
    shown_text = widget.importResultText.text()
    assert shown_text.startswith(
        "Import results: 1 paper found, 1 failure\nFailed entries written to "
    )
    assert Path(shown_text.split()[-1]).expanduser() == fail_file


def test_import_results_text_two_errors(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(
        "@ARTICLE{1957RvMP...29..547B,\n"
        " author = {{Burbidge}, E. Margaret},\n"
        '  title = "{Synthesis of the Elements in Stars}",\n'
        "journal = {Reviews of Modern Physics},\n"
        "   year = 1959,\n"  # changed to be an error
        "}",
        "@BOOK{2010gfe..book.....M,\n"
        "   author = {{Mo}, Houjun and {van den Bosch}, Frank C. and {White}, Simon},\n"
        '    title = "{Galaxy Formation and Evolution}",\n'
        "     year = 2014,\n"  # changed to be an error
        "}\n"
        "}",
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    fail_file = db_empty._failure_file_loc(file_loc)
    fail_file.unlink()  # remove failure files
    shown_text = widget.importResultText.text()
    assert shown_text.startswith(
        "Import results: 2 papers found, 2 failures\n" f"Failed entries written to "
    )
    assert Path(shown_text.split()[-1]).expanduser() == fail_file


def test_import_results_text_one_success_one_duplicate(qtbot, db_empty, monkeypatch):
    db_empty.add_paper(u.mine.bibcode)
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex, u.tremonti.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert (
        widget.importResultText.text()
        == "Import results: 2 papers found, 1 added successfully, 1 duplicate skipped"
    )


def test_import_results_text_one_success_one_failure(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(
        "@ARTICLE{1957RvMP...29..547B,\n"
        " author = {{Burbidge}, E. Margaret},\n"
        '  title = "{Synthesis of the Elements in Stars}",\n'
        "journal = {Reviews of Modern Physics},\n"
        "   year = 1959,\n"  # edited to be incorrect
        "}",
        u.mine.bibtex,
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    fail_file = db_empty._failure_file_loc(file_loc)
    fail_file.unlink()  # remove failure files
    shown_text = widget.importResultText.text()
    assert shown_text.startswith(
        "Import results: 2 papers found, 1 added successfully, 1 failure\n"
        f"Failed entries written to "
    )
    assert Path(shown_text.split()[-1]).expanduser() == fail_file


def test_import_results_text_one_duplicate_one_failure(qtbot, db_empty, monkeypatch):
    db_empty.add_paper(u.mine.bibcode)
    file_loc, test_func = create_bibtex_monkeypatch(
        "@ARTICLE{1957RvMP...29..547B,\n"
        " author = {{Burbidge}, E. Margaret},\n"
        '  title = "{Synthesis of the Elements in Stars}",\n'
        "journal = {Reviews of Modern Physics},\n"
        "   year = 1959,\n"  # edited to be incorrect
        "}",
        u.mine.bibtex,
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    fail_file = db_empty._failure_file_loc(file_loc)
    fail_file.unlink()  # remove failure files
    shown_text = widget.importResultText.text()
    assert shown_text.startswith(
        "Import results: 2 papers found, 1 duplicate skipped, 1 failure\n"
        f"Failed entries written to "
    )
    assert Path(shown_text.split()[-1]).expanduser() == fail_file


def test_import_results_text_one_success_one_dup_one_fail(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(
        "@ARTICLE{1957RvMP...29..547B,\n"
        " author = {{Burbidge}, E. Margaret},\n"
        '  title = "{Synthesis of the Elements in Stars}",\n'
        "journal = {Reviews of Modern Physics},\n"
        "   year = 1959,\n"  # edited to be incorrect
        "}",
        u.mine.bibtex,
        u.mine.bibtex,
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    fail_file = db_empty._failure_file_loc(file_loc)
    fail_file.unlink()  # remove failure files
    shown_text = widget.importResultText.text()
    assert shown_text.startswith(
        "Import results: "
        "3 papers found, 1 added successfully, 1 duplicate skipped, 1 failure\n"
        f"Failed entries written to "
    )
    assert Path(shown_text.split()[-1]).expanduser() == fail_file


def test_import_results_shown_file_location_shorthand(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(
        "@ARTICLE{1957RvMP...29..547B,\n"
        " author = {{Burbidge}, E. Margaret},\n"
        '  title = "{Synthesis of the Elements in Stars}",\n'
        "journal = {Reviews of Modern Physics},\n"
        "   year = 1959,\n"  # edited to be incorrect
        "}"
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    fail_file = db_empty._failure_file_loc(file_loc)
    fail_file.unlink()  # remove failure files
    shown_path = widget.importResultText.text().split()[-1]
    # ~ isn't part of Windows, so we need to be careful about how we check
    if sys.platform != "win32":
        assert shown_path.startswith("~/")


def test_import_after_finished_adds_new_tag_to_interface(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex, u.tremonti.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    tag_names = [t.label.text() for t in widget.tagsList.tags]
    assert f"Import {file_loc.name}" in tag_names


def test_import_after_finished_clicks_new_tag(qtbot, db_empty, monkeypatch):
    db_empty.add_new_tag("test")
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex, u.tremonti.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert widget.tagsList.showAllButton.property("is_highlighted") is False
    for tag in widget.tagsList.tags:
        if tag.label.text() == f"Import {file_loc.name}":
            assert tag.property("is_highlighted") is True
        else:
            assert tag.property("is_highlighted") is False


def test_import_imported_papers_are_shown_in_center(qtbot, db_empty, monkeypatch):
    db_empty.add_paper(u.juan.bibcode)
    db_empty.add_paper(u.mine.bibcode)
    db_empty.add_paper(u.forbes.bibcode)
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex, u.tremonti.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    seen_papers = [p.bibcode for p in widget.papersList.getPapers() if not p.isHidden()]
    assert seen_papers == [u.tremonti.bibcode, u.mine.bibcode]


def test_import_new_tag_is_shown_in_right_panel(qtbot, db_empty, monkeypatch):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.add_new_tag("Unread")
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex, u.tremonti.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()  # delete before tests may fail
    assert widget.rightPanel.tagText.text() == f"Tags: Import {file_loc.name}"


def test_import_cite_key_is_shown_correctly(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(
        u.mine.bibtex.replace("@ARTICLE{2018ApJ...864...94B", "@ARTICLE{test")
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.citeKeyText.text() == "Citation Keyword: test"


def test_import_twice_is_possible(qtbot, db_empty, monkeypatch):
    file_loc, test_func = create_bibtex_monkeypatch(u.mine.bibtex)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", test_func)
    widget = cInitialize(qtbot, db_empty)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    cClick(widget.importResultDismissButton, qtbot)
    with qtbot.waitSignal(widget.importWorker.signals.finished, timeout=10000):
        cClick(widget.importButton, qtbot)
    file_loc.unlink()
    assert (
        widget.importResultText.text()
        == "Import results: 1 paper found, 1 duplicate skipped"
    )


# ======================================================================================
#
# test right panel
#
# ======================================================================================
# =============
# initial state
# =============
def test_right_panel_title_is_empty_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.titleText.text() == ""


def test_right_panel_cite_text_is_empty_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.citeText.text() == ""


def test_right_panel_abstract_is_placeholder_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    true_text = "Click on a paper to show its details here"
    assert widget.rightPanel.abstractText.text() == true_text


def test_right_panel_tags_is_empty_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.tagText.text() == ""


def test_right_panel_title_text_has_correct_font_family(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.titleText.font().family() == "Cabin"


def test_right_panel_cite_text_has_correct_font_family(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.citeText.font().family() == "Cabin"


def test_right_panel_abstract_text_has_correct_font_family(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.abstractText.font().family() == "Cabin"


def test_right_panel_tag_text_has_correct_font_family(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.tagText.font().family() == "Cabin"


def test_right_panel_title_text_has_correct_font_size(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.titleText.font().pointSize() == 20


def test_right_panel_cite_text_has_correct_font_size(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.citeText.font().pointSize() == 16


def test_right_panel_abstract_text_has_correct_font_size(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.abstractText.font().pointSize() == 14


def test_right_panel_tag_text_has_correct_font_size(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.tagText.font().pointSize() == 14


def test_right_panel_title_text_has_word_wrap_on(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.titleText.wordWrap()


def test_right_panel_cite_text_has_word_wrap_on(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.citeText.wordWrap()


def test_right_panel_abstract_text_has_word_wrap_on(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.abstractText.wordWrap()


def test_right_panel_tag_text_has_word_wrap_on(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.tagText.wordWrap()


def test_right_panel_pdf_text_has_word_wrap_on(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.pdfText.wordWrap()


def test_right_panel_cite_key_has_word_wrap_on(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.citeKeyText.wordWrap()


def test_right_panel_title_is_copyable(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert (
        widget.rightPanel.titleText.textInteractionFlags() == Qt.TextSelectableByMouse
    )


def test_right_panel_cite_string_is_copyable(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.citeText.textInteractionFlags() == Qt.TextSelectableByMouse


def test_right_panel_abstract_is_copyable(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert (
        widget.rightPanel.abstractText.textInteractionFlags()
        == Qt.TextSelectableByMouse
    )


def test_right_panel_cite_key_is_copyable(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert (
        widget.rightPanel.citeKeyText.textInteractionFlags() == Qt.TextSelectableByMouse
    )


def test_right_panel_pdf_text_is_copyable(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.pdfText.textInteractionFlags() == Qt.TextSelectableByMouse


def test_right_panel_notes_is_copyable(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert (
        widget.rightPanel.userNotesText.textInteractionFlags()
        == Qt.TextSelectableByMouse
    )


def test_right_panel_tags_text_is_not_copyable(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.tagText.textInteractionFlags() != Qt.TextSelectableByMouse


def test_tags_selection_checkboxes_is_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    for tag in widget.rightPanel.getTagCheckboxes():
        assert tag.isHidden() is True


def test_tags_selection_edit_button_is_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.editTagsButton.isHidden() is True


def test_tags_selection_done_editing_button_is_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.doneEditingTagsButton.isHidden() is True


def test_copy_bibtex_button_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.copyBibtexButton.isHidden() is True


def test_first_delete_paper_button_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is True


def test_second_delete_paper_button_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is True


def test_second_delete_cancel_paper_button_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is True


def test_open_ads_button_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.adsButton.isHidden() is True


def test_user_notes_fields_are_not_shown_on_initialization(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    assert widget.rightPanel.userNotesText.isHidden() is True
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is True
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_user_notes_has_word_wrap_on(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.userNotesText.wordWrap()


def test_edit_user_notes_button_has_correct_text(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.userNotesTextEditButton.text() == "Edit Notes"


def test_user_notes_finished_editing_button_has_correct_text(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert (
        widget.rightPanel.userNotesTextEditFinishedButton.text() == "Done Editing Notes"
    )


def test_spacers_are_hidden_at_initialization(qtbot, db):
    widget = cInitialize(qtbot, db)
    for spacer in widget.rightPanel.spacers:
        assert spacer.isHidden() is True


def test_edit_citation_keyword_button_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True


def test_citation_keyword_text_shown_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.citeKeyText.isHidden() is True


def test_edit_citation_keyword_edit_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True


def test_citation_keyword_text_has_placeholder_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    correct_placeholder = "e.g. yourname_etal_2022"
    assert widget.rightPanel.editCiteKeyEntry.placeholderText() == correct_placeholder


def test_edit_citation_keyword_edit_error_text_hidden_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_button_text_is_correct(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.editCiteKeyButton.text() == "Edit Citation Keyword"


def test_paper_pdf_buttons_are_hidden_at_start(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.rightPanel.pdfText.isHidden() is True
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True


def test_paper_pdf_buttons_have_correct_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.rightPanel.pdfOpenButton.text() == "Open this paper's PDF"
    assert widget.rightPanel.pdfClearButton.text() == "Clear the selected PDF"
    assert widget.rightPanel.pdfChooseLocalFileButton.text() == "Choose a local PDF"
    assert widget.rightPanel.pdfDownloadButton.text() == "Download the PDF"


# ==========================================
# paper details added correctly when clicked
# ==========================================
def test_clicking_on_paper_puts_title_in_right_panel(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    assert widget.rightPanel.titleText.text() in [u.mine.title, u.tremonti.title]


def test_clicking_on_paper_puts_cite_string_in_right_panel(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    possible_cites = [
        db.get_cite_string(u.mine.bibcode),
        db.get_cite_string(u.tremonti.bibcode),
    ]
    assert widget.rightPanel.citeText.text() in possible_cites


def test_clicking_on_paper_puts_abstract_in_right_panel(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    assert widget.rightPanel.abstractText.text() in [
        u.mine.abstract,
        u.tremonti.abstract,
    ]


def test_clicking_on_paper_puts_tags_in_right_panel(qtbot, db_no_tags):
    widget = cInitialize(qtbot, db_no_tags)
    # Add some tags to the database - this is tested below
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        cAddTag(widget, tag, qtbot)

    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    # add one of the tags to this paper - this is done through the database, not the
    # actual adding tags functionality - that will be tested below
    db_no_tags.tag_paper(paper.bibcode, "T1")
    db_no_tags.tag_paper(paper.bibcode, "T3")
    db_no_tags.tag_paper(paper.bibcode, "T5")
    # then click on the paper
    cClick(paper, qtbot)
    assert widget.rightPanel.tagText.text() == "Tags: T1, T3, T5"


def test_clicking_on_paper_with_no_tags_puts_default_in_right_panel(qtbot, db_no_tags):
    widget = cInitialize(qtbot, db_no_tags)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.tagText.text() == "Tags: None"


def test_clicking_on_paper_scroll_is_at_top(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.verticalScrollBar().value() == 0
    assert widget.rightPanel.horizontalScrollBar().value() == 0


def test_clicking_on_paper_scroll_is_at_top_even_after_scrolling_down(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    widget.rightPanel.verticalScrollBar().setValue(100)
    assert widget.rightPanel.verticalScrollBar().value() == 100
    cClick(widget.papersList.getPapers()[1], qtbot)
    assert widget.rightPanel.verticalScrollBar().value() == 0


def test_clicking_on_same_paper_doesnt_adjust_scroll_position(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    widget.rightPanel.verticalScrollBar().setValue(100)
    assert widget.rightPanel.verticalScrollBar().value() == 100
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.verticalScrollBar().value() == 100


def test_tags_selection_edit_button_appears_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.editTagsButton.isHidden() is False


def test_tags_selection_done_editing_button_doesnt_appear_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.doneEditingTagsButton.isHidden() is True


def test_tags_selection_checkboxes_doesnt_appear_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    for tag in widget.rightPanel.getTagCheckboxes():
        assert tag.isHidden() is True


def test_copy_bibtex_button_appears_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.copyBibtexButton.isHidden() is False


def test_first_delete_paper_button_appears_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is False


def test_second_delete_paper_button_does_not_appear_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is True


def test_second_delete_paper_cancel_button_doesnt_appear_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is True


def test_open_ads_button_appears_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.adsButton.isHidden() is False


def test_user_notes_are_appropriately_shown_once_paper_clicked(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.userNotesText.isHidden() is False
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is False
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_spacers_are_shown_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    for spacer in widget.rightPanel.spacers:
        assert spacer.isHidden() is False


def test_edit_citation_keyword_button_shown_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False


def test_citation_keyword_text_shown_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.citeKeyText.isHidden() is False


def test_edit_citation_keyword_edit_hidden_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True


def test_edit_citation_keyword_edit_error_text_hidden_when_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


# =========================================================================
# handling paper pdfs -- double clicking from center panel tested elsewhere
# =========================================================================
def test_paper_pdf_buttons_show_paper_clicked_with_local_file(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is False
    assert widget.rightPanel.pdfClearButton.isHidden() is False
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True


def test_paper_pdf_buttons_show_paper_clicked_without_local_file(qtbot, db_temp):
    # no local files are set in the temp database
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_buttons_show_paper_clicked_nonexistent_local_file(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "nonexistent_file.pdf")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_buttons_update_database_if_file_doesnt_exist(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "nonexistent_file.pdf")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "local_file") is None


def test_paper_pdf_text_has_correct_text_with_local_file(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # check that the shown path uses ~ and resolves to the correct location
    # ~ isn't part of Windows, so we need to be careful about how we check
    shown_path = widget.rightPanel.pdfText.text().replace("PDF Location: ", "")
    if sys.platform != "win32":
        assert shown_path.startswith("~/")
    assert Path(shown_path).expanduser() == Path(__file__).resolve()


def test_paper_pdf_text_has_correct_text_without_local_file(qtbot, db_temp):
    # no local files are set in the temp database
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfText.text() == "No PDF location set"


def test_paper_pdf_text_has_correct_text_with_nonexistent_local_file(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "nonexistent_file.pdf")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfText.text() == "No PDF location set"


def test_paper_pdf_add_local_file_asks_user(qtbot, db_temp, monkeypatch):
    get_file_calls = []

    def mock_get_file(filter="", dir=""):
        get_file_calls.append(1)
        return __file__, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)
    assert get_file_calls == [1]


def test_paper_pdf_add_local_file_doesnt_add_if_cancelled(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)
    assert (
        db_temp.get_paper_attribute(
            widget.papersList.getPapers()[0].bibcode, "local_file"
        )
        is None
    )


def test_paper_pdf_add_local_file_doesnt_add_nonexistent(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileNonexistent)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)
    assert (
        db_temp.get_paper_attribute(
            widget.papersList.getPapers()[0].bibcode, "local_file"
        )
        is None
    )


def test_paper_pdf_add_local_file_adds_it_to_database(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileExists)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)
    assert (
        db_temp.get_paper_attribute(
            widget.papersList.getPapers()[0].bibcode, "local_file"
        )
        == __file__
    )


def test_paper_pdf_add_local_file_updates_text(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileExists)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)
    # check that the shown path uses ~ and resolves to the correct location
    shown_path = widget.rightPanel.pdfText.text().replace("PDF Location: ", "")
    if sys.platform != "win32":
        assert shown_path.startswith("~/")
    assert Path(shown_path).expanduser() == Path(__file__).resolve()


def test_paper_pdf_add_local_file_cancel_no_text_diff(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)
    assert widget.rightPanel.pdfText.text() == f"No PDF location set"


def test_paper_pdf_add_local_file_nonexistent_no_text_diff(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileNonexistent)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)
    assert widget.rightPanel.pdfText.text() == f"No PDF location set"


def test_paper_pdf_add_local_file_resets_buttons_if_good(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileExists)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)

    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is False
    assert widget.rightPanel.pdfClearButton.isHidden() is False
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True


def test_paper_pdf_add_local_file_cancel_keep_buttons(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)

    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_add_local_file_nonexistent_keep_buttons(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileNonexistent)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)

    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_open_pdf_button_opens_pdf(qtbot, db_empty, monkeypatch):
    # just record the files that were attempted to be opened
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfOpenButton, qtbot)
    assert open_calls == [f"file:{__file__}"]


def test_paper_pdf_open_bad_pdf_doesnt_open(qtbot, db_empty, monkeypatch):
    # just record the files that were attempted to be opened
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    shutil.copy2(__file__, "example.py")
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "example.py")

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    Path("example.py").unlink()
    cClick(widget.rightPanel.pdfOpenButton, qtbot)
    assert open_calls == []


def test_paper_pdf_open_bad_pdf_resets_buttons(qtbot, db_empty, monkeypatch):
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    shutil.copy2(__file__, "example.py")
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "example.py")

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    Path("example.py").unlink()
    cClick(widget.rightPanel.pdfOpenButton, qtbot)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_open_bad_pdf_resets_database(qtbot, db_empty, monkeypatch):
    # just record the files that were attempted to be opened
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    shutil.copy2(__file__, "example.py")
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "example.py")

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    Path("example.py").unlink()
    cClick(widget.rightPanel.pdfOpenButton, qtbot)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "local_file") is None


def test_paper_pdf_buttons_hidden_when_paper_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # don't use convenience function, for clarity
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    cClick(widget.rightPanel.secondDeletePaperButton, qtbot)

    assert widget.rightPanel.pdfText.isHidden() is True
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True


def test_download_pdf_button_asks_user(qtbot, db_temp, monkeypatch):
    # record the files that were attempted to be used to save a file
    get_file_calls = []

    def mock_get_file(filter="", caption="", dir=""):
        get_file_calls.append(1)
        return str(mSaveLocPDF), "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = cInitialize(qtbot, db_temp)

    # record files where we attempted to download something
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert get_file_calls == [1]
    assert download_links == [
        "https://ui.adsabs.harvard.edu/link_gateway/2004ApJ...613..898T/EPRINT_PDF"
    ] or download_links == [
        "https://ui.adsabs.harvard.edu/link_gateway/2004ApJ...613..898T/PUB_PDF"
    ]


def test_download_pdf_button_suggests_filename(qtbot, db_empty, monkeypatch):
    # record the files that were attempted to be used to save a file
    dir_suggestions = []

    def mock_get_file(filter="", caption="", dir=""):
        dir_suggestions.append(dir)
        return "", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    db_empty.add_paper(u.mine.bibcode)
    widget = cInitialize(qtbot, db_empty)

    # record files where we attempted to download something
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert dir_suggestions == [str(Path.home() / "brown_gnedin_li_2018_apj_864_94.pdf")]


def test_download_pdf_button_actually_downloads_paper(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidPDF)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert mSaveLocPDF.is_file()
    assert mSaveLocPDF.stat().st_size > 1e6  # 1 Mb, in bytes
    mSaveLocPDF.unlink()  # remove the file we just downloaded


def test_download_pdf_button_actually_downloads_old_paper(qtbot, db_empty, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidPDF)
    # this paper has no publisher or arXiv pdfs even available, but does have an
    # ADS pdf
    db_empty.add_paper("1971ApJ...168..327S")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert mSaveLocPDF.is_file()
    assert mSaveLocPDF.stat().st_size > 1e6  # 1 Mb, in bytes
    mSaveLocPDF.unlink()  # remove the file we just downloaded


def test_download_pdf_button_no_suffix_downloads_paper(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidNoSuffix)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert mSaveLocPDF.is_file()
    assert mSaveLocPDF.stat().st_size > 1e6  # 1 Mb, in bytes
    mSaveLocPDF.unlink()  # remove the file we just downloaded


def test_download_pdf_button_can_be_cancelled(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    # record the files where we attemped to save something
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert download_links == []


def test_download_pdf_button_updates_database(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidPDF)
    widget = cInitialize(qtbot, db_temp)
    # I cannot monkeypatch the downloading, since the code checks if the PDF exists
    # when setting the buttons
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert db_temp.get_paper_attribute(
        widget.papersList.getPapers()[0].bibcode, "local_file"
    ) == str(mSaveLocPDF)
    mSaveLocPDF.unlink()


def test_download_pdf_button_no_suffix_updates_database(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidNoSuffix)
    widget = cInitialize(qtbot, db_temp)
    # I cannot monkeypatch the downloading, since the code checks if the PDF exists
    # when setting the buttons
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert db_temp.get_paper_attribute(
        widget.papersList.getPapers()[0].bibcode, "local_file"
    ) == str(mSaveLocPDF)
    mSaveLocPDF.unlink()


def test_download_pdf_button_doesnt_update_db_if_cancelled(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert (
        db_temp.get_paper_attribute(
            widget.papersList.getPapers()[0].bibcode, "local_file"
        )
        == None
    )


def test_download_pdf_button_updates_buttons(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidPDF)
    widget = cInitialize(qtbot, db_temp)
    # I cannot monkeypatch the downloading, since the code checks if the PDF exists
    # when setting the buttons
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is False
    assert widget.rightPanel.pdfClearButton.isHidden() is False
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True
    mSaveLocPDF.unlink()


def test_download_pdf_button_cancel_doesnt_update_buttons(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_download_pdf_button_updates_text(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidPDF)
    widget = cInitialize(qtbot, db_temp)
    # I cannot monkeypatch the downloading, since the code checks if the PDF exists
    # when setting the buttons
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    # check that the shown path uses ~ and resolves to the correct location
    shown_path = widget.rightPanel.pdfText.text().replace("PDF Location: ", "")
    if sys.platform != "win32":
        assert shown_path.startswith("~/")
    assert Path(shown_path).expanduser() == mSaveLocPDF
    mSaveLocPDF.unlink()


def test_download_pdf_button_cancel_doesnt_reset_text(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert widget.rightPanel.pdfText.text() == "No PDF location set"


def test_download_pdf_doesnt_ask_user_if_none_available(qtbot, db_empty, monkeypatch):
    # add BBFH to the database, since it has no PDF
    db_empty.add_paper(u.bbfh.bibcode)
    # record if we asked the user.
    get_file_calls = []
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda x, y, z: get_file_calls.append(1)
    )

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert get_file_calls == []


def test_download_pdf_doesnt_download_if_none_available(qtbot, db_empty, monkeypatch):
    # add BBFH to the database, since it has no PDF
    db_empty.add_paper(u.bbfh.bibcode)
    widget = cInitialize(qtbot, db_empty)
    # record what we downloaded
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert download_links == []


def test_download_pdf_button_shows_error_message_no_pdf(qtbot, db_empty):
    # add BBFH to the database, since it has no PDF
    db_empty.add_paper(u.bbfh.bibcode)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert widget.rightPanel.pdfDownloadButton.text() == "Automatic Download Failed"


def test_download_pdf_button_error_resets_on_new_paper(qtbot, db_empty):
    # add BBFH to the database, since it has no PDF
    db_empty.add_paper(u.bbfh.bibcode)
    db_empty.add_paper(u.tremonti.bibcode)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert widget.rightPanel.pdfDownloadButton.text() == "Automatic Download Failed"
    cClick(widget.papersList.getPapers()[1], qtbot)
    assert widget.rightPanel.pdfDownloadButton.text() == "Download the PDF"


def test_clear_pdf_button_resets_buttons(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfClearButton, qtbot)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfClearButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_clear_pdf_button_updates_database(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "local_file") == __file__
    cClick(widget.rightPanel.pdfClearButton, qtbot)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "local_file") is None


def test_clear_pdf_button_updates_text(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.pdfClearButton, qtbot)
    assert widget.rightPanel.pdfText.text() == "No PDF location set"


# ====================
# modifying paper tags
# ====================
def test_right_panel_tags_should_list_all_tags_in_database(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get all tags in both the list and database, then check that they're the same
    db_tags = db.get_all_tags()
    list_tags = [t.text() for t in widget.rightPanel.getTagCheckboxes()]
    assert sorted(db_tags) == sorted(list_tags)


def test_right_panel_tags_checked_match_paper_that_is_selected(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get a random paper, we already tested that it has at least one tag
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    # go through each checkbox to verify the tag
    for tag in widget.rightPanel.getTagCheckboxes():
        if db.paper_has_tag(paper.bibcode, tag.text()):
            assert tag.isChecked()
        else:
            assert not tag.isChecked()


def test_tags_selection_edit_button_is_hidden_when_pressed(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    assert widget.rightPanel.editTagsButton.isHidden() is True


def test_tags_selection_done_editing_buttons_is_shown_when_edit_is_pressed(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    assert widget.rightPanel.doneEditingTagsButton.isHidden() is False


def test_tags_selection_edit_button_shown_again_when_done_editing_pressed(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    cClick(widget.rightPanel.doneEditingTagsButton, qtbot)
    assert widget.rightPanel.editTagsButton.isHidden() is False


def test_tags_selection_done_editing_button_is_hidden_when_pressed(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    cClick(widget.rightPanel.doneEditingTagsButton, qtbot)
    assert widget.rightPanel.doneEditingTagsButton.isHidden() is True


def test_tags_selection_checkboxes_are_unhidden_when_edit_is_pressed(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    for tag in widget.rightPanel.getTagCheckboxes():
        assert tag.isHidden() is False


def test_tags_selection_checkboxes_are_hidden_when_done_editing(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    cClick(widget.rightPanel.doneEditingTagsButton, qtbot)
    for tag in widget.rightPanel.getTagCheckboxes():
        assert tag.isHidden() is True


def test_checking_tag_in_checklist_adds_tag_to_paper_in_database(qtbot, db_no_tags):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_no_tags.add_new_tag(tag)
    widget = cInitialize(qtbot, db_no_tags)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    # this will show the tags in the right panel. Click on a few
    to_check = ["T1", "T3", "T4"]
    for tag_item in widget.rightPanel.getTagCheckboxes():
        if tag_item.text() in to_check:
            tag_item.setChecked(True)
    # Then check that these tags are listen in the database
    for tag in db_no_tags.get_all_tags():
        if tag in to_check:
            assert db_no_tags.paper_has_tag(paper.bibcode, tag) is True
        else:
            assert db_no_tags.paper_has_tag(paper.bibcode, tag) is False


def test_unchecking_tag_in_checklist_removes_tag_from_paper_in_db(qtbot, db_no_tags):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_no_tags.add_new_tag(tag)
    widget = cInitialize(qtbot, db_no_tags)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.getPapers()[0]
    # add all tags to this paper
    for tag in db_no_tags.get_all_tags():
        db_no_tags.tag_paper(paper.bibcode, tag)
    # click on the paper to show it in the right panel
    cClick(paper, qtbot)
    # click on the tags we want to remove
    to_uncheck = ["T1", "T3", "T4"]
    for tag_item in widget.rightPanel.getTagCheckboxes():
        if tag_item.text() in to_uncheck:
            tag_item.setChecked(False)
    # Then check that these tags are listen in the database
    for tag in db_no_tags.get_all_tags():
        if tag in to_uncheck:
            assert db_no_tags.paper_has_tag(paper.bibcode, tag) is False
        else:
            assert db_no_tags.paper_has_tag(paper.bibcode, tag) is True


def test_checking_tag_in_checklist_adds_tag_to_interface(qtbot, db_no_tags):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_no_tags.add_new_tag(tag)
    widget = cInitialize(qtbot, db_no_tags)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    # first double check that no tags are selected (is already be tested for elsewhere)
    assert widget.rightPanel.tagText.text() == "Tags: None"
    # this will show the tags in the right panel. Click on a few
    to_check = ["T1", "T3", "T4"]
    for tag_item in widget.rightPanel.getTagCheckboxes():
        if tag_item.text() in to_check:
            tag_item.setChecked(True)
    # click the done editing button
    cClick(widget.rightPanel.doneEditingTagsButton, qtbot)
    # Then check that these tags are listen in the interface
    assert widget.rightPanel.tagText.text() == "Tags: T1, T3, T4"


def test_unchecking_tag_in_checklist_removes_tag_from_interface(qtbot, db_no_tags):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_no_tags.add_new_tag(tag)
    widget = cInitialize(qtbot, db_no_tags)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.getPapers()[0]
    # add all tags to this paper
    for tag in db_no_tags.get_all_tags():
        db_no_tags.tag_paper(paper.bibcode, tag)
    # click on the paper to show it in the right panel
    cClick(paper, qtbot)
    # click on the tags we want to remove
    to_uncheck = ["T1", "T3", "T4"]
    for tag_item in widget.rightPanel.getTagCheckboxes():
        if tag_item.text() in to_uncheck:
            tag_item.setChecked(False)
    # click the done editing button
    cClick(widget.rightPanel.doneEditingTagsButton, qtbot)
    # Then check that these tags are not listed in the interface
    assert widget.rightPanel.tagText.text() == "Tags: T2, T5"


def test_tag_checkboxes_are_hidden_when_paper_clicked(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # click on a paper, then click the edit tags button
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    # click on a different paper
    cClick(widget.papersList.getPapers()[1], qtbot)
    # the tag edit checkboxes should all be hidden
    for t in widget.rightPanel.getTagCheckboxes():
        assert t.isHidden()


def test_done_editing_button_is_hidden_when_paper_clicked(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # click on a paper, then click the edit tags button
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    # click on a different paper
    cClick(widget.papersList.getPapers()[1], qtbot)
    # the tag edit checkboxes should all be hidden
    assert widget.rightPanel.doneEditingTagsButton.isHidden()


# ==============================================
# tags and their interaction with the left panel
# ==============================================
def test_paper_tag_list_is_sorted_alphabetically_not_case_sensitive(qtbot, db_empty):
    # set up tags to check
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    db_empty.add_paper(u.mine.bibcode)
    for t in tags:
        db_empty.add_new_tag(t)
        db_empty.tag_paper(u.mine.bibcode, t)

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    expected = "Tags: " + ", ".join(sorted(tags, key=lambda x: x.lower()))
    assert widget.rightPanel.tagText.text() == expected


def test_paper_tag_list_is_sorted_properly_after_modifying_tags(qtbot, db_empty):
    # set up tags to check
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    db_empty.add_paper(u.mine.bibcode)
    for t in tags:
        db_empty.add_new_tag(t)
    for t in tags[:3]:
        db_empty.tag_paper(u.mine.bibcode, t)

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # then add the final tag in the list
    to_add = tags[-1]
    cClick(widget.rightPanel.editTagsButton, qtbot)
    for tag_item in widget.rightPanel.getTagCheckboxes():
        if tag_item.text() == to_add:
            tag_item.setChecked(True)
    cClick(widget.rightPanel.doneEditingTagsButton, qtbot)

    expected_tags = tags[:3] + [tags[-1]]
    expected = "Tags: " + ", ".join(sorted(expected_tags, key=lambda x: x.lower()))
    assert widget.rightPanel.tagText.text() == expected


def test_tag_checkboxes_are_sorted_alphabetically_not_case_sensitive(qtbot, db_temp):
    # set up tags to check
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    for t in tags:
        db_temp.add_new_tag(t)

    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    tags = [tag.text() for tag in widget.rightPanel.getTagCheckboxes()]
    assert tags == sorted(tags, key=lambda x: x.lower())


def test_tag_checkboxes_are_sorted_properly_after_adding_new_tag(qtbot, db_temp):
    # set up tags to check
    tags = ["abc", "zyx", "Test", "ZAA"]
    for t in tags:
        db_temp.add_new_tag(t)

    widget = cInitialize(qtbot, db_temp)
    # click to show the checkboxes
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    # then add one in the left panel
    cAddTag(widget, "Aye", qtbot)
    # then ensure this new checkbox was added appropriately
    tags = [tag.text() for tag in widget.rightPanel.getTagCheckboxes()]
    assert "Aye" in tags
    assert tags == sorted(tags, key=lambda x: x.lower())


def test_tag_checkboxes_are_sorted_properly_after_deleting_tag(qtbot, db_temp):
    # set up tags to check
    tags = ["abc", "zyx", "Test", "ZAA"]
    for t in tags:
        db_temp.add_new_tag(t)

    widget = cInitialize(qtbot, db_temp)
    # click to show the checkboxes
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    # then delete a tag from the left panel
    cDeleteTag(widget, "Test", qtbot)
    # then ensure this new checkbox was removed appropriately
    tags = [tag.text() for tag in widget.rightPanel.getTagCheckboxes()]
    assert "Test" not in tags
    assert tags == sorted(tags, key=lambda x: x.lower())


def test_tag_text_is_updated_appropriately_when_tag_deleted(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.add_new_tag("test tag")
    db_empty.tag_paper(u.mine.bibcode, "test tag")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.tagText.text() == "Tags: test tag"
    cDeleteTag(widget, "test tag", qtbot)
    assert widget.rightPanel.tagText.text() == "Tags: None"


def test_unchecking_tag_in_checklist_removes_paper_from_center_panel(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.add_new_tag("test")
    db_empty.tag_paper(u.mine.bibcode, "test")

    widget = cInitialize(qtbot, db_empty)
    # click on the tag
    for tag in widget.tagsList.tags:
        if tag.name == "test":
            cClick(tag, qtbot)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.papersList.getPapers()[0].isHidden() is False
    for tag_item in widget.rightPanel.getTagCheckboxes():
        if tag_item.text() == "test":
            tag_item.setChecked(False)
    cClick(widget.rightPanel.doneEditingTagsButton, qtbot)
    # Then check that the paper is hidden, since it is not checked
    assert widget.papersList.getPapers()[0].isHidden() is True


def test_checking_tag_in_checklist_puts_paper_in_center_panel(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.add_new_tag("test")

    widget = cInitialize(qtbot, db_empty)
    # click on the paper, then click on a tag it does not have. The details will still
    # be in the right panel, but it will not be in the center panel
    cClick(widget.papersList.getPapers()[0], qtbot)
    for tag in widget.tagsList.tags:
        if tag.name == "test":
            cClick(tag, qtbot)

    assert widget.papersList.getPapers()[0].isHidden() is True
    for tag_item in widget.rightPanel.getTagCheckboxes():
        if tag_item.text() == "test":
            tag_item.setChecked(True)
    cClick(widget.rightPanel.doneEditingTagsButton, qtbot)
    # Then check that the paper is hidden, since it is not checked
    assert widget.papersList.getPapers()[0].isHidden() is False


# ===========================
# copying bibtex to clipboard
# ===========================
def test_clicking_bibtex_button_copies_bibtex(qtbot, db, monkeypatch):
    # Here we need to use monkeypatch to simulate the clipboard
    clipboard = QGuiApplication.clipboard()
    texts = []
    monkeypatch.setattr(clipboard, "setText", lambda x: texts.append(x))

    widget = cInitialize(qtbot, db)
    # get one of the papers in the right panel
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    # then click on the bibtext button
    cClick(widget.rightPanel.copyBibtexButton, qtbot)
    assert len(texts) == 1
    assert texts[0] in [u.mine.bibtex, u.tremonti.bibtex]


# =================
# open paper in ADS
# =================
def test_clicking_on_ads_button_opens_paper_in_browser(qtbot, db_empty, monkeypatch):
    # Here we need to use monkeypatch to simulate opening the URL
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = cInitialize(qtbot, db_empty)
    # add a paper to this empty database to make the paper object
    cAddPaper(widget, u.mine.bibcode, qtbot)
    # click on th epaper in the main panel, then click on the ADS button
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.adsButton, qtbot)

    # since this already has a URL it should be added
    assert open_calls == [
        f"https://ui.adsabs.harvard.edu/abs/2018ApJ...864...94B/abstract"
    ]


# ==========
# user notes
# ==========
def test_user_notes_has_correct_text(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.userNotesText.text() == "abc123"


def test_user_notes_has_correct_text_if_originally_blank(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.userNotesText.text() == "No notes yet"


def test_notes_static_text_disappears_when_edit_button_clicked(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    assert widget.rightPanel.userNotesText.isHidden() is True


def test_notes_edit_button_disappears_when_edit_button_clicked(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is True


def test_notes_finished_edit_button_appears_when_edit_button_clicked(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is False


def test_notes_edit_field_has_original_text(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    assert widget.rightPanel.userNotesTextEditField.toPlainText() == "abc123"


def test_notes_edit_field_has_focus_when_shown(qtbot, db_temp, monkeypatch):
    # I tried to test this directly, but was having trouble getting the tests to work
    # properly. Specifically, widget.hasFocus() was not working propertly in tests for
    # whatever reasonSo instead, I'll monkeypatch the setFocus method. I have tested
    # that this works in the actual interface
    setFocus_calls = []
    monkeypatch.setattr(QTextEdit, "setFocus", lambda x: setFocus_calls.append(True))

    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    # assert widget.tagsList.addTagBar.hasFocus() is True  # would be the best test
    assert setFocus_calls == [True]


def test_notes_edit_field_cursor_at_end_when_clicked(qtbot, db_notes):
    # we'll backspace one, then see what we have left to ensure we're at the end
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    cPressBackspace(widget.rightPanel.userNotesTextEditField, qtbot)
    assert widget.rightPanel.userNotesTextEditField.toPlainText() == "abc12"


def test_notes_edit_field_is_blank_if_there_are_no_notes(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    assert widget.rightPanel.userNotesTextEditField.toPlainText() == ""


def test_notes_edit_field_changes_database_when_finished(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    # simulate the user deleting the current into, then adding their own
    widget.rightPanel.userNotesTextEditField.clear()
    cEnterText(widget.rightPanel.userNotesTextEditField, "987XYZ", qtbot)
    cClick(widget.rightPanel.userNotesTextEditFinishedButton, qtbot)
    assert db_notes.get_paper_attribute(u.mine.bibcode, "user_notes") == "987XYZ"


def test_notes_edit_field_changes_shown_text(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    # simulate the user deleting the current into, then adding their own
    widget.rightPanel.userNotesTextEditField.clear()
    cEnterText(widget.rightPanel.userNotesTextEditField, "987XYZ", qtbot)
    cClick(widget.rightPanel.userNotesTextEditFinishedButton, qtbot)
    assert widget.rightPanel.userNotesText.text() == "987XYZ"


def test_notes_user_enters_blank_doesnt_print_blank(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    # simulate the user deleting the current into, then adding their own
    widget.rightPanel.userNotesTextEditField.clear()
    cClick(widget.rightPanel.userNotesTextEditFinishedButton, qtbot)
    assert widget.rightPanel.userNotesText.text() == "No notes yet"


def test_notes_edit_finished_button_disappears_when_clicked(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    cEnterText(widget.rightPanel.userNotesTextEditField, "987XYZ", qtbot)
    cClick(widget.rightPanel.userNotesTextEditFinishedButton, qtbot)
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_notes_edit_field_disappears_when_editing_done(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    cEnterText(widget.rightPanel.userNotesTextEditField, "987XYZ", qtbot)
    cClick(widget.rightPanel.userNotesTextEditFinishedButton, qtbot)
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True


def test_notes_edit_button_reappears_when_editing_done(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    cEnterText(widget.rightPanel.userNotesTextEditField, "987XYZ", qtbot)
    cClick(widget.rightPanel.userNotesTextEditFinishedButton, qtbot)
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is False


def test_notes_edit_can_quit_with_escape_reset_buttons(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    cPressEscape(widget.rightPanel.userNotesTextEditField, qtbot)
    assert widget.rightPanel.userNotesText.isHidden() is False
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is False
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_notes_edit_cannot_quit_with_backspace_buttons(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    # get rid of original text
    for _ in range(6):
        cPressBackspace(widget.rightPanel.userNotesTextEditField, qtbot)
    assert widget.rightPanel.userNotesTextEditField.isHidden() is False
    # one more backspace
    cPressBackspace(widget.rightPanel.userNotesTextEditField, qtbot)
    assert widget.rightPanel.userNotesText.isHidden() is True
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is True
    assert widget.rightPanel.userNotesTextEditField.isHidden() is False
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is False


def test_notes_edit_can_quit_with_escape_no_saving(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    cEnterText(widget.rightPanel.userNotesTextEditField, "ABC123", qtbot)
    cPressEscape(widget.rightPanel.userNotesTextEditField, qtbot)
    bibcode = widget.papersList.getPapers()[0].bibcode
    assert db_temp.get_paper_attribute(bibcode, "user_notes") is None


def test_notes_edit_can_quit_with_escape_original_text_shown(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    cEnterText(widget.rightPanel.userNotesTextEditField, "ZYX987", qtbot)
    cPressEscape(widget.rightPanel.userNotesTextEditField, qtbot)
    # the original notes should still be there
    assert widget.rightPanel.userNotesText.text() == "abc123"


def test_notes_edit_quit_with_escape_shows_original_text_next_edit(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    cEnterText(widget.rightPanel.userNotesTextEditField, "ZYX987", qtbot)
    cPressEscape(widget.rightPanel.userNotesTextEditField, qtbot)
    # the original notes should still be there
    cClick(widget.rightPanel.userNotesTextEditButton, qtbot)
    assert widget.rightPanel.userNotesTextEditField.toPlainText() == "abc123"


# ================
# citation keyword
# ================
def test_citation_keyword_text_is_correct(qtbot, db):
    widget = cInitialize(qtbot, db)
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    true_cite_key = db.get_paper_attribute(paper.bibcode, "citation_keyword")
    assert widget.rightPanel.citeKeyText.text() == f"Citation Keyword: {true_cite_key}"


def test_edit_citation_keyword_button_hidden_when_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True


def test_citation_keyword_text_not_hidden_when_button_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert widget.rightPanel.citeKeyText.isHidden() is False


def test_edit_citation_keyword_entry_shown_when_button_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is False


def test_edit_citation_keyword_entry_has_current_cite_key(qtbot, db_empty):
    # first set up the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "citation_keyword", "test")
    # then show it in the interface
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert widget.rightPanel.editCiteKeyEntry.text() == "test"


def test_edit_citation_keyword_entry_is_blank_if_none_currently_set(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert widget.rightPanel.editCiteKeyEntry.text() == ""


def test_edit_citation_keyword_entry_has_focus_when_shown(qtbot, db_temp, monkeypatch):
    # I tried to test this directly, but was having trouble getting the tests to work
    # properly. Specifically, widget.hasFocus() was not working propertly in tests for
    # whatever reasonSo instead, I'll monkeypatch the setFocus method. I have tested
    # that this works in the actual interface
    setFocus_calls = []
    monkeypatch.setattr(QLineEdit, "setFocus", lambda x: setFocus_calls.append(True))

    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    # assert widget.tagsList.addTagBar.hasFocus() is True  # would be the best test
    assert setFocus_calls == [True]


def test_edit_citation_keyword_entry_cursor_at_end(qtbot, db_empty):
    # first set up the database, the show the interface
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "citation_keyword", "test")
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # we'll show the text, then click backspace, then check what's there to see if the
    # cursor was really at the end
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cPressBackspace(widget.rightPanel.editCiteKeyEntry, qtbot)
    assert widget.rightPanel.editCiteKeyEntry.text() == "tes"


def test_edit_citation_keyword_error_text_not_shown_when_button_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_good_entry_updates_database(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # don't use convenience function, for clarity
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "test_key", qtbot)
    cPressEnter(widget.rightPanel.editCiteKeyEntry, qtbot)
    new_key = db_temp.get_paper_attribute(
        widget.papersList.getPapers()[0].bibcode, "citation_keyword"
    )
    assert new_key == "test_key"


def test_edit_citation_keyword_good_entry_updates_shown_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    assert widget.rightPanel.citeKeyText.text() == "Citation Keyword: test_key"


def test_edit_citation_keyword_good_entry_resets_buttons(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_good_entry_clears_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    assert widget.rightPanel.editCiteKeyEntry.text() == ""


def test_edit_citation_keyword_empty_string_uses_bibcode(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # first edit the cite key to something, then change it back
    cEditCiteKey(widget, "should_not_stay", qtbot)
    cEditCiteKey(widget, "", qtbot)
    bibcode = widget.papersList.getPapers()[0].bibcode
    assert db_temp.get_paper_attribute(bibcode, "citation_keyword") == bibcode


def test_edit_citation_keyword_empty_string_updates_shown_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # first edit the cite key to something, then change it back
    cEditCiteKey(widget, "should_not_stay", qtbot)
    cEditCiteKey(widget, "", qtbot)
    bibcode = widget.papersList.getPapers()[0].bibcode
    assert widget.rightPanel.citeKeyText.text() == f"Citation Keyword: {bibcode}"


def test_edit_citation_keyword_empty_string_resets_buttons(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # first edit the cite key to something, then change it back
    cEditCiteKey(widget, "should_not_stay", qtbot)
    cEditCiteKey(widget, "", qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_empty_string_clears_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    # first edit the cite key to something, then change it back
    cEditCiteKey(widget, "should_not_stay", qtbot)
    cEditCiteKey(widget, "", qtbot)
    assert widget.rightPanel.editCiteKeyEntry.text() == ""


def test_edit_citation_keyword_spaces_not_allowed(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test key", qtbot)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.text() == "Spaces not allowed"


def test_edit_citation_keyword_duplicates_not_allowed(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is False
    assert (
        widget.rightPanel.editCiteKeyErrorText.text()
        == "Another paper already uses this"
    )


def test_edit_citation_keyword_spaces_doesnt_reset_buttons(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test key", qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is False
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is False


def test_edit_citation_keyword_duplicates_doesnt_reset_buttons(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is False
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is False


def test_edit_citation_keyword_spaces_doesnt_clear_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test key", qtbot)
    assert widget.rightPanel.editCiteKeyEntry.text() == "test key"


def test_edit_citation_keyword_duplicates_doesnt_clear_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    assert widget.rightPanel.editCiteKeyEntry.text() == "test_key"


def test_edit_citation_keyword_spaces_doesnt_update_database(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test key", qtbot)
    bibcode = widget.papersList.getPapers()[0].bibcode
    assert db_temp.get_paper_attribute(bibcode, "citation_keyword") == bibcode


def test_edit_citation_keyword_duplicates_doesnt_update_database(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    cEditCiteKey(widget, "test_key", qtbot)
    bibcode_update = widget.papersList.getPapers()[0].bibcode
    assert db_temp.get_paper_attribute(bibcode_update, "citation_keyword") == "test_key"
    bibcode_dup = widget.papersList.getPapers()[1].bibcode
    assert db_temp.get_paper_attribute(bibcode_dup, "citation_keyword") == bibcode_dup


def test_edit_citation_keyword_entry_escape_exit_resets_buttons(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "abc", qtbot)
    cPressEscape(widget.rightPanel.editCiteKeyEntry, qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_entry_backspace_exit_resets_buttons(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "abc", qtbot)
    # back out the text we entered
    for _ in range(3):
        cPressBackspace(widget.rightPanel.editCiteKeyEntry, qtbot)
    # buttons should not be reset yet
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is False
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True
    # buttons should reset after one more backspace
    cPressBackspace(widget.rightPanel.editCiteKeyEntry, qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_entry_escape_exit_clears_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "abc", qtbot)
    cPressEscape(widget.rightPanel.editCiteKeyEntry, qtbot)
    assert widget.rightPanel.editCiteKeyEntry.text() == ""


def test_edit_citation_keywored_entry_backspace_exit_clears_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "abc", qtbot)
    # back out the text we entered
    for _ in range(3):
        cPressBackspace(widget.rightPanel.editCiteKeyEntry, qtbot)
    # buttons should reset after one more backspace
    cPressBackspace(widget.rightPanel.editCiteKeyEntry, qtbot)

    assert widget.rightPanel.editCiteKeyEntry.text() == ""


def test_edit_citation_keywored_entry_escape_exit_doesnt_change_db(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "abc", qtbot)
    cPressEscape(widget.rightPanel.editCiteKeyEntry, qtbot)
    bibcode = widget.papersList.getPapers()[0].bibcode
    assert db_temp.get_paper_attribute(bibcode, "citation_keyword") == bibcode


def test_edit_citation_keywored_entry_backspace_exit_doesnt_change_db(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cEnterText(widget.rightPanel.editCiteKeyEntry, "abc", qtbot)
    # back out the text we entered
    for _ in range(3):
        cPressBackspace(widget.rightPanel.editCiteKeyEntry, qtbot)
    # buttons should reset after one more backspace
    cPressBackspace(widget.rightPanel.editCiteKeyEntry, qtbot)
    bibcode = widget.papersList.getPapers()[0].bibcode
    assert db_temp.get_paper_attribute(bibcode, "citation_keyword") == bibcode


def test_edit_citation_keyword_entry_disappears_when_new_paper_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editCiteKeyButton, qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True


# ===============
# deleting papers
# ===============
def test_second_delete_paper_button_appears_when_first_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is False


def test_second_delete_paper_cancel_button_appears_when_first_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is False


def test_scroll_to_show_all_second_delete_buttons_when_first_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    scrollbar = widget.rightPanel.verticalScrollBar()
    assert scrollbar.value() == scrollbar.maximum()


def test_first_delete_paper_button_disappears_when_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is True


def test_first_delete_buttons_reset_when_on_new_paper(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is False


def test_second_delete_buttons_reset_when_on_new_paper(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is True


def test_second_delete_cancel_buttons_reset_when_on_new_paper(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    cClick(widget.papersList.getPapers()[1], qtbot)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is True


def test_second_delete_paper_button_deletes_paper_from_database(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    paper = widget.papersList.getPapers()[0]
    cDeleteFirstPaper(widget, qtbot)
    # check that it's not in the database anymore
    with pytest.raises(ValueError):
        db_temp.get_paper_attribute(paper.bibcode, "title")


def test_second_delete_paper_button_deletes_paper_from_interface(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    bibcode = widget.papersList.getPapers()[0].bibcode
    cDeleteFirstPaper(widget, qtbot)
    # check that it's not in the center list anymore
    for paper in widget.papersList.getPapers():
        assert bibcode != paper.bibcode


def test_second_delete_paper_cancel_doesnt_delete_paper_db(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    paper = widget.papersList.getPapers()[0]
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    cClick(widget.rightPanel.secondDeletePaperCancelButton, qtbot)
    # check that it's still in the database
    assert db_temp.get_paper_attribute(paper.bibcode, "title") == paper.titleText.text()


def test_second_delete_paper_cancel_doesnt_delete_paper_interface(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    bibcode = widget.papersList.getPapers()[0].bibcode
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    cClick(widget.rightPanel.secondDeletePaperCancelButton, qtbot)
    # check that it's still in the center list
    found = False
    for paper in widget.papersList.getPapers():
        if bibcode == paper.bibcode:
            found = True
    assert found


def test_second_delete_paper_cancel_resets_delete_buttons(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.firstDeletePaperButton, qtbot)
    cClick(widget.rightPanel.secondDeletePaperCancelButton, qtbot)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is False
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is True
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is True


def test_right_panel_edit_tags_button_is_hidden_when_paper_is_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.editTagsButton.isHidden()


def test_right_panel_done_editing_tags_button_hidden_when_paper_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.doneEditingTagsButton.isHidden()


def test_right_panel_copy_bibtex_button_is_hidden_when_paper_is_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.copyBibtexButton.isHidden()


def test_right_panel_open_ads_button_is_hidden_when_paper_is_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.adsButton.isHidden()


def test_right_panel_first_delete_button_is_hidden_when_paper_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.firstDeletePaperButton.isHidden()


def test_right_panel_second_delete_button_is_hidden_when_paper_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.secondDeletePaperButton.isHidden()


def test_right_panel_second_delete_cancel_button_hide_on_paper_delete(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden()


def test_right_panel_title_text_is_blank_when_paper_is_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.titleText.text() == ""


def test_right_panel_cite_text_is_blank_when_paper_is_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.citeText.text() == ""


def test_right_panel_tag_text_is_blank_when_paper_is_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.tagText.text() == ""


def test_right_panel_abstract_text_is_default_when_paper_is_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert (
        widget.rightPanel.abstractText.text()
        == "Click on a paper to show its details here"
    )


def test_user_notes_are_appropriately_shown_once_paper_deleted(qtbot, db_notes):
    widget = cInitialize(qtbot, db_notes)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.userNotesText.isHidden() is True
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is True
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_spacers_are_hidden_once_paper_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    for spacer in widget.rightPanel.spacers:
        assert spacer.isHidden() is True


def test_edit_citation_keyword_buttons_hidden_when_paper_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteFirstPaper(widget, qtbot)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is True
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


# ======================================================================================
#
# test center panel papers list
#
# ======================================================================================
# =============
# initial state
# =============
def test_paper_title_has_correct_font_family(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    assert paper.titleText.font().family() == "Cabin"


def test_paper_cite_text_has_correct_font_family(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    assert paper.citeText.font().family() == "Cabin"


def test_paper_title_has_correct_font_size(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    assert paper.titleText.font().pointSize() == 18


def test_paper_cite_string_has_correct_font_size(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    assert paper.citeText.font().pointSize() == 12


def test_paper_title_has_word_wrap_on(qtbot, db):
    widget = cInitialize(qtbot, db)
    for paper in widget.papersList.getPapers():
        assert paper.titleText.wordWrap()


def test_paper_cite_string_has_word_wrap_on(qtbot, db):
    widget = cInitialize(qtbot, db)
    for paper in widget.papersList.getPapers():
        assert paper.citeText.wordWrap()


# ===============
# creating papers
# ===============
def test_paper_initialization_has_correct_bibcode(qtbot, db):
    widget = cInitialize(qtbot, db)
    new_paper = Paper(u.mine.bibcode, widget)
    assert new_paper.bibcode == u.mine.bibcode


def test_paper_initialization_has_correct_title_in_the_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    new_paper = Paper(u.mine.bibcode, widget)
    assert new_paper.titleText.text() == u.mine.title


def test_paper_initialization_has_correct_cite_string_in_the_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    new_paper = Paper(u.mine.bibcode, widget)
    assert new_paper.citeText.text() == db.get_cite_string(u.mine.bibcode)


def test_paper_initialization_has_accents_in_author_list(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    db_empty.add_paper(u.juan.bibcode)
    new_paper = Paper(u.juan.bibcode, widget)
    assert "á" in new_paper.citeText.text()


def test_all_papers_in_database_are_in_the_paper_list_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    papers_list_bibcodes = [p.bibcode for p in widget.papersList.getPapers()]
    assert sorted(papers_list_bibcodes) == sorted(db.get_all_bibcodes())


def test_get_tags_from_paper_object_is_correct(qtbot, db):
    widget = cInitialize(qtbot, db)
    paper = widget.papersList.getPapers()[0]
    assert paper.getTags() == db.get_paper_tags(paper.bibcode)


# ============
# highlighting
# ============
def test_clicking_on_paper_highlights_it_in_center_panel(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    assert paper.property("is_highlighted") is True


def test_clicking_on_paper_highlights_its_text_it_in_center_panel(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the papers, not sure which
    paper = widget.papersList.getPapers()[0]
    cClick(paper, qtbot)
    assert paper.titleText.property("is_highlighted") is True
    assert paper.citeText.property("is_highlighted") is True


def test_all_papers_are_unhilighted_to_start(qtbot, db):
    widget = cInitialize(qtbot, db)
    for paper in widget.papersList.getPapers():
        assert paper.property("is_highlighted") is False


def test_all_papers_text_are_unhilighted_to_start(qtbot, db):
    widget = cInitialize(qtbot, db)
    for paper in widget.papersList.getPapers():
        assert paper.titleText.property("is_highlighted") is False
        assert paper.citeText.property("is_highlighted") is False


def test_papers_are_unhighlighted_when_others_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert len(widget.papersList.getPapers()) > 1
    for paper_click in widget.papersList.getPapers():
        cClick(paper_click, qtbot)
        for paper_test in widget.papersList.getPapers():
            if paper_test.titleText == paper_click.titleText:
                assert paper_test.property("is_highlighted") is True
            else:
                assert paper_test.property("is_highlighted") is False


def test_paper_texts_are_unhighlighted_when_others_clicked(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert len(widget.papersList.getPapers()) > 1
    for paper_click in widget.papersList.getPapers():
        cClick(paper_click, qtbot)
        for paper_test in widget.papersList.getPapers():
            if paper_test.titleText == paper_click.titleText:
                assert paper_test.titleText.property("is_highlighted") is True
                assert paper_test.citeText.property("is_highlighted") is True
            else:
                assert paper_test.titleText.property("is_highlighted") is False
                assert paper_test.citeText.property("is_highlighted") is False


# ================================================================
# opening paper pdfs when double clicked, or modifying right panel
# ================================================================
def test_dclicking_on_paper_with_local_file_opens_it(qtbot, db_empty, monkeypatch):
    test_loc = __file__
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = cInitialize(qtbot, db_empty)
    # add a paper to this empty database to make the paper object
    cAddPaper(widget, u.mine.bibcode, qtbot)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", test_loc)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    # since this already has a URL it should be added
    assert open_calls == [f"file:{test_loc}"]


def test_dclicking_on_paper_with_no_local_file_doesnt_ask(qtbot, db_temp, monkeypatch):
    user_asks = []
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda filter, dir, caption: user_asks.append("save"),
    )
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda filter, dir: user_asks.append("open"),
    )

    widget = cInitialize(qtbot, db_temp)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    assert user_asks == []


def test_dclicking_on_paper_with_no_local_file_doesnt_open(qtbot, db_temp, monkeypatch):
    # Here we need to use monkeypatch to simulate opening the file
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = cInitialize(qtbot, db_temp)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    assert open_calls == []


def test_dclicking_on_paper_with_no_local_file_highlights_right_panel(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True


def test_dclicking_on_paper_with_no_local_file_scrolls_to_show_buttons(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    # I don't know exactly where this should end up, but not at the top or bottom
    assert (
        0
        < widget.rightPanel.verticalScrollBar().value()
        < widget.rightPanel.verticalScrollBar().maximum()
    )
    assert widget.rightPanel.horizontalScrollBar().value() == 0


def test_pdf_highlighting_goes_away_with_any_click(qtbot, db_temp):
    # any text that can be selected by the user will not remove the highlighting, but
    # all other things should
    widget = cInitialize(qtbot, db_temp)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True
    cClick(widget.rightPanel.spacers[0], qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == False
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == False


def test_pdf_highlighting_hide_with_choose_local_click(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getOpenFileName", mOpenFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True
    cClick(widget.rightPanel.pdfChooseLocalFileButton, qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == False
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == False


def test_pdf_highlighting_hide_with_download_click(qtbot, db_temp, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileNoResponse)
    widget = cInitialize(qtbot, db_temp)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True
    cClick(widget.rightPanel.pdfDownloadButton, qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == False
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == False


def test_pdf_highlighting_goes_away_when_new_paper_clicked(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True
    cClick(widget.papersList.getPapers()[1], qtbot)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == False
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == False


def test_dclicking_paper_nonexistent_file_pdf_highlight(qtbot, db_empty, monkeypatch):
    # first, add a file to the database, then set the file to something nonsense. We'll
    # then try to open it, and check that the interface asks the user.
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "lskdlskdflskj")

    # when we try to open files, just list the ones we tried to open
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = cInitialize(qtbot, db_empty)
    # add a paper to this empty database to make the paper object
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    # check that we didn't open anything
    assert open_calls == []
    # check that the right panel is highlighted
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True


def test_dclicking_on_paper_shows_details_in_right_panel(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    # add a paper to this empty database to make the paper object
    cAddPaper(widget, u.mine.bibcode, qtbot)  # do not add file location
    cDoubleClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.titleText.text() == u.mine.title


# ==============
# sorting papers
# ==============
def test_papers_are_in_sorted_order_to_begin(qtbot, db):
    widget = cInitialize(qtbot, db)
    dates = [
        db.get_paper_attribute(paper.bibcode, "pubdate")
        for paper in widget.papersList.getPapers()
    ]

    assert dates == sorted(dates)


def test_papers_are_in_sorted_order_after_adding(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # add two papers: one very old, one very recent
    for bibcode in [u.mine_recent.bibcode, u.bbfh.bibcode]:
        cAddPaper(widget, bibcode, qtbot)
    # then check sorting
    dates = [
        db_temp.get_paper_attribute(paper.bibcode, "pubdate")
        for paper in widget.papersList.getPapers()
    ]
    assert dates == sorted(dates)


def test_paper_sort_is_initially_by_date(qtbot, db):
    widget = cInitialize(qtbot, db)
    bibcodes = [paper.bibcode for paper in widget.papersList.getPapers()]
    assert bibcodes == [u.tremonti.bibcode, u.mine.bibcode]


def test_paper_sort_dropdown_can_sort_by_author(qtbot, db):
    widget = cInitialize(qtbot, db)
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by First Author")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.getPapers()]
    assert bibcodes == [u.mine.bibcode, u.tremonti.bibcode]


def test_paper_sort_dropdown_can_sort_by_author_same_last_name(qtbot, db_temp):
    # add another paper by Warren Brown, should be sorted after me (Gillen Brown)
    db_temp.add_paper("2015ApJ...804...49B")
    widget = cInitialize(qtbot, db_temp)
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by First Author")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.getPapers()]
    assert bibcodes == [u.mine.bibcode, "2015ApJ...804...49B", u.tremonti.bibcode]


def test_paper_sort_dropdown_can_sort_in_both_directions(qtbot, db):
    widget = cInitialize(qtbot, db)
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by First Author")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.getPapers()]
    assert bibcodes == [u.mine.bibcode, u.tremonti.bibcode]
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by Date")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.getPapers()]
    assert bibcodes == [u.tremonti.bibcode, u.mine.bibcode]


def test_paper_sort_dropdown_can_sort_by_author_single_author(qtbot, db_empty):
    bibcodes_to_add = [
        u.mine.bibcode,
        u.mine_recent.bibcode,
        "2021MNRAS.508.5935B",
        "2021NewA...8401501B",
    ]
    # put some papers by me in the database
    for b in bibcodes_to_add:
        db_empty.add_paper(b)
    widget = cInitialize(qtbot, db_empty)
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by First Author")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.getPapers()]
    # since these are all one author, they should be in date order
    assert bibcodes == [
        u.mine.bibcode,
        "2021NewA...8401501B",
        "2021MNRAS.508.5935B",
        u.mine_recent.bibcode,
    ]


# ======================================================================================
#
# test the left panel tags list
#
# ======================================================================================
# =============
# initial state
# =============
def test_add_tag_button_is_shown_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.addTagButton.isHidden() is False


def test_add_tag_text_button_has_correct_font_size(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.addTagButton.font().pointSize() == 14


def test_add_tag_text_button_has_correct_font_family(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.addTagButton.font().family() == "Cabin"


def test_add_tag_text_bar_is_hidden_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.addTagBar.isHidden() is True


def test_add_tag_error_text_is_hidden_at_beginning(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.addTagErrorText.isHidden() is True


def test_add_tag_text_bar_has_correct_font_family(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.addTagButton, qtbot)
    assert widget.tagsList.addTagBar.font().family() == "Cabin"


def test_add_tag_text_bar_has_correct_placeholder_text(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.addTagButton, qtbot)
    assert widget.tagsList.addTagBar.placeholderText() == "Tag name"


def test_add_tag_text_bar_has_correct_font_size(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.addTagButton, qtbot)
    assert widget.tagsList.addTagBar.font().pointSize() == 14


def test_tag_has_correct_font_family(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the tags, not sure which
    tag = widget.tagsList.tags[0]
    assert tag.font().family() == "Cabin"


def test_tag_has_correct_font_size(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the tags, not sure which
    tag = widget.tagsList.tags[0]
    assert tag.font().family() == "Cabin"


def test_all_tags_in_database_are_in_the_tag_list_at_beginning(qtbot, db):
    widget = cInitialize(qtbot, db)
    tags_list = [t.name for t in widget.tagsList.tags]
    assert sorted(tags_list) == sorted(db.get_all_tags())


def test_unread_is_initialized_in_new_database(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    tags_list = [t.name for t in widget.tagsList.tags]
    assert sorted(tags_list) == ["Unread"]


def test_unread_isnt_added_to_nonempty_database(qtbot, db_no_tags):
    db_no_tags.add_new_tag("lskdjlkj")
    db_no_tags.add_new_tag("ghjghjg")
    widget = cInitialize(qtbot, db_no_tags)
    tags_list = [t.name for t in widget.tagsList.tags]
    assert "Unread" not in tags_list


def test_tag_has_correct_name(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get one of the tags, not sure which
    tag = widget.tagsList.tags[0]
    assert tag.label.text() == tag.name


def test_show_all_button_fontsize(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.tagsList.showAllButton.font().pointSize() == 14


def test_show_all_button_has_correct_font_family(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.showAllButton.font().family() == "Cabin"


def test_show_all_button_has_correct_text(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.showAllButton.label.text() == "All Papers"


def test_rename_tag_button_shown_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.renameTagButton.isHidden() is False


def test_rename_tag_button_has_correct_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.renameTagButton.text() == "Rename a tag"


def test_rename_tag_old_entry_hidden_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.renameTagOldEntry.isHidden() is True


def test_rename_tag_new_entry_hidden_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.renameTagNewEntry.isHidden() is True


def test_rename_tag_error_text_hidden_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.renameTagErrorText.isHidden() is True


def test_rename_tag_old_entry_has_placeholder_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.renameTagOldEntry.placeholderText() == "Tag to rename"


def test_rename_tag_new_entry_has_placeholder_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.renameTagNewEntry.placeholderText() == "New tag name"


def test_first_delete_tag_button_shown_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.firstDeleteTagButton.isHidden() is False


def test_first_delete_tag_button_has_correct_font_size(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.firstDeleteTagButton.font().pointSize() == 14


def test_first_delete_tag_button_has_correct_font_family(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    assert widget.tagsList.firstDeleteTagButton.font().family() == "Cabin"


def test_first_delete_tag_button_has_correct_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.firstDeleteTagButton.text() == "Delete a tag"


def test_second_delete_tag_entry_hidden_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is True


def test_second_delete_tag_error_text_hidden_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.secondDeleteTagErrorText.isHidden() is True


def test_second_delete_tag_button_has_correct_font_size(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.font().pointSize() == 14


def test_second_delete_tag_button_has_correct_font_family(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.font().family() == "Cabin"


def test_second_delete_tag_entry_has_placeholder_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    text = "Tag to delete"
    assert widget.tagsList.secondDeleteTagEntry.placeholderText() == text


def test_third_delete_tag_entry_hidden_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.thirdDeleteTagButton.isHidden() is True


def test_third_cancel_tag_entry_hidden_at_beginning(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.thirdDeleteTagCancelButton.isHidden() is True


def test_third_delete_tag_button_has_correct_font_size(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.thirdDeleteTagButton.font().pointSize() == 14


def test_third_delete_tag_button_has_correct_font_family(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.thirdDeleteTagButton.font().family() == "Cabin"


def test_third_delete_tag_cancel_button_has_correct_font_size(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.thirdDeleteTagCancelButton.font().pointSize() == 14


def test_third_delete_tag_cancel_button_has_correct_font_family(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.thirdDeleteTagCancelButton.font().family() == "Cabin"


def test_show_all_export_button_has_correct_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    assert widget.tagsList.showAllButton.exportButton.text() == "Export"


def test_tag_export_button_has_correct_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.tags[0].exportButton.text() == "Export"


def test_show_all_tags_button_starts_with_export_button(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.showAllButton.exportButton.isHidden() is False


def test_all_tags_start_with_export_hidden(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # get a tag from the left panel to click on
    for tag in widget.tagsList.tags:
        assert tag.exportButton.isHidden() is True


def test_left_panel_tags_are_sorted_alphabetically(qtbot, db_empty):
    # add tags to database before we initialize interface
    # add tags
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    for t in tags:
        db_empty.add_new_tag(t)

    widget = cInitialize(qtbot, db_empty)
    tag_names = [tag.name for tag in widget.tagsList.tags]
    assert tag_names == sorted(tags, key=lambda t: t.lower())


# ===========
# adding tags
# ===========
def test_clicking_add_tag_button_hides_button(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.addTagButton, qtbot)
    assert widget.tagsList.addTagButton.isHidden() is True


def test_clicking_add_tag_button_shows_text_entry(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.addTagButton, qtbot)
    assert widget.tagsList.addTagBar.isHidden() is False


def test_add_tag_button_and_entry_have_same_height(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    button_height = widget.tagsList.addTagButton.height()
    cClick(widget.tagsList.addTagButton, qtbot)
    assert widget.tagsList.addTagBar.height() == button_height


def test_clicking_add_tag_button_puts_focus_on_text_entry(qtbot, db_empty, monkeypatch):
    # I tried to test this directly, but was having trouble getting the tests to work
    # properly. Specifically, widget.hasFocus() was not working propertly in tests for
    # whatever reasonSo instead, I'll monkeypatch the setFocus method. I have tested
    # that this works in the actual interface
    setFocus_calls = []
    monkeypatch.setattr(QLineEdit, "setFocus", lambda x: setFocus_calls.append(True))

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.tagsList.addTagButton, qtbot)
    # assert widget.tagsList.addTagBar.hasFocus() is True  # would be the best test
    assert setFocus_calls == [True]


def test_can_add_tag_by_filling_tag_name_then_pressing_enter(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # Don't use convenience function, for clarity on what I'm doing
    cClick(widget.tagsList.addTagButton, qtbot)
    cEnterText(widget.tagsList.addTagBar, "Test Tag", qtbot)
    cPressEnter(widget.tagsList.addTagBar, qtbot)
    assert db_temp.paper_has_tag(u.mine.bibcode, "Test Tag") is False


def test_can_add_tag_to_list_by_filling_tag_name_then_pressing_enter(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # Don't use convenience function, for clarity on what I'm doing
    cClick(widget.tagsList.addTagButton, qtbot)
    cEnterText(widget.tagsList.addTagBar, "Test Tag", qtbot)
    cPressEnter(widget.tagsList.addTagBar, qtbot)
    tag_names = [t.name for t in widget.tagsList.tags]
    assert "Test Tag" in tag_names


def test_tag_name_entry_is_cleared_after_successful_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "Test Tag", qtbot)
    assert widget.tagsList.addTagBar.text() == ""


def test_tag_name_entry_is_hidden_after_successful_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "Test Tag", qtbot)
    assert widget.tagsList.addTagBar.isHidden() is True


def test_tag_name_button_is_shown_after_successful_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "Test Tag", qtbot)
    assert widget.tagsList.addTagButton.isHidden() is False


def test_duplicate_in_internal_tags_list_raises_error(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "Test Tag", qtbot)
    with pytest.raises(AssertionError):
        widget.tagsList.addTagInternal("Test Tag")


def test_tag_name_entry_is_not_cleared_after_duplicate_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "Test Tag", qtbot)
    cAddTag(widget, "Test Tag", qtbot)
    assert widget.tagsList.addTagBar.text() == "Test Tag"


def test_add_tag_error_message_shown_after_duplicate_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "Test Tag", qtbot)
    cAddTag(widget, "Test Tag", qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is False
    assert widget.tagsList.addTagErrorText.text() == "This tag already exists"


def test_tag_name_entry_is_not_cleared_after_duplicate_cap_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "Test Tag", qtbot)
    cAddTag(widget, "test tag", qtbot)
    assert widget.tagsList.addTagBar.text() == "test tag"


def test_tag_name_entry_is_not_cleared_after_whitespace_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "   ", qtbot)
    assert widget.tagsList.addTagBar.text() == "   "


def test_add_tag_error_message_shown_after_whitesapce_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "   ", qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is False
    assert widget.tagsList.addTagErrorText.text() == "Pure whitespace isn't valid"


def test_tag_name_entry_is_not_cleared_after_all_papers_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "All Papers", qtbot)
    assert widget.tagsList.addTagBar.text() == "All Papers"


def test_add_tag_error_message_shown_after_all_papers_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "All Papers", qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is False
    assert widget.tagsList.addTagErrorText.text() == "Sorry, can't duplicate this"


def test_add_tag_error_message_shown_after_all_papers_lower_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "all papers", qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is False
    assert widget.tagsList.addTagErrorText.text() == "Sorry, can't duplicate this"


def test_tag_name_entry_is_not_cleared_after_backtick_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "`", qtbot)
    assert widget.tagsList.addTagBar.text() == "`"


def test_tag_name_entry_is_not_cleared_after_square_bracket_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "[]", qtbot)
    assert widget.tagsList.addTagBar.text() == "[]"


def test_add_tag_error_message_shown_after_backtick_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "`", qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is False
    assert widget.tagsList.addTagErrorText.text() == "Backticks aren't allowed"


def test_add_tag_error_message_shown_after_square_bracket_tag_attempt(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "[]", qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is False
    assert widget.tagsList.addTagErrorText.text() == "Square brackets aren't allowed"


def test_add_tag_error_message_hidden_after_text_changed(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "   ", qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is False
    cPressBackspace(widget.tagsList.addTagBar, qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is True


def test_add_tag_error_message_hidden_after_cursor_moved(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "   ", qtbot)
    assert widget.tagsList.addTagErrorText.isHidden() is False
    widget.tagsList.addTagBar.setCursorPosition(0)
    assert widget.tagsList.addTagErrorText.isHidden() is True


def test_add_tag_entry_can_exit_with_escape_press_at_any_time(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.addTagButton, qtbot)
    cEnterText(widget.tagsList.addTagBar, "sdfsdf", qtbot)
    cPressEscape(widget.tagsList.addTagBar, qtbot)
    assert widget.tagsList.addTagBar.isHidden() is True
    assert widget.tagsList.addTagButton.isHidden() is False
    assert widget.tagsList.addTagErrorText.isHidden() is True


def test_add_tag_entry_can_exit_with_escape_press_at_any_time_clears_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.addTagButton, qtbot)
    cEnterText(widget.tagsList.addTagBar, "sdfsdf", qtbot)
    cPressEscape(widget.tagsList.addTagBar, qtbot)
    assert widget.tagsList.addTagBar.text() == ""


def test_add_tag_entry_can_exit_with_backspace_when_empty(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.addTagButton, qtbot)
    cEnterText(widget.tagsList.addTagBar, "abc", qtbot)
    # back out those three letters
    for _ in range(3):
        cPressBackspace(widget.tagsList.addTagBar, qtbot)
    # entry should still be visible
    assert widget.tagsList.addTagBar.isHidden() is False
    assert widget.tagsList.addTagButton.isHidden() is True
    # with one more backspace, we exit
    cPressBackspace(widget.tagsList.addTagBar, qtbot)
    assert widget.tagsList.addTagBar.isHidden() is True
    assert widget.tagsList.addTagButton.isHidden() is False
    assert widget.tagsList.addTagErrorText.isHidden() is True


def test_newly_added_tags_appear_in_right_panel(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "Test Tag", qtbot)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert "Test Tag" in [t.text() for t in widget.rightPanel.getTagCheckboxes()]


def test_adding_tags_doesnt_duplicate_tags_in_right_panel(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    widget = cInitialize(qtbot, db_empty)
    cAddTag(widget, "Test Tag", qtbot)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert ["Test Tag"] == [t.text() for t in widget.rightPanel.getTagCheckboxes()]
    # add another tag, then check again
    cAddTag(widget, "Test Tag 2", qtbot)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert ["Test Tag", "Test Tag 2"] == [
        t.text() for t in widget.rightPanel.getTagCheckboxes()
    ]


# ======================================
# clicking tags shows only tagged papers
# ======================================
def test_all_papers_start_not_hidden(qtbot, db):
    widget = cInitialize(qtbot, db)
    for paper in widget.papersList.getPapers():
        assert not paper.isHidden()


def test_clicking_on_tag_in_left_panel_hides_papers(qtbot, db):
    widget = cInitialize(qtbot, db)
    # get a tag from the left panel to click on
    left_tag = widget.tagsList.tags[0]
    cClick(left_tag, qtbot)
    # then check the tags that are in shown papers
    for paper in widget.papersList.getPapers():
        if left_tag.label.text() in db.get_paper_tags(paper.bibcode):
            assert paper.isHidden() is False
        else:
            assert paper.isHidden() is True


def test_clicking_on_show_all_button_shows_all_papers(qtbot, db):
    widget = cInitialize(qtbot, db)
    # First click on a tag to restrict the number of papers shown
    left_tag = widget.tagsList.tags[0]
    cClick(left_tag, qtbot)
    # then click on the button to show all
    cClick(widget.tagsList.showAllButton, qtbot)
    # then check that all are shown
    for paper in widget.papersList.getPapers():
        assert paper.isHidden() is False


def test_show_all_tags_button_starts_highlighted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    assert widget.tagsList.showAllButton.property("is_highlighted") is True
    assert widget.tagsList.showAllButton.label.property("is_highlighted") is True


def test_all_tags_start_unhighlighted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # get a tag from the left panel to click on
    for tag in widget.tagsList.tags:
        assert tag.property("is_highlighted") is False
        assert tag.label.property("is_highlighted") is False


def test_clicking_on_tag_in_left_panel_highlights_tag_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # get a tag from the left panel to click on
    tag = widget.tagsList.tags[0]
    cClick(tag, qtbot)
    assert tag.property("is_highlighted") is True
    assert tag.label.property("is_highlighted") is True


def test_clicking_on_show_all_in_left_panel_highlights_tag_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.showAllButton, qtbot)
    assert widget.tagsList.showAllButton.property("is_highlighted") is True
    assert widget.tagsList.showAllButton.label.property("is_highlighted") is True


def test_clicking_on_tag_in_left_panel_unlights_others(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # Click on one tag, then another
    for tag in widget.tagsList.tags:
        cClick(tag, qtbot)
        for tag_comp in widget.tagsList.tags:
            if tag.label.text() == tag_comp.label.text():
                assert tag_comp.property("is_highlighted") is True
                assert tag_comp.label.property("is_highlighted") is True
            else:
                assert tag_comp.property("is_highlighted") is False
                assert tag_comp.label.property("is_highlighted") is False


def test_clicking_on_show_all_in_left_panel_unlights_others(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.showAllButton, qtbot)
    for tag in widget.tagsList.tags:
        assert tag.property("is_highlighted") is False
        assert tag.label.property("is_highlighted") is False


def test_newly_added_tag_is_unhighlighted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "newly added tag", qtbot)
    for tag in widget.tagsList.tags:
        if tag.label.text() == "newly added tag":
            assert tag.property("is_highlighted") is False
            assert tag.label.property("is_highlighted") is False


def test_left_panel_tags_are_sorted_alphabetically_after_adding(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    # add tags
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    for tag in tags:
        cAddTag(widget, tag, qtbot)
    tag_names = [tag.name for tag in widget.tagsList.tags]
    # in comparison, include unread, since it was included on widget
    # initialization too
    assert tag_names == sorted(tags + ["Unread"], key=lambda w: w.lower())


# =============
# renaming tags
# =============
def test_clicking_first_rename_tag_button_shows_old_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    assert widget.tagsList.renameTagOldEntry.isHidden() is False


def test_clicking_rename_tag_button_focus_on_entry(qtbot, db_temp, monkeypatch):
    # I tried to test this directly, but was having trouble getting the tests to work
    # properly. Specifically, widget.hasFocus() was not working propertly in tests for
    # whatever reasonSo instead, I'll monkeypatch the setFocus method. I have tested
    # that this works in the actual interface
    setFocus_calls = []
    monkeypatch.setattr(QLineEdit, "setFocus", lambda x: setFocus_calls.append(True))

    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    # assert widget.renameTagOldEntry.hasFocus() is True  # would be the best test
    assert setFocus_calls == [True]


def test_clicking_rename_tag_button_hides_button(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    assert widget.tagsList.renameTagButton.isHidden() is True


def test_rename_tag_button_and_old_entry_have_same_height(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    button_height = widget.tagsList.renameTagButton.height()
    cClick(widget.tagsList.renameTagButton, qtbot)
    assert widget.tagsList.renameTagOldEntry.height() == button_height


def test_rename_tag_old_entry_is_hidden_when_entry_done(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)  # tag must exist
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagOldEntry.isHidden() is True


def test_rename_tag_new_entry_appears_when_old_entry_done(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagNewEntry.isHidden() is False


def test_clicking_rename_tag_button_focus_on_new_entry(qtbot, db_temp, monkeypatch):
    # I tried to test this directly, but was having trouble getting the tests to work
    # properly. Specifically, widget.hasFocus() was not working propertly in tests for
    # whatever reasonSo instead, I'll monkeypatch the setFocus method. I have tested
    # that this works in the actual interface
    setFocus_calls = []
    monkeypatch.setattr(QLineEdit, "setFocus", lambda x: setFocus_calls.append(True))

    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    # assert widget.renameTagNewEntry.hasFocus() is True  # would be the best test
    assert setFocus_calls == [True, True]


def test_rename_tag_old_and_new_entry_have_same_height(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    button_height = widget.tagsList.renameTagButton.height()
    cClick(widget.tagsList.renameTagButton, qtbot)
    entry_old_height = widget.tagsList.renameTagOldEntry.height()
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    entry_new_height = widget.tagsList.renameTagNewEntry.height()
    assert button_height == entry_old_height  # already checked, included for clarity
    assert entry_old_height == entry_new_height


def test_rename_tag_error_text_hidden_when_old_entry_done(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is True


def test_rename_tag_old_entry_can_exit_with_escape_press_at_any_time(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdf", qtbot)
    cPressEscape(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagButton.isHidden() is False
    assert widget.tagsList.renameTagOldEntry.isHidden() is True
    assert widget.tagsList.renameTagNewEntry.isHidden() is True


def test_rename_tag_new_entry_can_exit_with_escape_press_at_any_time(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "Read", qtbot)
    cPressEscape(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagButton.isHidden() is False
    assert widget.tagsList.renameTagOldEntry.isHidden() is True
    assert widget.tagsList.renameTagNewEntry.isHidden() is True


def test_rename_tag_old_entry_exit_with_escape_press_at_any_time_clears_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdf", qtbot)
    cPressEscape(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagOldEntry.text() == ""


def test_rename_tag_new_entry_exit_with_escape_press_at_any_time_clears_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "Read", qtbot)
    cPressEscape(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagNewEntry.text() == ""


def test_rename_tag_old_entry_can_exit_with_backspace_when_empty(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "abc", qtbot)
    # back out those three letters
    for _ in range(3):
        cPressBackspace(widget.tagsList.renameTagOldEntry, qtbot)
    # entry should still be visible
    assert widget.tagsList.renameTagButton.isHidden() is True
    assert widget.tagsList.renameTagOldEntry.isHidden() is False
    assert widget.tagsList.renameTagNewEntry.isHidden() is True
    # with one more backspace, we exit
    cPressBackspace(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagButton.isHidden() is False
    assert widget.tagsList.renameTagOldEntry.isHidden() is True
    assert widget.tagsList.renameTagNewEntry.isHidden() is True


def test_rename_tag_new_entry_can_exit_with_backspace_when_empty(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "abc", qtbot)
    # back out those three letters
    for _ in range(3):
        cPressBackspace(widget.tagsList.renameTagNewEntry, qtbot)
    # entry should still be visible
    assert widget.tagsList.renameTagButton.isHidden() is True
    assert widget.tagsList.renameTagNewEntry.isHidden() is False
    assert widget.tagsList.renameTagOldEntry.isHidden() is True
    # with one more backspace, we exit
    cPressBackspace(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagButton.isHidden() is False
    assert widget.tagsList.renameTagNewEntry.isHidden() is True
    assert widget.tagsList.renameTagOldEntry.isHidden() is True


def test_rename_tag_does_that_in_database(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    original_tags = db_temp.get_all_tags()
    # don't use convenience function, for clarity
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "New", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    # check that it's not in the database anymore
    new_tags = db_temp.get_all_tags()
    assert "Read" not in new_tags
    assert "New" in new_tags
    assert len(new_tags) == len(original_tags)


def test_rename_tag_different_caps_does_that_in_database(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    original_tags = db_temp.get_all_tags()
    # don't use convenience function, for clarity
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "READ", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    # check that it's not in the database anymore
    new_tags = db_temp.get_all_tags()
    assert "Read" not in new_tags
    assert "READ" in new_tags
    assert len(new_tags) == len(original_tags)


def test_rename_tag_does_that_in_interface(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # first get the original number of tags
    num_original_tags = len([t.name for t in widget.tagsList.tags])
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "New", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    # Then see what tags are in the list now
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(new_tags) == num_original_tags
    assert not "Read" in new_tags
    assert "New" in new_tags


def test_rename_tag_does_that_in_interface_sorted(qtbot, db_empty):
    db_empty.add_new_tag("G")
    db_empty.add_new_tag("H")
    db_empty.add_new_tag("O")
    db_empty.add_new_tag("S")
    db_empty.add_new_tag("T")
    widget = cInitialize(qtbot, db_empty)
    cRenameTag(widget, "O", "Z", qtbot)
    # Then see what tags are in the list now
    new_tags = [t.name for t in widget.tagsList.tags]
    assert new_tags == ["G", "H", "S", "T", "Z"]


def test_rename_tag_does_that_in_right_panel_text(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.add_new_tag("old")
    db_empty.tag_paper(u.mine.bibcode, "old")

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    assert widget.rightPanel.tagText.text() == "Tags: old"
    cRenameTag(widget, "old", "new", qtbot)
    assert widget.rightPanel.tagText.text() == "Tags: new"


def test_rename_tag_does_that_in_right_panel_checkboxes(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    db_empty.add_new_tag("old")
    db_empty.tag_paper(u.mine.bibcode, "old")

    widget = cInitialize(qtbot, db_empty)
    cClick(widget.papersList.getPapers()[0], qtbot)
    cClick(widget.rightPanel.editTagsButton, qtbot)
    assert [t.text() for t in widget.rightPanel.getTagCheckboxes()] == ["old"]
    cRenameTag(widget, "old", "new", qtbot)
    assert [t.text() for t in widget.rightPanel.getTagCheckboxes()] == ["new"]


def test_rename_tag_button_comes_back_once_done(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cRenameTag(widget, "Read", "New", qtbot)
    assert widget.tagsList.renameTagButton.isHidden() is False


def test_rename_tag_old_entry_hidden_once_tag_renamed(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cRenameTag(widget, "Read", "New", qtbot)
    assert widget.tagsList.renameTagOldEntry.isHidden() is True


def test_rename_tag_new_entry_hidden_once_tag_renamed(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cRenameTag(widget, "Read", "New", qtbot)
    assert widget.tagsList.renameTagNewEntry.isHidden() is True


def test_rename_tag_button_comes_back_once_cancelled_at_old(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdf", qtbot)
    cPressEscape(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagButton.isHidden() is False


def test_rename_tag_button_comes_back_once_cancelled_at_new(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "Read", qtbot)
    cPressEscape(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagButton.isHidden() is False


def test_rename_tag_old_entry_hidden_once_cancelled(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdf", qtbot)
    cPressEscape(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagOldEntry.isHidden() is True


def test_rename_tag_new_entry_hidden_once_cancelled(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "Read", qtbot)
    cPressEscape(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagNewEntry.isHidden() is True


def test_cancel_renanme_tags_doesnt_rename_db(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # first get the original tags
    original_tags = db_temp.get_all_tags()
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "Read", qtbot)
    cPressEscape(widget.tagsList.renameTagNewEntry, qtbot)
    new_tags = db_temp.get_all_tags()
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_cancel_rename_tags_doesnt_rename_interface(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # first get the original tags
    original_tags = [t.name for t in widget.tagsList.tags]
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "Read", qtbot)
    cPressEscape(widget.tagsList.renameTagNewEntry, qtbot)
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_rename_invalid_old_tag_entry_keeps_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdfsdf", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagOldEntry.isHidden() is False
    assert widget.tagsList.renameTagOldEntry.text() == "sdfsdfsdf"


def test_rename_invalid_old_tag_entry_shows_error_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdfsdf", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    assert widget.tagsList.renameTagErrorText.text() == "This tag does not exist"


def test_rename_invalid_old_tag_entry_keeps_new_hidden(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdfsdf", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagNewEntry.isHidden() is True


def test_rename_invalid_old_tag_error_text_hidden_when_clicked(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdfsdf", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    widget.tagsList.renameTagOldEntry.setCursorPosition(0)
    assert widget.tagsList.renameTagErrorText.isHidden() is True


def test_rename_invalid_old_tag_error_text_hidden_when_text_modified(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "sdfsdfsdf", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    cPressBackspace(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is True


def test_rename_invalid_new_tag_entry_keeps_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "   ", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagNewEntry.isHidden() is False
    assert widget.tagsList.renameTagNewEntry.text() == "   "


def test_rename_invalid_new_tag_entry_shows_error_text_duplicate(qtbot, db_temp):
    db_temp.add_new_tag("New")
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "New", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    assert widget.tagsList.renameTagErrorText.text() == "This tag already exists"


def test_rename_invalid_new_tag_entry_shows_error_text_backticks(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "`New`", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    assert widget.tagsList.renameTagErrorText.text() == "Backticks aren't allowed"


def test_rename_invalid_new_tag_entry_shows_error_text_square_brackets(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "[New]", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    assert widget.tagsList.renameTagErrorText.text() == "Square brackets aren't allowed"


def test_rename_invalid_new_tag_entry_shows_error_text_whitespace(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "   ", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    assert widget.tagsList.renameTagErrorText.text() == "Pure whitespace isn't valid"


def test_rename_invalid_new_tag_entry_shows_error_text_show_all(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "all papers", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    assert widget.tagsList.renameTagErrorText.text() == "Sorry, can't duplicate this"


def test_rename_invalid_new_tag_error_text_hidden_when_clicked(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "   ", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    widget.tagsList.renameTagNewEntry.setCursorPosition(0)
    assert widget.tagsList.renameTagErrorText.isHidden() is True


def test_rename_invalid_new_tag_error_text_hidden_when_text_modified(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    cEnterText(widget.tagsList.renameTagNewEntry, "   ", qtbot)
    cPressEnter(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    cPressBackspace(widget.tagsList.renameTagNewEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is True


def test_renaming_currently_selected_tag_shows_new_tag(qtbot, db_temp):
    assert len(db_temp.get_all_tags()) > 1
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.tags[0], qtbot)
    cRenameTag(widget, widget.tagsList.tags[0].name, "New", qtbot)
    for t in widget.tagsList.tags:
        if t.name == "New":
            assert t.property("is_highlighted") is True
        else:
            assert t.property("is_highlighted") is False
    assert widget.tagsList.showAllButton.property("is_highlighted") is False


def test_cannot_rename_all_papers_tag(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.renameTagButton, qtbot)
    cEnterText(widget.tagsList.renameTagOldEntry, "all papers", qtbot)
    cPressEnter(widget.tagsList.renameTagOldEntry, qtbot)
    assert widget.tagsList.renameTagErrorText.isHidden() is False
    assert widget.tagsList.renameTagErrorText.text() == "Sorry, can't rename this"


# =============
# deleting tags
# =============
def test_clicking_first_tag_delete_button_shows_second_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is False


def test_clicking_first_tag_delete_button_focus_on_entry(qtbot, db_temp, monkeypatch):
    # I tried to test this directly, but was having trouble getting the tests to work
    # properly. Specifically, widget.hasFocus() was not working propertly in tests for
    # whatever reasonSo instead, I'll monkeypatch the setFocus method. I have tested
    # that this works in the actual interface
    setFocus_calls = []
    monkeypatch.setattr(QLineEdit, "setFocus", lambda x: setFocus_calls.append(True))

    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    # assert widget.secondDeleteTagEntry.hasFocus() is True  # would be the best test
    assert setFocus_calls == [True]


def test_clicking_first_tag_delete_button_hides_first_button(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    assert widget.tagsList.firstDeleteTagButton.isHidden() is True


def test_delete_tag_button_and_entry_have_same_height(qtbot, db_empty):
    widget = cInitialize(qtbot, db_empty)
    button_height = widget.tagsList.firstDeleteTagButton.height()
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.height() == button_height


def test_second_delete_tag_entry_is_hidden_when_entry_done(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)  # tag must exist
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_appears_when_first_entry_done(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.thirdDeleteTagButton.isHidden() is False


def test_third_delete_tag_button_and_entry_have_same_height(qtbot, db_empty):
    db_empty.add_new_tag("Read")
    widget = cInitialize(qtbot, db_empty)
    button_1_height = widget.tagsList.firstDeleteTagButton.height()
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    entry_height = widget.tagsList.secondDeleteTagEntry.height()
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    button_2_height = widget.tagsList.thirdDeleteTagButton.height()
    button_3_height = widget.tagsList.thirdDeleteTagCancelButton.height()
    assert button_1_height == entry_height  # already checked, included for clarity
    assert entry_height == button_2_height
    assert button_2_height == button_3_height


def test_third_delete_tag_cancel_button_appears_when_first_entry_done(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.thirdDeleteTagCancelButton.isHidden() is False


def test_second_tag_delete_error_text_hidden_when_first_entry_done(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagErrorText.isHidden() is True


def test_delete_tag_entry_can_exit_with_escape_press_at_any_time(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "sdfsdf", qtbot)
    cPressEscape(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is True
    assert widget.tagsList.firstDeleteTagButton.isHidden() is False


def test_delete_tag_entry_can_exit_with_escape_press_at_any_time_clears_text(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "sdfsdf", qtbot)
    cPressEscape(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.text() == ""


def test_delete_tag_entry_can_exit_with_backspace_when_empty(qtbot, db):
    widget = cInitialize(qtbot, db)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "abc", qtbot)
    # back out those three letters
    for _ in range(3):
        cPressBackspace(widget.tagsList.secondDeleteTagEntry, qtbot)
    # entry should still be visible
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is False
    assert widget.tagsList.firstDeleteTagButton.isHidden() is True
    # with one more backspace, we exit
    cPressBackspace(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is True
    assert widget.tagsList.firstDeleteTagButton.isHidden() is False


def test_third_delete_tag_button_text_is_accurate(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert (
        widget.tagsList.thirdDeleteTagButton.text() == 'Confirm deletion of tag "Read"'
    )


def test_third_delete_tag_cancel_button_text_is_accurate(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert (
        widget.tagsList.thirdDeleteTagCancelButton.text()
        == "Oops, don't delete tag " + '"Read"'
    )


def test_third_delete_tag_button_deletes_tag_from_db_when_pressed(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    original_tags = db_temp.get_all_tags()
    # don't use convenience function, for clarity
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(widget.tagsList.thirdDeleteTagButton, qtbot)
    # check that it's not in the database anymore
    new_tags = db_temp.get_all_tags()
    assert "Read" not in new_tags
    assert len(new_tags) == len(original_tags) - 1


def test_third_delete_tag_button_deletes_tag_from_list_when_pressed(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # first get the original number of tags
    num_original_tags = len([t.name for t in widget.tagsList.tags])
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "Read", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(widget.tagsList.thirdDeleteTagButton, qtbot)
    # Then see what tags are in the list now
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(new_tags) == num_original_tags - 1
    assert not "Read" in new_tags


def test_first_delete_tag_button_comes_back_once_tag_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteTag(widget, "Read", qtbot)
    assert widget.tagsList.firstDeleteTagButton.isHidden() is False


def test_second_delete_tag_entry_hidden_once_tag_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteTag(widget, "Read", qtbot)
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_hides_once_tag_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteTag(widget, "Read", qtbot)
    assert widget.tagsList.thirdDeleteTagButton.isHidden() is True


def test_third_delete_tag_cancel_button_hides_once_tag_deleted(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cDeleteTag(widget, "Read", qtbot)
    assert widget.tagsList.thirdDeleteTagCancelButton.isHidden() is True


def test_first_delete_tag_button_comes_back_once_cancelled(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "tag_1", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(widget.tagsList.thirdDeleteTagCancelButton, qtbot)
    assert widget.tagsList.firstDeleteTagButton.isHidden() is False


def test_second_delete_tag_entry_hidden_once_cancelled(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "tag_1", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(widget.tagsList.thirdDeleteTagCancelButton, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_hides_once_cancelled(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "tag_1", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(widget.tagsList.thirdDeleteTagCancelButton, qtbot)
    assert widget.tagsList.thirdDeleteTagButton.isHidden() is True


def test_third_delete_tag_cancel_button_hides_once_cancelled(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "tag_1", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(widget.tagsList.thirdDeleteTagCancelButton, qtbot)
    assert widget.tagsList.thirdDeleteTagCancelButton.isHidden() is True


def test_cancel_tag_delete_doesnt_delete_any_tags_db(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # first get the original tags
    original_tags = db_temp.get_all_tags()
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "tag_1", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(widget.tagsList.thirdDeleteTagCancelButton, qtbot)
    new_tags = db_temp.get_all_tags()
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_cancel_tag_delete_doesnt_delete_any_tags_interface(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # first get the original tags
    original_tags = [t.name for t in widget.tagsList.tags]
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "tag_1", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    cClick(widget.tagsList.thirdDeleteTagCancelButton, qtbot)
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_invalid_tag_delete_entry_keeps_entry(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "sdfsdfadbsdf", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagEntry.isHidden() is False
    assert widget.tagsList.secondDeleteTagEntry.text() == "sdfsdfadbsdf"


def test_invalid_tag_delete_entry_shows_error_text(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "sdfsdfadbsdf", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagErrorText.isHidden() is False
    assert widget.tagsList.secondDeleteTagErrorText.text() == "This tag does not exist"


def test_cannot_delete_all_papers_tag(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "All Papers", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagErrorText.isHidden() is False
    assert widget.tagsList.secondDeleteTagErrorText.text() == "Sorry, can't delete this"


def test_invalid_tag_delete_entry_keeps_third_hidden(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "sdfsdfadbsdf", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.thirdDeleteTagButton.isHidden() is True


def test_invalid_tag_delete_entry_keeps_third_cancel_hidden(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "sdfsdfadbsdf", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.thirdDeleteTagCancelButton.isHidden() is True


def test_invalid_tag_delete_error_text_hidden_when_clicked(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "sdfsdfadbsdf", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagErrorText.isHidden() is False
    widget.tagsList.secondDeleteTagEntry.setCursorPosition(0)
    assert widget.tagsList.secondDeleteTagErrorText.isHidden() is True


def test_invalid_tag_delete_error_text_hidden_when_text_modified(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.firstDeleteTagButton, qtbot)
    cEnterText(widget.tagsList.secondDeleteTagEntry, "sdfsdfadbsdf", qtbot)
    cPressEnter(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagErrorText.isHidden() is False
    cPressBackspace(widget.tagsList.secondDeleteTagEntry, qtbot)
    assert widget.tagsList.secondDeleteTagErrorText.isHidden() is True


def test_deleting_currently_selected_tag_shows_all_papers(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.tags[0], qtbot)
    cDeleteTag(widget, widget.tagsList.tags[0].name, qtbot)
    assert widget.tagsList.showAllButton.property("is_highlighted") is True
    for paper in widget.papersList.getPapers():
        assert paper.isHidden() is False


# =====================
# exporting a given tag
# =====================
def test_clicking_on_tag_in_left_panel_shows_export_button(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # get a tag from the left panel to click on
    tag = widget.tagsList.tags[0]
    cClick(tag, qtbot)
    assert tag.exportButton.isHidden() is False


def test_clicking_on_show_all_in_left_panel_shows_export_button(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.tags[0], qtbot)
    cClick(widget.tagsList.showAllButton, qtbot)
    assert widget.tagsList.showAllButton.exportButton.isHidden() is False


def test_clicking_on_tag_in_left_panel_removes_export_button(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    # Click on one tag, then another
    for tag in widget.tagsList.tags:
        cClick(tag, qtbot)
        for tag_comp in widget.tagsList.tags:
            if tag.label.text() == tag_comp.label.text():
                assert tag_comp.exportButton.isHidden() is False
            else:
                assert tag_comp.exportButton.isHidden() is True


def test_clicking_on_show_all_in_left_panel_removes_other_exports(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cClick(widget.tagsList.showAllButton, qtbot)
    for tag in widget.tagsList.tags:
        assert tag.exportButton.isHidden() is True


def test_newly_added_tag_has_hidden_export(qtbot, db_temp):
    widget = cInitialize(qtbot, db_temp)
    cAddTag(widget, "newly added tag", qtbot)
    for tag in widget.tagsList.tags:
        if tag.label.text() == "newly added tag":
            assert tag.exportButton.isHidden() is True


def test_clicking_export_all_exports_all(qtbot, db, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidTXT)

    widget = cInitialize(qtbot, db)
    # click on the export all button
    cClick(widget.tagsList.showAllButton.exportButton, qtbot)
    # then open the file and compare it
    with open(mSaveLocTXT, "r") as out_file:
        file_contents = out_file.read()
    # remove the file now before the test, so it always gets deleted
    mSaveLocTXT.unlink()
    # then compare the contents to what we expect
    expected_file_contents = u.tremonti.bibtex + "\n" + u.mine.bibtex + "\n"
    assert file_contents == expected_file_contents


def test_exporting_a_single_tag(qtbot, db_empty, monkeypatch):
    # first, get the database into a format we like. I duplicate this from the db tests
    papers_to_add = [u.bbfh, u.tremonti, u.mine, u.forbes]
    for paper in papers_to_add:
        db_empty.add_paper(paper.bibcode)
    # then tag a few of them
    db_empty.add_new_tag("test_tag")
    tagged_papers = papers_to_add[::2]
    for paper in tagged_papers:
        db_empty.tag_paper(paper.bibcode, "test_tag")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileValidTXT)

    widget = cInitialize(qtbot, db_empty)
    # find the tag to click on, then click it's export button
    for tag in widget.tagsList.tags:
        if tag.name == "test_tag":
            break

    cClick(tag.exportButton, qtbot)
    # then open the file and compare it
    with open(mSaveLocTXT, "r") as out_file:
        file_contents = out_file.read()
    # remove the file now before the test, so it always gets deleted
    mSaveLocTXT.unlink()
    # then compare the contents to what we expect
    expected_file_contents = "\n".join([p.bibtex for p in tagged_papers]) + "\n"
    assert file_contents == expected_file_contents


def test_no_export_happens_if_user_cancels(qtbot, db, monkeypatch):
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mSaveFileNoResponse)
    # Also set up a monkeypatch for the export, so that we can see if anything
    # happened
    export_calls = []
    monkeypatch.setattr(db, "export", lambda x, y: export_calls.append(1))

    widget = cInitialize(qtbot, db)
    # find the tag to click on, then click it's export button
    cClick(widget.tagsList.showAllButton.exportButton, qtbot)
    # then see if anything has happened. I did test my test by using an actual file for
    # the file dialog monkeypatch, and did get 1 export_call
    assert len(export_calls) == 0
