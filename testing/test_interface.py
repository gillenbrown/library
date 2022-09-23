"""
test_interface.py

Perform tests on the GUI using pytest-qt
"""
from pathlib import Path
import random

import pytest
import pytestqt
from PySide2.QtCore import Qt
from PySide2.QtGui import QFontDatabase, QDesktopServices, QGuiApplication
from PySide2.QtWidgets import QApplication, QFileDialog

from library.interface import MainWindow, get_fonts, set_up_fonts, Paper, LeftPanelTag
from library.database import Database
import test_utils as u


def add_my_paper(qtbot, widget):
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
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
    db.add_paper(u.mine.bibcode)
    db.add_paper(u.tremonti.bibcode)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db_temp_tags")
def temporary_database_with_papers_and_tags():
    """
    Fixture to get a database at a temporary path in the current directory. This will be
    removed once the test is done
    """
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Database(file_path)
    db.add_paper(u.mine.bibcode)
    db.add_paper(u.tremonti.bibcode)
    db.add_new_tag("tag_1")
    db.add_new_tag("tag_2")
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="db")
def testing_database():
    """
    Fixture to get the testing database, which has some prefilled info
    """
    return Database(Path(__file__).parent / "testing.db")


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
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.mouseClick(widget.addButton, Qt.LeftButton)
    assert len(empty_db.get_all_bibcodes()) == 1
    assert u.mine.bibcode in empty_db.get_all_bibcodes()


def test_can_add_paper_by_filling_bibcode_then_pressing_enter(qtbot, empty_db):
    assert len(empty_db.get_all_bibcodes()) == 0
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert len(empty_db.get_all_bibcodes()) == 1
    assert u.mine.bibcode in empty_db.get_all_bibcodes()


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
    qtbot.waitExposed(widget)
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


def test_paper_initialization_has_correct_bibcode(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.mine.bibcode, db, widget.rightPanel)
    assert new_paper.bibcode == u.mine.bibcode


def test_paper_initialization_has_correct_title_in_the_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.mine.bibcode, db, widget.rightPanel)
    assert new_paper.titleText.text() == u.mine.title


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
    new_paper = Paper(u.mine.bibcode, db, widget.rightPanel)
    assert new_paper.citeText.text() == db.get_cite_string(u.mine.bibcode)


def test_cannot_initialize_paper_thats_not_in_database(qtbot, empty_db):
    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    with pytest.raises(AssertionError):
        Paper(u.mine.bibcode, empty_db, widget.rightPanel)


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
    assert widget.papersList.papers[0].bibcode == u.mine.bibcode


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
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
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
    new_paper = Paper(u.mine.bibcode, db, widget.rightPanel)
    with pytest.raises(AssertionError):
        widget.papersList.addPaper(new_paper)


def test_clicking_on_paper_puts_title_in_right_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    assert widget.rightPanel.titleText.text() in [u.mine.title, u.tremonti.title]


def test_clicking_on_paper_puts_cite_string_in_right_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    possible_cites = [
        db.get_cite_string(u.mine.bibcode),
        db.get_cite_string(u.tremonti.bibcode),
    ]
    assert widget.rightPanel.citeText.text() in possible_cites


def test_clicking_on_paper_puts_abstract_in_right_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    assert widget.rightPanel.abstractText.text() in [
        u.mine.abstract,
        u.tremonti.abstract,
    ]


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
    assert empty_db.get_paper_attribute(u.mine.bibcode, "local_file") == test_loc


def test_double_clicking_on_paper_without_local_file_but_not_choosing_doesnt_add_it(
    qtbot, empty_db, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return ("", "")

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert empty_db.get_paper_attribute(u.mine.bibcode, "local_file") == None


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
    empty_db.set_paper_attribute(u.mine.bibcode, "local_file", test_loc)
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
        return ("", "")

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)  # do not add file location
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert open_calls == []


