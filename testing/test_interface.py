"""
test_interface.py

Perform tests on the GUI using pytest-qt
"""
from pathlib import Path
import random

import pytest
import pytestqt
from PySide2.QtCore import Qt
from PySide2.QtGui import QFontDatabase, QDesktopServices
from PySide2.QtWidgets import QApplication, QFileDialog

from library.interface import MainWindow, get_fonts, set_up_fonts, Paper, Tag
from library.database import Database
import test_utils as u


def add_my_paper(qtbot, widget):
    qtbot.keyClicks(widget.searchBar, u.my_bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)


@pytest.fixture(name="empty_db")
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
    db.add_paper(u.my_bibcode)
    db.add_paper(u.tremonti_bibcode)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db")
def testing_database():
    """
    Fixture to get the testing database, which has some prefilled info
    """
    return Database(Path(__file__).parent / "testing.db")


def test_all_fonts_are_found_by_get_fonts():
    font_dir = (Path(__file__).parent.parent / "fonts").absolute()
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
    # q tbot is needed to initialize the application
    fontDb = QFontDatabase()

    assert not fontDb.hasFamily("Lobster")
    assert not fontDb.hasFamily("Cabin")

    set_up_fonts()

    assert fontDb.hasFamily("Lobster")
    assert fontDb.hasFamily("Cabin")


