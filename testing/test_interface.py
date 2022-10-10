"""
test_interface.py

Perform tests on the GUI using pytest-qt
"""
import os
from pathlib import Path
import random

import pytest
import pytestqt
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QDesktopServices, QGuiApplication
from PySide6.QtWidgets import QApplication, QFileDialog

from library.interface import MainWindow, get_fonts, set_up_fonts, Paper, LeftPanelTag
from library.database import Database
import test_utils as u


def add_my_paper(qtbot, widget):
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)


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


@pytest.fixture(name="db_empty_change_ads_key")
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


@pytest.fixture(name="db")
def testing_database():
    """
    Fixture to get the testing database, which has some prefilled info. This avoids
    lots of unnecessary ADS calls
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
    # qtbot is needed to initialize the application
    assert not QFontDatabase.hasFamily("Lobster")
    assert not QFontDatabase.hasFamily("Cabin")

    set_up_fonts()

    assert QFontDatabase.hasFamily("Lobster")
    assert QFontDatabase.hasFamily("Cabin")


def test_window_initial_width(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.size().width() == 1000


def test_window_initial_height(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.size().height() == 600


def test_title_is_has_text_saying_library(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.title.text() == "Library"


def test_title_is_centered(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.title.alignment() == Qt.AlignCenter


def test_title_is_lobster_font(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.title.font().family() == "Lobster"


def test_title_is_correct_font_size(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.title.font().pointSize() == 40


def test_title_has_correct_height_in_pixels(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.title.height() == 60


def test_search_bar_has_placeholder_text(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    text = "Enter your paper URL or ADS bibcode here"
    assert widget.searchBar.placeholderText() == text


def test_search_bar_has_correct_font_family(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.searchBar.font().family() == "Cabin"


def test_search_bar_has_correct_font_size(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.searchBar.font().pointSize() == 14


def test_add_button_has_correct_font_family(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.addButton.font().family() == "Cabin"


def test_add_button_has_correct_font_size(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.addButton.font().pointSize() == 14


def test_add_button_and_search_bar_have_almost_same_height(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    height_ratio = widget.addButton.height() / widget.searchBar.height()
    assert 0.8 < height_ratio < 1.3


def test_add_button_and_search_bar_are_much_shorter_than_title(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.addButton.height() < 0.6 * widget.title.height()
    assert widget.searchBar.height() < 0.6 * widget.title.height()


def test_can_add_paper_by_filling_bibcode_then_clicking_button(qtbot, db_empty):
    assert len(db_empty.get_all_bibcodes()) == 0
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.mouseClick(widget.addButton, Qt.LeftButton)
    assert len(db_empty.get_all_bibcodes()) == 1
    assert u.mine.bibcode in db_empty.get_all_bibcodes()


def test_can_add_paper_by_filling_bibcode_then_pressing_enter(qtbot, db_empty):
    assert len(db_empty.get_all_bibcodes()) == 0
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert len(db_empty.get_all_bibcodes()) == 1
    assert u.mine.bibcode in db_empty.get_all_bibcodes()


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
    new_paper = Paper(u.mine.bibcode, db, widget.rightPanel, widget.papersList)
    assert new_paper.bibcode == u.mine.bibcode


def test_paper_initialization_has_correct_title_in_the_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    new_paper = Paper(u.mine.bibcode, db, widget.rightPanel, widget.papersList)
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
    new_paper = Paper(u.mine.bibcode, db, widget.rightPanel, widget.papersList)
    assert new_paper.citeText.text() == db.get_cite_string(u.mine.bibcode)


def test_paper_initialization_has_accents_in_author_list(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    db_empty.add_paper(u.juan.bibcode)
    new_paper = Paper(u.juan.bibcode, db_empty, widget.rightPanel, widget.papersList)
    assert "á" in new_paper.citeText.text()


def test_cannot_initialize_paper_thats_not_in_database(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    with pytest.raises(AssertionError):
        Paper(u.mine.bibcode, db_empty, widget.rightPanel, widget.papersList)


def test_all_papers_in_database_are_in_the_paper_list_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    papers_list_bibcodes = [p.bibcode for p in widget.papersList.papers]
    assert sorted(papers_list_bibcodes) == sorted(db.get_all_bibcodes())


def test_adding_paper_adds_paper_to_interface(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    add_my_paper(qtbot, widget)
    assert len(widget.papersList.papers) == 1


def test_adding_paper_adds_correct_paper_to_interface(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    add_my_paper(qtbot, widget)
    assert widget.papersList.papers[0].bibcode == u.mine.bibcode


def test_textedit_is_not_in_error_state_at_beginning(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert widget.searchBar.property("error") is False


def test_textedit_error_message_hidden_at_beginning(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert widget.searchBarErrorText.isHidden() is True


def test_add_paper_button_shown_at_beginning(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert widget.addButton.isHidden() is False


def test_adding_paper_clears_search_bar_if_successful(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    add_my_paper(qtbot, widget)
    assert widget.searchBar.text() == ""


def test_adding_paper_does_not_clear_search_bar_if_not_successful(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.text() == "nonsense"


def test_adding_bad_paper_shows_error_formatting_of_textedit(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.property("error") is True


def test_adding_bad_paper_shows_error_text(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBarErrorText.isHidden() is False
    assert (
        widget.searchBarErrorText.text() == "This paper was not found in ADS. "
        "If it was just added to the arXiv, ADS may not have registered it."
    )


def test_adding_bad_paper_hides_add_button(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.addButton.isHidden() is True


def test_search_bar_and_error_text_have_almost_same_height(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a bad paper, which is when this situation arises
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    height_ratio = widget.searchBarErrorText.height() / widget.searchBar.height()
    assert 0.8 < height_ratio < 1.3


def test_search_bar_and_error_text_are_much_shorter_than_title(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a bad paper, which is when this situation arises
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.height() < 0.6 * widget.title.height()
    assert widget.searchBarErrorText.height() < 0.6 * widget.title.height()


def test_bad_paper_error_formatting_of_textedit_reset_after_any_clicking(
    qtbot, db_empty
):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBar.property("error") is False


def test_bad_paper_error_message_of_textedit_reset_after_any_clicking(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBarErrorText.isHidden() is True


def test_bad_paper_add_button_reshown_after_any_clicking(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.addButton.isHidden() is False


def test_bad_paper_error_formatting_of_textedit_reset_after_editing_text(
    qtbot, db_empty
):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "nonsens")
    assert widget.searchBar.property("error") is False


def test_bad_paper_error_message_of_textedit_reset_after_editing_text(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "nonsens")
    assert widget.searchBarErrorText.isHidden() is True


def test_bad_paper_add_button_reshown_after_editing_text(qtbot, db_empty):
    widget = MainWindow(db_empty)
    assert len(widget.papersList.papers) == 0
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, "nonsense")
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "nonsens")
    assert widget.addButton.isHidden() is False


def test_adding_paper_does_not_clear_search_bar_if_already_in_library(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.text() == u.mine.bibcode


def test_adding_duplicate_paper_shows_error_formatting_of_textedit(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.property("error") is True


def test_adding_duplicate_paper_shows_error_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBarErrorText.isHidden() is False
    assert widget.searchBarErrorText.text() == "This paper is already in the library."


def test_adding_duplicate_paper_hides_add_button(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.addButton.isHidden() is True


def test_duplicate_error_formatting_of_textedit_reset_after_any_clicking(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBar.property("error") is False


def test_duplicate_error_message_of_textedit_reset_after_any_clicking(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBarErrorText.isHidden() is True


def test_duplicate_add_button_reshown_after_any_clicking(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.addButton.isHidden() is False


def test_duplicate_error_formatting_of_textedit_reset_after_editing_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "s")
    assert widget.searchBar.property("error") is False


def test_duplicate_error_message_of_textedit_reset_after_editing_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "s")
    assert widget.searchBarErrorText.isHidden() is True


def test_duplicate_add_button_reshown_after_editing_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.mine.bibcode)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "s")
    assert widget.addButton.isHidden() is False


def test_adding_paper_does_not_clear_search_bar_if_no_ads_key_set(
    qtbot, db_empty_change_ads_key
):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    # need to use a paper that's not already stored in my ADS cache
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.text() == u.used_for_no_ads_key.url


def test_adding_paper_no_ads_key_set_shows_error_formatting_of_textedit(
    qtbot, db_empty_change_ads_key
):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBar.property("error") is True


def test_adding_paper_no_ads_key_set_shows_error_text(qtbot, db_empty_change_ads_key):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.searchBarErrorText.isHidden() is False
    assert (
        widget.searchBarErrorText.text() == "You don't have an ADS key set. "
        "See this repository readme for more, then restart this application."
    )


def test_adding_paper_no_ads_key_hides_add_button(qtbot, db_empty_change_ads_key):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    assert widget.addButton.isHidden() is True


def test_no_ads_key_set_error_formatting_of_textedit_reset_after_any_clicking(
    qtbot, db_empty_change_ads_key
):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBar.property("error") is False


def test_no_ads_key_set_error_message_of_textedit_reset_after_any_clicking(
    qtbot, db_empty_change_ads_key
):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.searchBarErrorText.isHidden() is True


def test_no_ads_key_add_button_reshown_after_any_clicking(
    qtbot, db_empty_change_ads_key
):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    widget.searchBar.setCursorPosition(0)
    assert widget.addButton.isHidden() is False


def test_no_ads_key_set_error_formatting_of_textedit_reset_after_editing_text(
    qtbot, db_empty_change_ads_key
):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "s")
    assert widget.searchBar.property("error") is False


def test_no_ads_key_set_error_message_of_textedit_reset_after_editing_text(
    qtbot, db_empty_change_ads_key
):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "s")
    assert widget.searchBarErrorText.isHidden() is True


def test_no_ads_key_add_button_reshown_after_editing_text(
    qtbot, db_empty_change_ads_key
):
    widget = MainWindow(db_empty_change_ads_key)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.used_for_no_ads_key.url)
    qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    qtbot.keyClicks(widget.searchBar, "s")
    assert widget.addButton.isHidden() is False


def test_paper_cannot_be_added_twice(qtbot, db_empty):
    widget = MainWindow(db_empty)
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
    new_paper = Paper(u.mine.bibcode, db, widget.rightPanel, widget.papersList)
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


def test_clicking_on_paper_highlights_it_in_center_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    assert paper.property("is_highlighted") is True


def test_clicking_on_paper_highlights_its_text_it_in_center_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    assert paper.titleText.property("is_highlighted") is True
    assert paper.citeText.property("is_highlighted") is True


def test_all_papers_are_unhilighted_to_start(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    for paper in widget.papersList.papers:
        assert paper.property("is_highlighted") is False


def test_all_papers_text_are_unhilighted_to_start(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    for paper in widget.papersList.papers:
        assert paper.titleText.property("is_highlighted") is False
        assert paper.citeText.property("is_highlighted") is False


def test_papers_are_unhighlighted_when_others_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert len(widget.papersList.papers) > 1
    for paper_click in widget.papersList.papers:
        qtbot.mouseClick(paper_click, Qt.LeftButton)
        for paper_test in widget.papersList.papers:
            if paper_test.titleText == paper_click.titleText:
                assert paper_test.property("is_highlighted") is True
            else:
                assert paper_test.property("is_highlighted") is False


def test_paper_texts_are_unhighlighted_when_others_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert len(widget.papersList.papers) > 1
    for paper_click in widget.papersList.papers:
        qtbot.mouseClick(paper_click, Qt.LeftButton)
        for paper_test in widget.papersList.papers:
            if paper_test.titleText == paper_click.titleText:
                assert paper_test.titleText.property("is_highlighted") is True
                assert paper_test.citeText.property("is_highlighted") is True
            else:
                assert paper_test.titleText.property("is_highlighted") is False
                assert paper_test.citeText.property("is_highlighted") is False


def test_double_clicking_on_paper_without_local_file_asks_user(
    qtbot, db_empty, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input
    test_loc = "/Users/gillenb/test.pdf"
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return test_loc, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "local_file") == test_loc


def test_double_clicking_on_paper_without_local_file_but_not_choosing_doesnt_add_it(
    qtbot, db_empty, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return ("", "")

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "local_file") == None


def test_double_clicking_on_paper_with_local_file_opens_it(
    qtbot, db_empty, monkeypatch
):
    # Here we need to use monkeypatch to simulate opening the file
    test_loc = "/Users/gillenb/test.pdf"
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", test_loc)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    # since this already has a URL it should be added
    assert open_calls == [f"file:{test_loc}"]


def test_double_clicking_on_paper_without_local_file_selects_and_opens_it(
    qtbot, db_empty, monkeypatch
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

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)  # do not add file location
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert open_calls == [f"file:{test_loc}"]


def test_dclicking_on_paper_without_local_file_but_not_choosing_doesnt_add_or_open_it(
    qtbot, db_empty, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input and open files
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return ("", "")

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(db_empty)
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


def test_add_tag_button_is_shown_at_beginning(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.tagsList.addTagButton.isHidden() is False


def test_add_tag_text_button_has_correct_font_size(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.tagsList.addTagButton.font().pointSize() == 14


def test_add_tag_text_button_has_correct_font_family(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.tagsList.addTagButton.font().family() == "Cabin"


def test_add_tag_text_bar_is_hidden_at_beginning(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.tagsList.addTagBar.isHidden() is True


def test_clicking_add_tag_button_hides_button(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    assert widget.tagsList.addTagButton.isHidden() is True


def test_clicking_add_tag_button_shows_text_entry(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    assert widget.tagsList.addTagBar.isHidden() is False


def test_add_tag_text_bar_has_correct_font_size(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    assert widget.tagsList.addTagBar.font().pointSize() == 14


def test_add_tag_text_bar_has_correct_font_family(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    assert widget.tagsList.addTagBar.font().family() == "Cabin"


def test_add_tag_text_bar_has_correct_placeholder_text(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    text = "Tag name"
    assert widget.tagsList.addTagBar.placeholderText() == text


def test_can_add_tag_by_filling_tag_name_then_pressing_enter(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    assert db_temp.paper_has_tag(u.mine.bibcode, "Test Tag") is False


def test_can_add_tag_to_list_by_filling_tag_name_then_pressing_enter(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    tag_names = [t.name for t in widget.tagsList.tags]
    assert "Test Tag" in tag_names


def test_tag_name_entry_is_cleared_after_successful_entry(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    # this has been tested to work
    assert widget.tagsList.addTagBar.text() == ""


def test_tag_name_entry_is_hidden_after_successful_entry(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    assert widget.tagsList.addTagBar.isHidden() is True


def test_tag_name_button_is_shown_after_successful_entry(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    assert widget.tagsList.addTagButton.isHidden() is False


def test_tag_name_entry_is_not_cleared_after_duplicate_tag_attempt(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
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


def test_read_and_unread_are_initialized_even_in_new_database(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    tags_list = [t.name for t in widget.tagsList.tags]
    assert sorted(tags_list) == ["Read", "Unread"]


def test_read_and_unread_arent_added_to_nonempty_databased(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    tags_list = [t.name for t in widget.tagsList.tags]
    assert "Read" not in tags_list
    assert "Unread" not in tags_list


def test_tag_has_correct_name(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # get one of the tags, not sure which
    tag = widget.tagsList.tags[0]
    assert tag.label.text() == tag.name


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
    new_tag = LeftPanelTag("Test Tag", widget.papersList, widget.tagsList)
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


def test_checking_tag_in_checklist_adds_tag_to_interface(qtbot, db_temp):
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
    # click the done editing button
    qtbot.mouseClick(widget.rightPanel.doneEditingTagsButton, Qt.LeftButton)
    # Then check that these tags are listen in the interface
    assert widget.rightPanel.tagText.text() == "Tags: T1, T3, T4"


def test_unchecking_tag_in_checklist_removes_tag_from_interface(qtbot, db_temp):
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
    # click the done editing button
    qtbot.mouseClick(widget.rightPanel.doneEditingTagsButton, Qt.LeftButton)
    # Then check that these tags are not listed in the interface
    assert widget.rightPanel.tagText.text() == "Tags: T2, T5"


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
        if left_tag.label.text() in db.get_paper_tags(paper.bibcode):
            assert paper.isHidden() is False
        else:
            assert paper.isHidden() is True


def test_show_all_tags_button_starts_highlighted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.tagsList.showAllButton.property("is_highlighted") is True


def test_all_tags_start_unhighlighted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # get a tag from the left panel to click on
    for tag in widget.tagsList.tags:
        assert tag.property("is_highlighted") is False


def test_clicking_on_tag_in_left_panel_highlights_tag_text(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # get a tag from the left panel to click on
    tag = widget.tagsList.tags[0]
    qtbot.mouseClick(tag, Qt.LeftButton)
    assert tag.property("is_highlighted") is True


def test_clicking_on_show_all_in_left_panel_highlights_tag_text(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.showAllButton, Qt.LeftButton)
    assert widget.tagsList.showAllButton.property("is_highlighted") is True


def test_clicking_on_tag_in_left_panel_unlights_others(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # Click on one tag, then another
    for tag in widget.tagsList.tags:
        qtbot.mouseClick(tag, Qt.LeftButton)
        for tag_comp in widget.tagsList.tags:
            if tag.label.text() == tag_comp.label.text():
                assert tag_comp.property("is_highlighted") is True
            else:
                assert tag_comp.property("is_highlighted") is False


def test_clicking_on_show_all_in_left_panel_unlights_others(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.showAllButton, Qt.LeftButton)
    for tag in widget.tagsList.tags:
        assert tag.property("is_highlighted") is False


def test_newly_added_tag_is_unhighlighted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "newly added tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    for tag in widget.tagsList.tags:
        if tag.label.text() == "newly added tag":
            assert tag.property("is_highlighted") is False


def test_show_all_button_fontsize(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.tagsList.showAllButton.font().pointSize() == 14


def test_show_all_button_has_correct_font_family(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.tagsList.showAllButton.font().family() == "Cabin"


def test_show_all_button_has_correct_text(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.tagsList.showAllButton.label.text() == "All Papers"


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


def test_second_delete_cancel_paper_button_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is True


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


def test_second_delete_paper_cancel_button_does_not_appear_when_paper_clicked(
    qtbot, db
):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is True


def test_second_delete_paper_button_appears_when_first_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is False


def test_second_delete_paper_cancel_button_appears_when_first_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is False


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


def test_second_delete_cancel_buttons_reset_when_on_new_paper(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is True


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


def test_second_delete_paper_cancel_button_does_not_delete_paper_from_database(
    qtbot, db_temp
):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperCancelButton, Qt.LeftButton)
    # check that it's still in the database
    assert db_temp.get_paper_attribute(paper.bibcode, "title") == paper.titleText.text()


def test_second_delete_paper_cancel_button_does_not_delete_paper_from_interface(
    qtbot, db_temp
):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    bibcode = widget.papersList.papers[0].bibcode
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperCancelButton, Qt.LeftButton)
    # check that it's still in the center list
    found = False
    for paper in widget.papersList.papers:
        if bibcode == paper.bibcode:
            found = True
    assert found


def test_second_delete_paper_cancel_button_resets_delete_buttons(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperCancelButton, Qt.LeftButton)
    assert widget.rightPanel.firstDeletePaperButton.isHidden() is False
    assert widget.rightPanel.secondDeletePaperButton.isHidden() is True
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden() is True


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


def test_right_panel_open_ads_button_is_hidden_when_paper_is_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.adsButton.isHidden()


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


def test_right_panel_second_delete_cancel_button_is_hidden_when_paper_is_deleted(
    qtbot, db_temp
):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.secondDeletePaperCancelButton.isHidden()


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


def test_first_delete_tag_button_shown_at_beginning(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.firstDeleteTagButton.isHidden() is False


def test_first_delete_tag_button_has_correct_font_size(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.firstDeleteTagButton.font().pointSize() == 14


def test_first_delete_tag_button_has_correct_font_family(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    assert widget.firstDeleteTagButton.font().family() == "Cabin"


def test_first_delete_tag_button_has_correct_text(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.firstDeleteTagButton.text() == "Delete a tag"


def test_second_delete_tag_entry_hidden_at_beginning(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_clicking_first_tag_delete_button_shows_second_entry(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.isHidden() is False


def test_clicking_first_tag_delete_button_hides_first_button(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    assert widget.firstDeleteTagButton.isHidden() is True


def test_second_delete_tag_button_has_correct_font_size(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.font().pointSize() == 14


def test_second_delete_tag_button_has_correct_font_family(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.font().family() == "Cabin"


def test_second_delete_tag_entry_has_placeholder_text(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    text = "Tag to delete"
    assert widget.secondDeleteTagEntry.placeholderText() == text


def test_third_delete_tag_entry_hidden_at_beginning(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.thirdDeleteTagButton.isHidden() is True


def test_third_cancel_tag_entry_hidden_at_beginning(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.thirdDeleteTagCancelButton.isHidden() is True


def test_second_delete_tag_entry_is_hidden_when_entry_done(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_appears_when_first_entry_done(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagButton.isHidden() is False


def test_third_delete_tag_cancel_button_appears_when_first_entry_done(
    qtbot, db_temp_tags
):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagCancelButton.isHidden() is False


def test_third_delete_tag_button_has_correct_font_size(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagButton.font().pointSize() == 14


def test_third_delete_tag_button_has_correct_font_family(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagButton.font().family() == "Cabin"


def test_third_delete_tag_cancel_button_has_correct_font_size(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagCancelButton.font().pointSize() == 14


def test_third_delete_tag_cancel_button_has_correct_font_family(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagCancelButton.font().family() == "Cabin"


def test_third_delete_tag_button_text_is_accurate(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert (
        widget.thirdDeleteTagButton.text() == 'Click to confirm deletion of tag "tag_1"'
    )


def test_third_delete_tag_cancel_button_text_is_accurate(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert (
        widget.thirdDeleteTagCancelButton.text()
        == "Oops, don't delete tag " + '"tag_1"'
    )


def test_third_delete_tag_button_deletes_tag_from_db_when_pressed(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    original_tags = db_temp_tags.get_all_tags()
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    # check that it's not in the database anymore
    new_tags = db_temp_tags.get_all_tags()
    assert "tag_1" not in new_tags
    assert len(new_tags) == len(original_tags) - 1


def test_third_delete_tag_button_deletes_tag_from_list_when_pressed(
    qtbot, db_temp_tags
):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original number of tags
    num_original_tags = len([t.name for t in widget.tagsList.tags])
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    # Then see what tags are in the list now
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(new_tags) == num_original_tags - 1
    assert not "tag_1" in new_tags


def test_first_delete_tag_button_comes_back_once_tag_deleted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    assert widget.firstDeleteTagButton.isHidden() is False


def test_second_delete_tag_entry_hidden_once_tag_deleted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_hides_once_tag_deleted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    assert widget.thirdDeleteTagButton.isHidden() is True


def test_third_delete_tag_cancel_button_hides_once_tag_deleted(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    assert widget.thirdDeleteTagCancelButton.isHidden() is True


def test_first_delete_tag_button_comes_back_once_cancelled(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    assert widget.firstDeleteTagButton.isHidden() is False


def test_second_delete_tag_entry_hidden_once_cancelled(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_hides_once_cancelled(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    assert widget.thirdDeleteTagButton.isHidden() is True


def test_third_delete_tag_cancel_button_hides_once_cancelled(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    assert widget.thirdDeleteTagCancelButton.isHidden() is True


def test_cancel_tag_delete_doesnt_delete_any_tags_db(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original tags
    original_tags = db_temp_tags.get_all_tags()
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    new_tags = db_temp_tags.get_all_tags()
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_cancel_tag_delete_doesnt_delete_any_tags_interface(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    # first get the original tags
    original_tags = [t.name for t in widget.tagsList.tags]
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_invalid_tag_delete_entry_hides_entry(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_invalid_tag_delete_entry_shows_first_button(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.firstDeleteTagButton.isHidden() is False


def test_invalid_tag_delete_entry_resets_entry(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagEntry.text() == ""


def test_invalid_tag_delete_entry_keeps_third_hidden(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagButton.isHidden() is True


def test_invalid_tag_delete_entry_keeps_third_cancel_hidden(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagCancelButton.isHidden() is True


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


def test_open_ads_button_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.adsButton.isHidden() is True


def test_open_ads_button_appears_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.adsButton.isHidden() is False


def test_clicking_on_ads_button_opens_paper_in_browser(qtbot, db_empty, monkeypatch):
    # Here we need to use monkeypatch to simulate opening the URL
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)
    # click on th epaper in the main panel, then click on the ADS button
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.adsButton, Qt.LeftButton)

    # since this already has a URL it should be added
    assert open_calls == [
        f"https://ui.adsabs.harvard.edu/abs/2018ApJ...864...94B/abstract"
    ]


def test_show_all_export_button_has_correct_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.tagsList.showAllButton.exportButton.text() == "Export"


def test_tag_export_button_has_correct_text(qtbot, db_temp_tags):
    widget = MainWindow(db_temp_tags)
    qtbot.addWidget(widget)
    assert widget.tagsList.tags[0].exportButton.text() == "Export"


def test_clicking_export_all_exports_all(qtbot, db, monkeypatch):
    # Here we need to use monkeypatch to simulate user input
    test_loc = Path(__file__).parent / "test.txt"

    # create a mock function to get the file. It needs to have a couple of kwargs,
    # since those are used in the actual call. The filter is actually returned
    def mock_get_file(filter="", caption="", dir=""):
        return test_loc, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # click on the export all button
    qtbot.mouseClick(widget.tagsList.showAllButton.exportButton, Qt.LeftButton)
    # then open the file and compare it
    with open(test_loc, "r") as out_file:
        file_contents = out_file.read()
    # remove the file now before the test, so it always gets deleted
    test_loc.unlink()
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

    # Here we need to use monkeypatch to simulate user input
    test_loc = Path(__file__).parent / "test.txt"

    # create a mock function to get the file. It needs to have a couple of kwargs,
    # since those are used in the actual call. The filter is actually returned
    def mock_get_file(filter="", caption="", dir=""):
        return test_loc, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # find the tag to click on, then click it's export button
    for tag in widget.tagsList.tags:
        if tag.name == "test_tag":
            break

    qtbot.mouseClick(tag.exportButton, Qt.LeftButton)
    # then open the file and compare it
    with open(test_loc, "r") as out_file:
        file_contents = out_file.read()
    # remove the file now before the test, so it always gets deleted
    test_loc.unlink()
    # then compare the contents to what we expect
    expected_file_contents = "\n".join([p.bibtex for p in tagged_papers]) + "\n"
    assert file_contents == expected_file_contents


def test_no_export_happens_if_user_cancels(qtbot, db, monkeypatch):
    # create a mock function to get the file. It needs to have a couple of kwargs,
    # since those are used in the actual call. The filter is actually returned. Since
    # we're simulating no user interaction, return the emtpy string
    def mock_get_file(filter="", caption="", dir=""):
        return "", ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    # Also set up a monkeypatch for the export, so that we can see if anything
    # happened
    export_calls = []
    monkeypatch.setattr(db, "export", lambda x, y: export_calls.append(1))

    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # find the tag to click on, then click it's export button
    qtbot.mouseClick(widget.tagsList.showAllButton.exportButton, Qt.LeftButton)
    # then see if anything has happened. I did test my test by using an actual file for
    # the file dialog monkeypatch, and did get 1 export_call
    assert len(export_calls) == 0