def test_get_tags_from_paper_object_is_correct(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    paper = widget.papersList.papers[0]
    assert paper.getTags() == db.get_paper_tags(paper.bibcode)


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
    assert db_temp.paper_has_tag(u.mine.bibcode, "Test Tag") is False


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
    new_tag = LeftPanelTag("Test Tag", widget.papersList)
    with pytest.raises(AssertionError):
        widget.tagsList.addTag(new_tag)


def test_right_panel_tags_should_list_all_tags_in_database(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get all tags in both the list and database, then check that they're the same
    db_tags = db.get_all_tags()
    list_tags = [t.text() for t in widget.rightPanel.tags]
    assert sorted(db_tags) == sorted(list_tags)


def test_right_panel_tags_checked_match_paper_that_is_selected(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get a random paper, we already tested that it has at least one tag
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    # go through each checkbox to verify the tag
    for tag in widget.rightPanel.tags:
        if db.paper_has_tag(paper.bibcode, tag.text()):
            assert tag.isChecked()
        else:
            assert not tag.isChecked()


def test_checking_tag_in_checklist_adds_tag_to_paper_in_database(qtbot, db_temp):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_temp.add_new_tag(tag)
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    # this will show the tags in the right panel. Click on a few
    to_check = ["T1", "T3", "T4"]
    for tag_item in widget.rightPanel.tags:
        if tag_item.text() in to_check:
            tag_item.setChecked(True)
    # Then check that these tags are listen in the database
    for tag in db_temp.get_all_tags():
        if tag in to_check:
            assert db_temp.paper_has_tag(paper.bibcode, tag) is True
        else:
            assert db_temp.paper_has_tag(paper.bibcode, tag) is False


def test_unchecking_tag_in_checklist_removes_tag_from_paper_in_database(qtbot, db_temp):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_temp.add_new_tag(tag)
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.papers[0]
    # add all tags to this paper
    for tag in db_temp.get_all_tags():
        db_temp.tag_paper(paper.bibcode, tag)
    # click on the paper to show it in the right panel
    qtbot.mouseClick(paper, Qt.LeftButton)
    # click on the tags we want to remove
    to_uncheck = ["T1", "T3", "T4"]
    for tag_item in widget.rightPanel.tags:
        if tag_item.text() in to_uncheck:
            tag_item.setChecked(False)
    # Then check that these tags are listen in the database
    for tag in db_temp.get_all_tags():
        if tag in to_uncheck:
            assert db_temp.paper_has_tag(paper.bibcode, tag) is False
        else:
            assert db_temp.paper_has_tag(paper.bibcode, tag) is True


def test_all_papers_start_not_hidden(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    for paper in widget.papersList.papers:
        assert not paper.isHidden()


def test_clicking_on_tag_in_left_panel_hides_papers(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get a tag from the left panel to click on
    left_tag = widget.tagsList.tags[0]
    qtbot.mouseClick(left_tag, Qt.LeftButton)
    # then check the tags that are in shown papers
    for paper in widget.papersList.papers:
        if left_tag.text() in db.get_paper_tags(paper.bibcode):
            assert paper.isHidden() is False
        else:
            assert paper.isHidden() is True


def test_clicking_on_show_all_button_shows_all_papers(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # First click on a tag to restrict the number of papers shown
    left_tag = widget.tagsList.tags[0]
    qtbot.mouseClick(left_tag, Qt.LeftButton)
    # then click on the button to show all
    qtbot.mouseClick(widget.tagsList.showAllButton, Qt.LeftButton)
    # then check that all are shown
    for paper in widget.papersList.papers:
        assert paper.isHidden() is False


def test_tags_selection_checkboxes_is_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    for tag in widget.rightPanel.tags:
        assert tag.isHidden() is True


def test_tags_selection_edit_button_is_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.editTagsButton.isHidden() is True


def test_tags_selection_done_editing_button_is_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.doneEditingTagsButton.isHidden() is True


def test_tags_selection_edit_button_appears_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.editTagsButton.isHidden() is False


def test_tags_selection_done_editing_button_doesnt_appear_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.doneEditingTagsButton.isHidden() is True


def test_tags_selection_checkboxes_doesnt_appear_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    for tag in widget.rightPanel.tags:
        assert tag.isHidden() is True


def test_tags_selection_edit_button_is_hidden_when_pressed(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    assert widget.rightPanel.editTagsButton.isHidden() is True


def test_tags_selection_done_editing_buttons_is_shown_when_edit_is_pressed(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    assert widget.rightPanel.doneEditingTagsButton.isHidden() is False


def test_tags_selection_edit_button_shown_again_when_done_editing_pressed(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.doneEditingTagsButton, Qt.LeftButton)
    assert widget.rightPanel.editTagsButton.isHidden() is False


def test_tags_selection_done_editing_button_is_hidden_when_pressed(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.doneEditingTagsButton, Qt.LeftButton)
    assert widget.rightPanel.doneEditingTagsButton.isHidden() is True


def test_tags_selection_checkboxes_are_unhidden_when_edit_is_pressed(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    for tag in widget.rightPanel.tags:
        assert tag.isHidden() is False


def test_tags_selection_checkboxes_are_hidden_when_done_editing(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.doneEditingTagsButton, Qt.LeftButton)
    for tag in widget.rightPanel.tags:
        assert tag.isHidden() is True


def test_clicking_bibtex_button_copies_bibtex(qtbot, db, monkeypatch):
    # Here we need to use monkeypatch to simulate the clipboard
    clipboard = QGuiApplication.clipboard()
    texts = []
    monkeypatch.setattr(clipboard, "setText", lambda x: texts.append(x))

    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers in the right panel
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    # then click on the bibtext button
    qtbot.mouseClick(widget.rightPanel.copyBibtexButton, Qt.LeftButton)
    assert len(texts) == 1
    assert texts[0] in [u.mine.bibtex, u.tremonti.bibtex]


def test_copy_bibtex_button_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.copyBibtexButton.isHidden() is True


def test_copy_bibtex_button_appears_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.copyBibtexButton.isHidden() is False


def test_first_delete_paper_button_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is True


def test_second_delete_paper_button_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is True


def test_first_delete_paper_button_appears_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is False


def test_second_delete_paper_button_does_not_appear_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is True


def test_second_delete_paper_button_appears_when_first_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is False


def test_second_delete_paper_button_is_red(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # need to click on paper so the button shows up
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    stylesheet = widget.rightPanel.secondDeletePaperButton.styleSheet()
    assert stylesheet == "background-color: #FFCCCC;"


def test_first_delete_paper_button_disappears_when_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is True


def test_first_delete_buttons_reset_when_on_new_paper(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is False


def test_second_delete_buttons_reset_when_on_new_paper(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is True


def test_second_delete_paper_button_deletes_paper_from_database_when_pressed(
    qtbot, db_temp
):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    # check that it's not in the database anymore
    with pytest.raises(ValueError):
        db_temp.get_paper_attribute(paper.bibcode, "title")


def test_second_delete_paper_button_deletes_paper_from_interface_when_pressed(
    qtbot, db_temp
):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    bibcode = widget.papersList.papers[0].bibcode
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    # check that it's not in the center list anymore
    for paper in widget.papersList.papers:
        assert bibcode != paper.bibcode


def test_right_panel_edit_tags_button_is_hidden_when_paper_is_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.editTagsButton.isHidden()


def test_right_panel_done_editing_tags_button_is_hidden_when_paper_is_deleted(
    qtbot, db_temp
):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    bibcode = widget.papersList.papers[0].bibcode
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.doneEditingTagsButton.isHidden()


def test_right_panel_copy_bibtex_button_is_hidden_when_paper_is_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.copyBibtexButton.isHidden()


def test_right_panel_first_delete_button_is_hidden_when_paper_is_deleted(
    qtbot, db_temp
):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.firstDeletePaperButton.isHidden()


def test_right_panel_second_delete_button_is_hidden_when_paper_is_deleted(
    qtbot, db_temp
):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperButton.isHidden()


def test_right_panel_title_text_is_blank_when_paper_is_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.titleText.text() == ""


def test_right_panel_cite_text_is_blank_when_paper_is_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.citeText.text() == ""


def test_right_panel_tag_text_is_blank_when_paper_is_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.tagText.text() == ""


def test_right_panel_abstract_text_is_default_when_paper_is_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert (
        widget.rightPanel.abstractText.text()
        == "Click on a paper to show its details here"
    )


def test_first_delete_tag_entry_shown_at_beginning(qtbot, db_temp_tags):

    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.firstDeleteTagEntry.isHidden() is False


def test_first_delete_tag_entry_has_placeholder_text(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    text = "Enter a tag's name here to delete it"
    assert widget.firstDeleteTagEntry.placeholderText() == text


def test_second_delete_tag_entry_hidden_at_beginning(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.secondDeleteTagButton.isHidden() is True


def test_second_cancel_tag_entry_hidden_at_beginning(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.secondDeleteTagCancelButton.isHidden() is True


def test_first_delete_tag_button_is_hidden_when_entry_done(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert widget.firstDeleteTagEntry.isHidden() is True


def test_second_delete_tag_button_appears_when_first_entry_done(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagButton.isHidden() is False


def test_second_delete_tag_cancel_button_appears_when_first_entry_done(
    qtbot, db_temp_tags
):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagCancelButton.isHidden() is False


def test_second_delete_tag_button_is_red(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    stylesheet = widget.secondDeleteTagButton.styleSheet()
    assert stylesheet == "background-color: #FFCCCC;"


def test_second_delete_tag_cancel_button_is_red(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    stylesheet = widget.secondDeleteTagCancelButton.styleSheet()
    assert stylesheet == "background-color: #FFCCCC;"


def test_second_delete_tag_button_text_is_accurate(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert (
        widget.secondDeleteTagButton.text()
        == 'Click to confirm deletion of tag "tag_1"'
    )


def test_second_delete_tag_cancel_button_text_is_accurate(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert (
        widget.secondDeleteTagCancelButton.text()
        == 'Click to cancel the deletion of tag "tag_1"'
    )


def test_second_delete_tag_button_deletes_tag_from_db_when_pressed(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    original_tags = db_temp_tags.get_all_tags()
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagButton, Qt.LeftButton)
    # check that it's not in the database anymore
    new_tags = db_temp_tags.get_all_tags()
    assert "tag_1" not in new_tags
    assert len(new_tags) == len(original_tags) - 1


def test_second_delete_tag_button_deletes_tag_from_list_when_pressed(
    qtbot, db_temp_tags
):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original number of tags
    num_original_tags = len([t.name for t in widget.tagsList.tags])
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagButton, Qt.LeftButton)
    # Then see what tags are in the list now
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(new_tags) == num_original_tags - 1
    assert not "tag_1" in new_tags


def test_first_delete_tag_button_comes_back_once_tag_deleted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagButton, Qt.LeftButton)
    assert widget.firstDeleteTagEntry.isHidden() is False


def test_second_delete_tag_button_hides_once_tag_deleted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagButton.isHidden() is True


def test_second_delete_tag_cancel_button_hides_once_tag_deleted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagCancelButton.isHidden() is True


def test_first_delete_tag_button_comes_back_once_cancelled(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagCancelButton, Qt.LeftButton)
    assert widget.firstDeleteTagEntry.isHidden() is False


def test_second_delete_tag_button_hides_once_cancelled(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original number of tags
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagCancelButton, Qt.LeftButton)
    assert widget.secondDeleteTagButton.isHidden() is True


def test_second_delete_tag_cancel_button_hides_once_cancelled(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original number of tags
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagCancelButton, Qt.LeftButton)
    assert widget.secondDeleteTagCancelButton.isHidden() is True


def test_cancel_tag_delete_doesnt_delete_any_tags_db(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original tags
    original_tags = db_temp_tags.get_all_tags()
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagCancelButton, Qt.LeftButton)
    new_tags = db_temp_tags.get_all_tags()
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_cancel_tag_delete_doesnt_delete_any_tags_interface(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original tags
    original_tags = [t.name for t in widget.tagsList.tags]
    qtbot.keyClicks(widget.firstDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.secondDeleteTagCancelButton, Qt.LeftButton)
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_invalid_tag_delete_entry_resets_entry(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original tags
    qtbot.keyClicks(widget.firstDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert widget.firstDeleteTagEntry.text() == ""


def test_invalid_tag_delete_entry_keeps_first_visible(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original tags
    qtbot.keyClicks(widget.firstDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert widget.firstDeleteTagEntry.isHidden() is False


def test_invalid_tag_delete_entry_keeps_second_hidden(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original tags
    qtbot.keyClicks(widget.firstDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagButton.isHidden() is True


def test_invalid_tag_delete_entry_keeps_second_cancel_hidden(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original tags
    qtbot.keyClicks(widget.firstDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.firstDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagCancelButton.isHidden() is True


def test_tag_checkboxes_are_hidden_when_paper_clicked(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # click on a paper, then click the edit tags button
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    # click on a different paper
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    # the tag edit checkboxes should all be hidden
    for t in widget.rightPanel.tags:
        assert t.isHidden()


def test_done_editing_button_is_hidden_when_paper_clicked(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # click on a paper, then click the edit tags button
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    # click on a different paper
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    # the tag edit checkboxes should all be hidden
    assert widget.rightPanel.doneEditingTagsButton.isHidden()


def test_newly_added_tags_appear_in_right_panel(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # first add a tag
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    # then look at the tags in the right panel
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert "Test Tag" in [t.text() for t in widget.rightPanel.tags]


def test_adding_tags_doesnt_duplicate_tags_in_right_panel(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # first add a tag
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    # then look at the tags in the right panel
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert ["Test Tag"] == [t.text() for t in widget.rightPanel.tags]

    # add another tag, then check again
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag 2")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    # then look at the tags in the right panel
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert ["Test Tag", "Test Tag 2"] == [t.text() for t in widget.rightPanel.tags]