def test_window_initial_width(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.size().width() == 1000


def test_window_initial_height(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.size().height() == 600


def test_title_is_has_text_saying_library(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.title.text() == "Library"


def test_title_is_centered(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.title.alignment() == Qt.AlignCenter


def test_title_is_lobster_font(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.title.font().family() == "Lobster"


def test_title_is_correct_font_size(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.title.font().pointSize() == 40


def test_title_has_correct_height_in_pixels(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.title.height() == 60


def test_search_bar_has_placeholder_text(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    text = "Enter your paper URL or ADS bibcode here"
    assert widget.searchBar.placeholderText() == text


def test_search_bar_has_correct_font_family(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.searchBar.font().family() == "Cabin"


def test_search_bar_has_correct_font_size(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.searchBar.font().pointSize() == 14


def test_add_button_has_correct_font_family(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.addButton.font().family() == "Cabin"


def test_add_button_has_correct_font_size(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.addButton.font().pointSize() == 14


def test_add_button_and_search_bar_have_almost_same_height(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    height_ratio = widget.addButton.height() / widget.searchBar.height()
    assert 0.8 < height_ratio < 1.3


def test_add_button_and_search_bar_are_much_shorter_than_title(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.addButton.height() < 0.6 * widget.title.height()
    assert widget.searchBar.height() < 0.6 * widget.title.height()


def test_can_add_paper_by_filling_bibcode_then_clicking_button(qtbot, empty_db):
    assert len(empty_db.get_all_bibcodes()) == 0
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.my_bibcode)
    qtbot.mouseClick(widget.addButton, Qt.LeftButton)
    assert len(empty_db.get_all_bibcodes()) == 1
    assert u.my_bibcode in empty_db.get_all_bibcodes()


def test_can_add_paper_by_filling_bibcode_then_pressing_enter(qtbot, empty_db):
    assert len(empty_db.get_all_bibcodes()) == 0
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.my_bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert len(empty_db.get_all_bibcodes()) == 1
    assert u.my_bibcode in empty_db.get_all_bibcodes()


def test_testing_database_was_premade_with_some_papers(db):
    assert len(db.get_all_bibcodes()) > 0


def test_testing_database_was_premade_with_some_tags(db):
    assert len(db.get_all_tags()) > 0


def test_can_exit_action_actually_exit_the_app(qtbot, db, monkeypatch):
    # see https://pytest-qt.readthedocs.io/en/3.3.0/app_exit.html
    # It's hard to actually test the menu item, so I'll skip this for now
    # https://github.com/pytest-dev/pytest-qt/issues/195
    exit_calls = []
    monkeypatch.setattr(QApplication, "quit", lambda: exit_calls.append(1))

    widget = MainWindow(db)
    qtbot.addWidget(widget)
    widget.exitAction.trigger()

    assert exit_calls == [1]


def test_can_exit_keyboard_shortcut_exit_the_app(qtbot, db, monkeypatch):
    # see https://pytest-qt.readthedocs.io/en/3.3.0/app_exit.html
    # It's hard to actually test the menu item, so I'll skip this for now
    # https://github.com/pytest-dev/pytest-qt/issues/195
    exit_calls = []
    monkeypatch.setattr(QApplication, "quit", lambda: exit_calls.append(1))

    widget = MainWindow(db)
    qtbot.addWidget(widget)
    widget.show()  # needed to activate keyboard shortcuts
    qtbot.waitForWindowShown(widget)
    qtbot.keyPress(widget, "q", Qt.ControlModifier)

    assert exit_calls == [1]


def test_right_panel_title_is_empty_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.titleText.text() == ""


def test_right_panel_cite_text_is_empty_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.citeText.text() == ""


def test_right_panel_abstract_is_placeholder_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    true_text = "Click on a paper to show its details here"
    assert widget.rightPanel.abstractText.text() == true_text


def test_right_panel_tags_is_empty_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.tagText.text() == ""


def test_right_panel_title_text_has_correct_font_family(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.titleText.font().family() == "Cabin"


def test_right_panel_cite_text_has_correct_font_family(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.citeText.font().family() == "Cabin"


def test_right_panel_abstract_text_has_correct_font_family(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.abstractText.font().family() == "Cabin"


def test_right_panel_tag_text_has_correct_font_family(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.tagText.font().family() == "Cabin"


def test_right_panel_title_text_has_correct_font_size(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.titleText.font().pointSize() == 20


def test_right_panel_cite_text_has_correct_font_size(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.citeText.font().pointSize() == 16


def test_right_panel_abstract_text_has_correct_font_size(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.abstractText.font().pointSize() == 14


def test_right_panel_tag_text_has_correct_font_size(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.tagText.font().pointSize() == 14


def test_right_panel_title_text_has_word_wrap_on(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.titleText.wordWrap()


def test_right_panel_cite_text_has_word_wrap_on(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.citeText.wordWrap()


def test_right_panel_abstract_text_has_word_wrap_on(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.abstractText.wordWrap()


def test_right_panel_tag_text_has_word_wrap_on(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.tagText.wordWrap()


def test_right_panel_title_can_be_set(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    widget.rightPanel.setPaperDetails("Test Title", "", "", [""])
    assert widget.rightPanel.titleText.text() == "Test Title"


def test_right_panel_cite_text_can_be_set(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    widget.rightPanel.setPaperDetails("", "Test cite text", "", [""])
    assert widget.rightPanel.citeText.text() == "Test cite text"


def test_right_panel_abstract_can_be_set(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    widget.rightPanel.setPaperDetails("", "", "Test Abstract", [""])
    assert widget.rightPanel.abstractText.text() == "Test Abstract"


def test_right_panel_tags_can_be_set(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    widget.rightPanel.setPaperDetails("", "", "", ["Tag 1", "Test", "ABC"])
    assert widget.rightPanel.tagText.text() == "Tags: Tag 1, Test, ABC"


def test_paper_initialization_has_correct_bibcode(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.my_bibcode, db, widget.rightPanel)
    assert new_paper.bibcode == u.my_bibcode


def test_paper_initialization_has_correct_title(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.my_bibcode, db, widget.rightPanel)
    assert new_paper.title == u.my_title


def test_paper_initialization_has_correct_cite_string(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.my_bibcode, db, widget.rightPanel)
    assert db.get_cite_string(u.my_bibcode) == new_paper.citeString


def test_paper_initialization_has_correct_abstract(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.my_bibcode, db, widget.rightPanel)
    assert new_paper.abstract == u.my_abstract


def test_paper_initialization_has_correct_title_in_the_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.my_bibcode, db, widget.rightPanel)
    assert new_paper.titleText.text() == u.my_title


def test_paper_title_has_correct_font_family(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    assert paper.titleText.font().family() == "Cabin"


def test_paper_cite_text_has_correct_font_family(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    assert paper.citeText.font().family() == "Cabin"


def test_paper_title_has_correct_font_size(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    assert paper.titleText.font().pointSize() == 16


def test_paper_cite_string_has_correct_font_size(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    assert paper.citeText.font().pointSize() == 12


def test_paper_initialization_has_correct_cite_string_in_the_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.my_bibcode, db, widget.rightPanel)
    assert new_paper.citeText.text() == db.get_cite_string(u.my_bibcode)


def test_cannot_initialize_paper_thats_not_in_database(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    with pytest.raises(AssertionError):
        Paper(u.my_bibcode, empty_db, widget.rightPanel)


def test_all_papers_in_database_are_in_the_paper_list_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    papers_list_bibcodes = [p.bibcode for p in widget.papersList.papers]
    assert sorted(papers_list_bibcodes) == sorted(db.get_all_bibcodes())


def test_adding_paper_adds_paper_to_interface(qtbot, empty_db):
    widget = MainWindow(empty_db)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    add_my_paper(qtbot, widget)
    assert len(widget.papersList.papers) == 1


def test_adding_paper_adds_correct_paper_to_interface(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    add_my_paper(qtbot, widget)
    assert widget.papersList.papers[0].bibcode == u.my_bibcode


def test_adding_paper_clears_search_bar_if_successful(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    add_my_paper(qtbot, widget)
    assert widget.searchBar.text() == ""


def test_adding_paper_does_not_clear_search_bar_if_not_successful(qtbot, empty_db):
    widget = MainWindow(empty_db)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.text() == "nonsense"


def test_adding_paper_does_clear_search_bar_if_already_in_library(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.my_bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.text() == ""


def test_paper_cannot_be_added_twice(qtbot, empty_db):
    widget = MainWindow(empty_db)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    add_my_paper(qtbot, widget)
    assert len(widget.papersList.papers) == 1
    # add it again
    add_my_paper(qtbot, widget)
    assert len(widget.papersList.papers) == 1


def test_duplicate_in_internal_paper_list_raises_error(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.my_bibcode, db, widget.rightPanel)
    with pytest.raises(AssertionError):
        widget.papersList.addPaper(new_paper)


def test_clicking_on_paper_puts_title_in_right_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    assert widget.rightPanel.titleText.text() in [u.my_title, u.tremonti_title]


def test_clicking_on_paper_puts_cite_string_in_right_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    possible_cites = [
        db.get_cite_string(u.my_bibcode),
        db.get_cite_string(u.tremonti_bibcode),
    ]
    assert widget.rightPanel.citeText.text() in possible_cites


def test_clicking_on_paper_puts_abstract_in_right_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    assert widget.rightPanel.abstractText.text() in [u.my_abstract, u.tremonti_abstract]


def test_clicking_on_paper_puts_tags_in_right_panel(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # Add some tags to the database - this is tested below
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        qtbot.keyClicks(widget.tagsList.addTagBar, tag)
        qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)

    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    # add one of the tags to this paper - this is done through the database, not the
    # actual adding tags functionality - that will be tested below
    db_temp.tag_paper(paper.bibcode, "T1")
    db_temp.tag_paper(paper.bibcode, "T3")
    db_temp.tag_paper(paper.bibcode, "T5")
    # then click on the paper
    qtbot.mouseClick(paper, Qt.LeftButton)
    assert widget.rightPanel.tagText.text() == "Tags: T1, T3, T5"


def test_double_clicking_on_paper_without_local_file_asks_user(
    qtbot, empty_db, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input
    test_loc = "/Users/gillenb/test.pdf"
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return test_loc, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert empty_db.get_paper_attribute(u.my_bibcode, "local_file") == test_loc


def test_double_clicking_on_paper_without_local_file_but_not_choosing_doesnt_add_it(
    qtbot, empty_db, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return ""

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert empty_db.get_paper_attribute(u.my_bibcode, "local_file") == None


def test_double_clicking_on_paper_with_local_file_opens_it(
    qtbot, empty_db, monkeypatch
):
    # Here we need to use monkeypatch to simulate opening the file
    test_loc = "/Users/gillenb/test.pdf"
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)
    empty_db.set_paper_attribute(u.my_bibcode, "local_file", test_loc)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    # since this already has a URL it should be added
    assert open_calls == [f"file:{test_loc}"]


def test_double_clicking_on_paper_without_local_file_selects_and_opens_it(
    qtbot, empty_db, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input and open files
    test_loc = "/Users/gillenb/test.pdf"
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return test_loc, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)  # do not add file location
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert open_calls == [f"file:{test_loc}"]


def test_dclicking_on_paper_without_local_file_but_not_choosing_doesnt_add_or_open_it(
    qtbot, empty_db, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input and open files
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return ""

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)  # do not add file location
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert open_calls == []


def test_add_tag_text_bar_has_correct_font_size(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.tagsList.addTagBar.font().pointSize() == 14


def test_add_tag_text_bar_has_correct_font_family(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    assert widget.tagsList.addTagBar.font().family() == "Cabin"


def test_add_tag_text_bar_has_correct_placeholder_text(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    text = "Add a new tag here"
    assert widget.tagsList.addTagBar.placeholderText() == text


def test_can_add_tag_by_filling_tag_name_then_pressing_enter(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    assert db_temp.paper_has_tag(u.my_bibcode, "Test Tag") is False


def test_can_add_tag_to_list_by_filling_tag_name_then_pressing_enter(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    tag_names = [t.name for t in widget.tagsList.tags]
    assert "Test Tag" in tag_names


def test_tag_name_entry_is_cleared_after_successful_entry(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    # this has been tested to work
    assert widget.tagsList.addTagBar.text() == ""


def test_tag_name_entry_is_not_cleared_after_duplicate_tag_attempt(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    # this has been tested to work and now be clear, so try it again
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    assert widget.tagsList.addTagBar.text() == "Test Tag"


def test_all_tags_in_database_are_in_the_tag_list_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    tags_list = [t.name for t in widget.tagsList.tags]
    assert sorted(tags_list) == sorted(db.get_all_tags())


def test_tag_has_correct_name(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the tags, not sure which
    tag = widget.tagsList.tags[0]
    assert tag.text() == tag.name


def test_tag_has_correct_font_family(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the tags, not sure which
    tag = widget.tagsList.tags[0]
    assert tag.font().family() == "Cabin"


def test_tag_has_correct_font_size(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the tags, not sure which
    tag = widget.tagsList.tags[0]
    assert tag.font().family() == "Cabin"


def test_duplicate_in_internal_tags_list_raises_error(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    new_tag = Tag("Test Tag")
    with pytest.raises(AssertionError):
        widget.tagsList.addTag(new_tag)


def test_right_panel_tags_should_list_all_tags_in_database(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get all tags in both the list and database, then check that they're the same
    db_tags = db.get_all_tags()
    list_tags = [t.text() for t in widget.rightPanel.tagCheckboxes.tags]
    assert sorted(db_tags) == sorted(list_tags)
