"""
test_interface.py

Perform tests on the GUI using pytest-qt
"""
import os
from pathlib import Path
import random
import shutil

import pytest
import pytestqt
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QDesktopServices, QGuiApplication
from PySide6.QtWidgets import QApplication, QFileDialog, QLineEdit

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


def test_right_panel_pdf_text_has_word_wrap_on(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.pdfText.wordWrap()


def test_right_panel_cite_key_has_word_wrap_on(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.citeKeyText.wordWrap()


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
    assert paper.titleText.font().pointSize() == 18


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


def test_paper_title_has_word_wrap_on(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    for paper in widget.papersList.papers:
        assert paper.titleText.wordWrap()


def test_paper_cite_string_has_word_wrap_on(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    for paper in widget.papersList.papers:
        assert paper.citeText.wordWrap()


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


def test_clicking_on_paper_puts_tags_in_right_panel(qtbot, db_no_tags):
    widget = MainWindow(db_no_tags)
    qtbot.addWidget(widget)
    # Add some tags to the database - this is tested below
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        qtbot.keyClicks(widget.tagsList.addTagBar, tag)
        qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)

    # get one of the papers, not sure which
    paper = widget.papersList.papers[0]
    # add one of the tags to this paper - this is done through the database, not the
    # actual adding tags functionality - that will be tested below
    db_no_tags.tag_paper(paper.bibcode, "T1")
    db_no_tags.tag_paper(paper.bibcode, "T3")
    db_no_tags.tag_paper(paper.bibcode, "T5")
    # then click on the paper
    qtbot.mouseClick(paper, Qt.LeftButton)
    assert widget.rightPanel.tagText.text() == "Tags: T1, T3, T5"


def test_clicking_on_paper_with_no_tags_puts_default_in_right_panel(qtbot, db_no_tags):
    widget = MainWindow(db_no_tags)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.tagText.text() == "Tags: None"


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


def test_clicking_on_paper_scroll_is_at_top(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.verticalScrollBar().value() == 0
    assert widget.rightPanel.horizontalScrollBar().value() == 0


def test_clicking_on_paper_scroll_is_at_top_even_after_scrolling_down(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    widget.rightPanel.verticalScrollBar().setValue(100)
    assert widget.rightPanel.verticalScrollBar().value() == 100
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    assert widget.rightPanel.verticalScrollBar().value() == 0


def test_clicking_on_same_paper_doesnt_adjust_scroll_position(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    widget.rightPanel.verticalScrollBar().setValue(100)
    assert widget.rightPanel.verticalScrollBar().value() == 100
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.verticalScrollBar().value() == 100


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


def test_paper_pdf_buttons_are_hidden_at_start(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.pdfText.isHidden() is True
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True


def test_paper_pdf_buttons_show_when_paper_clicked_with_local_file(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is False
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True


def test_paper_pdf_buttons_show_when_paper_clicked_without_local_file(qtbot, db_temp):
    # no local files are set in the temp database
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_buttons_show_when_paper_clicked_with_nonexistent_local_file(
    qtbot, db_empty
):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "nonexistent_file.pdf")
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_buttons_update_database_if_file_doesnt_exist(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "nonexistent_file.pdf")
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "local_file") is None


def test_paper_pdf_buttons_have_correct_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    assert widget.rightPanel.pdfOpenButton.text() == "Open this paper's PDF"
    assert widget.rightPanel.pdfChooseLocalFileButton.text() == "Choose a local PDF"
    assert widget.rightPanel.pdfDownloadButton.text() == "Download the PDF"


def test_paper_pdf_text_has_correct_text_with_local_file(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfText.text() == f"PDF Location: {__file__}"


def test_paper_pdf_text_has_correct_text_without_local_file(qtbot, db_temp):
    # no local files are set in the temp database
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfText.text() == "No PDF location set"


def test_paper_pdf_text_has_correct_text_with_nonexistent_local_file(qtbot, db_empty):
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "nonexistent_file.pdf")
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfText.text() == "No PDF location set"


def test_paper_pdf_add_local_file_button_asks_user(qtbot, db_temp, monkeypatch):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    get_file_calls = []

    def mock_get_file(filter="", dir=""):
        get_file_calls.append(1)
        return __file__, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)
    assert get_file_calls == [1]


def test_paper_pdf_add_local_file_button_doesnt_add_if_cancelled(
    qtbot, db_temp, monkeypatch
):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call. We return nothing, as that's the default
    # value if the user cancels the file chooser in the actual use
    def mock_get_file(filter="", dir=""):
        return "", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)
    assert (
        db_temp.get_paper_attribute(widget.papersList.papers[0].bibcode, "local_file")
        is None
    )


def test_paper_pdf_add_local_file_button_doesnt_add_if_doesnt_exist(
    qtbot, db_temp, monkeypatch
):
    # I don't think this should happen in real usage, but validate
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call. We return nothing, as that's the default
    # value if the user cancels the file chooser in the actual use
    def mock_get_file(filter="", dir=""):
        return "nonexistent_file.pdf", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)
    assert (
        db_temp.get_paper_attribute(widget.papersList.papers[0].bibcode, "local_file")
        is None
    )


def test_paper_pdf_add_local_file_button_adds_it_to_database(
    qtbot, db_temp, monkeypatch
):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", dir=""):
        return __file__, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)
    assert (
        db_temp.get_paper_attribute(widget.papersList.papers[0].bibcode, "local_file")
        == __file__
    )


def test_paper_pdf_add_local_file_button_updates_text(qtbot, db_temp, monkeypatch):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", dir=""):
        return __file__, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)
    assert widget.rightPanel.pdfText.text() == f"PDF Location: {__file__}"


def test_paper_pdf_add_local_file_button_cancel_doesnt_update_text(
    qtbot, db_temp, monkeypatch
):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", dir=""):
        return "", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)
    assert widget.rightPanel.pdfText.text() == f"No PDF location set"


def test_paper_pdf_add_local_file_nonexistent_file_doesnt_update_text(
    qtbot, db_temp, monkeypatch
):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", dir=""):
        return "nonexistent_file.pdf", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)
    assert widget.rightPanel.pdfText.text() == f"No PDF location set"


def test_paper_pdf_add_local_file_button_resets_buttons_if_successful(
    qtbot, db_temp, monkeypatch
):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", dir=""):
        return __file__, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)

    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is False
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True


def test_paper_pdf_add_local_file_button_doest_change_buttons_cancel(
    qtbot, db_temp, monkeypatch
):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", dir=""):
        return "", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)

    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_add_local_file_button_doest_change_buttons_nonexistent(
    qtbot, db_temp, monkeypatch
):
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", dir=""):
        return "nonexistent_file.pdf", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)

    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_open_pdf_button_opens_pdf(qtbot, db_empty, monkeypatch):
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", __file__)
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfOpenButton, Qt.LeftButton)
    assert open_calls == [f"file:{__file__}"]


def test_paper_pdf_open_bad_pdf_doesnt_open(qtbot, db_empty, monkeypatch):
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    shutil.copy2(__file__, "example.py")
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "example.py")

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    Path("example.py").unlink()
    qtbot.mouseClick(widget.rightPanel.pdfOpenButton, Qt.LeftButton)
    assert open_calls == []


def test_paper_pdf_open_bad_pdf_resets_buttons(qtbot, db_empty, monkeypatch):
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    shutil.copy2(__file__, "example.py")
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "example.py")

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    Path("example.py").unlink()
    qtbot.mouseClick(widget.rightPanel.pdfOpenButton, Qt.LeftButton)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_paper_pdf_open_bad_pdf_resets_database(qtbot, db_empty, monkeypatch):
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
    # fill a local file into the database
    db_empty.add_paper(u.mine.bibcode)
    shutil.copy2(__file__, "example.py")
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "example.py")

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    Path("example.py").unlink()
    qtbot.mouseClick(widget.rightPanel.pdfOpenButton, Qt.LeftButton)
    assert db_empty.get_paper_attribute(u.mine.bibcode, "local_file") is None


def test_paper_pdf_buttons_hidden_when_paper_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)

    assert widget.rightPanel.pdfText.isHidden() is True
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True


def test_download_pdf_button_asks_user(qtbot, db_temp, monkeypatch):
    # Here we need to use monkeypatch to simulate user selecting a file location
    test_loc = str(Path(__file__).parent / "test.pdf")
    get_file_calls = []
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        get_file_calls.append(1)
        return test_loc, "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert get_file_calls == [1]
    assert download_links == [
        "https://ui.adsabs.harvard.edu/link_gateway/2004ApJ...613..898T/EPRINT_PDF"
    ] or download_links == [
        "https://ui.adsabs.harvard.edu/link_gateway/2004ApJ...613..898T/PUB_PDF"
    ]


def test_download_pdf_button_actually_downloads_paper(qtbot, db_temp, monkeypatch):
    # Here we need to use monkeypatch to simulate user selecting a file location
    test_loc = Path(__file__).parent / "test.pdf"

    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        return str(test_loc), "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert test_loc.is_file()
    assert test_loc.stat().st_size > 1e6  # 1 Mb, in bytes
    test_loc.unlink()  # remove the file we just downloaded


def test_download_pdf_button_can_be_cancelled(qtbot, db_temp, monkeypatch):
    # Here we need to use monkeypatch to simulate user selecting a file location
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        return "", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )

    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert download_links == []


def test_download_pdf_button_updates_database(qtbot, db_temp, monkeypatch):
    # Here we need to use monkeypatch to simulate user selecting a file location
    test_loc = Path(__file__).parent / "test.pdf"

    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        return str(test_loc), "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)

    # I cannot monkeypatch the downloading, since the code checks if the PDF exists
    # when setting the buttons
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert db_temp.get_paper_attribute(
        widget.papersList.papers[0].bibcode, "local_file"
    ) == str(test_loc)
    test_loc.unlink()


def test_download_pdf_button_doesnt_update_database_if_cancelled(
    qtbot, db_temp, monkeypatch
):
    # Here we need to use monkeypatch to simulate user selecting a file location
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        return "", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert (
        db_temp.get_paper_attribute(widget.papersList.papers[0].bibcode, "local_file")
        == None
    )


def test_download_pdf_button_updates_buttons(qtbot, db_temp, monkeypatch):
    # Here we need to use monkeypatch to simulate user selecting a file location
    test_loc = Path(__file__).parent / "test.pdf"

    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        return str(test_loc), "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)

    # I cannot monkeypatch the downloading, since the code checks if the PDF exists
    # when setting the buttons
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is False
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is True
    assert widget.rightPanel.pdfDownloadButton.isHidden() is True
    test_loc.unlink()


def test_download_pdf_button_doesnt_update_buttons_if_cancelled(
    qtbot, db_temp, monkeypatch
):
    # Here we need to use monkeypatch to simulate user selecting a file location
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        return "", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert widget.rightPanel.pdfText.isHidden() is False
    assert widget.rightPanel.pdfOpenButton.isHidden() is True
    assert widget.rightPanel.pdfChooseLocalFileButton.isHidden() is False
    assert widget.rightPanel.pdfDownloadButton.isHidden() is False


def test_download_pdf_button_updates_text(qtbot, db_temp, monkeypatch):
    # Here we need to use monkeypatch to simulate user selecting a file location
    test_loc = Path(__file__).parent / "test.pdf"

    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        return str(test_loc), "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)

    # I cannot monkeypatch the downloading, since the code checks if the PDF exists
    # when setting the buttons
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert widget.rightPanel.pdfText.text() == f"PDF Location: {str(test_loc)}"
    test_loc.unlink()


def test_download_pdf_button_doesnt_reset_text_if_cancelled(
    qtbot, db_temp, monkeypatch
):
    # Here we need to use monkeypatch to simulate user selecting a file location
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter="", caption="", dir=""):
        return "", "dummy filter"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_file)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert widget.rightPanel.pdfText.text() == "No PDF location set"


def test_download_pdf_doesnt_ask_user_if_none_available(qtbot, db_empty, monkeypatch):
    # add BBFH to the database, since it has no PDF
    db_empty.add_paper(u.bbfh.bibcode)
    # Here we need to use monkeypatch to simulate user selecting a file location
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    test_loc = Path(__file__).parent / "test.pdf"
    get_file_calls = []

    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda x, y, z: get_file_calls.append(1)
    )

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert get_file_calls == []


def test_download_pdf_doesnt_download_if_none_available(qtbot, db_empty, monkeypatch):
    # add BBFH to the database, since it has no PDF
    db_empty.add_paper(u.bbfh.bibcode)
    # Here we need to use monkeypatch to simulate user selecting a file location
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    test_loc = Path(__file__).parent / "test.pdf"
    get_file_calls = []

    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda x, y, z: get_file_calls.append(1)
    )

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert download_links == []


def test_download_pdf_button_shows_error_message_if_none_available(
    qtbot, db_empty, monkeypatch
):
    # add BBFH to the database, since it has no PDF
    db_empty.add_paper(u.bbfh.bibcode)
    # Here we need to use monkeypatch to simulate user selecting a file location
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    test_loc = Path(__file__).parent / "test.pdf"
    get_file_calls = []

    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda x, y, z: get_file_calls.append(1)
    )

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert widget.rightPanel.pdfDownloadButton.text() == "Automatic Download Failed"


def test_download_pdf_button_error_message_resets_on_new_paper_clicked(
    qtbot, db_empty, monkeypatch
):
    # add BBFH to the database, since it has no PDF
    db_empty.add_paper(u.bbfh.bibcode)
    db_empty.add_paper(u.tremonti.bibcode)
    # Here we need to use monkeypatch to simulate user selecting a file location
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    test_loc = Path(__file__).parent / "test.pdf"
    get_file_calls = []

    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", lambda x, y, z: get_file_calls.append(1)
    )

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)

    # monkeypatch the downloading
    download_links = []
    monkeypatch.setattr(
        widget.rightPanel, "_downloadURL", lambda x, y: download_links.append(x)
    )
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert widget.rightPanel.pdfDownloadButton.text() == "Automatic Download Failed"
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    assert widget.rightPanel.pdfDownloadButton.text() == "Download the PDF"


def test_double_clicking_on_paper_with_local_file_opens_it(
    qtbot, db_empty, monkeypatch
):
    # Here we need to use monkeypatch to simulate opening the file
    test_loc = __file__
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


def test_dclicking_on_paper_with_no_local_file_doesnt_ask_user(
    qtbot, db_temp, monkeypatch
):
    # Here we need to use monkeypatch to simulate opening the file and asking user
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))
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

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert user_asks == []


def test_dclicking_on_paper_with_no_local_file_doesnt_open(qtbot, db_temp, monkeypatch):
    # Here we need to use monkeypatch to simulate opening the file
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert open_calls == []


def test_dclicking_on_paper_with_no_local_file_highlights_right_panel(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True


def test_dclicking_on_paper_with_no_local_file_scrolls_to_show_buttons(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    # I don't know exactly where this should end up, but not at the top or bottom
    assert (
        0
        < widget.rightPanel.verticalScrollBar().value()
        < widget.rightPanel.verticalScrollBar().maximum()
    )
    assert widget.rightPanel.horizontalScrollBar().value() == 0


def test_pdf_highlighting_goes_away_with_any_click(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True
    qtbot.mouseClick(widget.rightPanel.titleText, Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == False
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == False


def test_pdf_highlighting_goes_away_with_choose_local_interaction(
    qtbot, db_temp, monkeypatch
):
    # mock the selection interaction
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda filter, dir: ("", ""))

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True
    qtbot.mouseClick(widget.rightPanel.pdfChooseLocalFileButton, Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == False
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == False


def test_pdf_highlighting_goes_away_with_download_interaction(
    qtbot, db_temp, monkeypatch
):
    # mock the selection interaction
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda dir, caption: ("", ""))

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True
    qtbot.mouseClick(widget.rightPanel.pdfDownloadButton, Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == False
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == False


def test_pdf_highlighting_goes_away_when_new_paper_clicked(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == False
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == False


def test_dclicking_on_paper_with_nonexistent_file_redirects_to_right_panel(
    qtbot, db_empty, monkeypatch
):
    # first, add a file to the database, then set the file to something nonsense. We'll
    # then try to open it, and check that the interface asks the user.
    db_empty.add_paper(u.mine.bibcode)
    db_empty.set_paper_attribute(u.mine.bibcode, "local_file", "lskdlskdflskj")

    # when we try to open files, just list the ones we tried to open
    open_calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda x: open_calls.append(x))

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    # check that we didn't open anything
    assert open_calls == []
    # check that the right panel is highlighted
    assert widget.rightPanel.pdfChooseLocalFileButton.property("pdf_highlight") == True
    assert widget.rightPanel.pdfDownloadButton.property("pdf_highlight") == True


def test_dclicking_on_paper_shows_details_in_right_panel(qtbot, db_empty, monkeypatch):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add a paper to this empty database to make the paper object
    add_my_paper(qtbot, widget)  # do not add file location
    qtbot.mouseDClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.titleText.text() == u.mine.title


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


def test_clicking_add_tag_button_puts_focus_on_text_entry(qtbot, db_empty, monkeypatch):
    # I tried to test this directly, but was having trouble getting the tests to work
    # properly. Specifically, widget.hasFocus() was not working propertly in tests for
    # whatever reasonSo instead, I'll monkeypatch the setFocus method. I have tested
    # that this works in the actual interface
    setFocus_calls = []
    monkeypatch.setattr(QLineEdit, "setFocus", lambda x: setFocus_calls.append(True))

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    # assert widget.tagsList.addTagBar.hasFocus() is True  # would be the best test
    assert setFocus_calls == [True]


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


def test_tag_name_entry_is_not_cleared_after_duplicate_cap_tag_attempt(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Test Tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    # this has been tested to work and now be clear, so try it again
    qtbot.keyClicks(widget.tagsList.addTagBar, "test tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    assert widget.tagsList.addTagBar.text() == "test tag"


def test_tag_name_entry_is_not_cleared_after_whitespace_tag_attempt(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "   ")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    assert widget.tagsList.addTagBar.text() == "   "


def test_add_tag_entry_can_exit_with_escape_press_at_any_time(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "sdfsdf")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Escape)
    assert widget.tagsList.addTagBar.isHidden() is True
    assert widget.tagsList.addTagButton.isHidden() is False


def test_add_tag_entry_can_exit_with_escape_press_at_any_time_clears_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "sdfsdf")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Escape)
    assert widget.tagsList.addTagBar.text() == ""


def test_add_tag_entry_can_exit_with_backspace_when_empty(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "abc")
    # back out those three letters
    for _ in range(3):
        qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Backspace)
    # entry should still be visible
    assert widget.tagsList.addTagBar.isHidden() is False
    assert widget.tagsList.addTagButton.isHidden() is True
    # with one more backspace, we exit
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Backspace)
    assert widget.tagsList.addTagBar.isHidden() is True
    assert widget.tagsList.addTagButton.isHidden() is False


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


def test_read_and_unread_arent_added_to_nonempty_database(qtbot, db_no_tags):
    db_no_tags.add_new_tag("lskdjlkj")
    db_no_tags.add_new_tag("ghjghjg")
    widget = MainWindow(db_no_tags)
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


def test_checking_tag_in_checklist_adds_tag_to_paper_in_database(qtbot, db_no_tags):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_no_tags.add_new_tag(tag)
    widget = MainWindow(db_no_tags)
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
    for tag in db_no_tags.get_all_tags():
        if tag in to_check:
            assert db_no_tags.paper_has_tag(paper.bibcode, tag) is True
        else:
            assert db_no_tags.paper_has_tag(paper.bibcode, tag) is False


def test_unchecking_tag_in_checklist_removes_tag_from_paper_in_database(
    qtbot, db_no_tags
):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_no_tags.add_new_tag(tag)
    widget = MainWindow(db_no_tags)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.papers[0]
    # add all tags to this paper
    for tag in db_no_tags.get_all_tags():
        db_no_tags.tag_paper(paper.bibcode, tag)
    # click on the paper to show it in the right panel
    qtbot.mouseClick(paper, Qt.LeftButton)
    # click on the tags we want to remove
    to_uncheck = ["T1", "T3", "T4"]
    for tag_item in widget.rightPanel.tags:
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
    widget = MainWindow(db_no_tags)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    # first double check that no tags are selected (is already be tested for elsewhere)
    assert widget.rightPanel.tagText.text() == "Tags: None"
    # this will show the tags in the right panel. Click on a few
    to_check = ["T1", "T3", "T4"]
    for tag_item in widget.rightPanel.tags:
        if tag_item.text() in to_check:
            tag_item.setChecked(True)
    # click the done editing button
    qtbot.mouseClick(widget.rightPanel.doneEditingTagsButton, Qt.LeftButton)
    # Then check that these tags are listen in the interface
    assert widget.rightPanel.tagText.text() == "Tags: T1, T3, T4"


def test_unchecking_tag_in_checklist_removes_tag_from_interface(qtbot, db_no_tags):
    # add some tags to this database
    for tag in ["T1", "T2", "T3", "T4", "T5"]:
        db_no_tags.add_new_tag(tag)
    widget = MainWindow(db_no_tags)
    qtbot.addWidget(widget)
    # get one of the papers, not sure which, then click on it
    paper = widget.papersList.papers[0]
    # add all tags to this paper
    for tag in db_no_tags.get_all_tags():
        db_no_tags.tag_paper(paper.bibcode, tag)
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


def test_show_all_tags_button_starts_highlighted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    assert widget.tagsList.showAllButton.property("is_highlighted") is True
    assert widget.tagsList.showAllButton.label.property("is_highlighted") is True


def test_all_tags_start_unhighlighted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # get a tag from the left panel to click on
    for tag in widget.tagsList.tags:
        assert tag.property("is_highlighted") is False
        assert tag.label.property("is_highlighted") is False


def test_clicking_on_tag_in_left_panel_highlights_tag_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # get a tag from the left panel to click on
    tag = widget.tagsList.tags[0]
    qtbot.mouseClick(tag, Qt.LeftButton)
    assert tag.property("is_highlighted") is True
    assert tag.label.property("is_highlighted") is True


def test_clicking_on_show_all_in_left_panel_highlights_tag_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.showAllButton, Qt.LeftButton)
    assert widget.tagsList.showAllButton.property("is_highlighted") is True
    assert widget.tagsList.showAllButton.label.property("is_highlighted") is True


def test_clicking_on_tag_in_left_panel_unlights_others(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # Click on one tag, then another
    for tag in widget.tagsList.tags:
        qtbot.mouseClick(tag, Qt.LeftButton)
        for tag_comp in widget.tagsList.tags:
            if tag.label.text() == tag_comp.label.text():
                assert tag_comp.property("is_highlighted") is True
                assert tag_comp.label.property("is_highlighted") is True
            else:
                assert tag_comp.property("is_highlighted") is False
                assert tag_comp.label.property("is_highlighted") is False


def test_clicking_on_show_all_in_left_panel_unlights_others(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.showAllButton, Qt.LeftButton)
    for tag in widget.tagsList.tags:
        assert tag.property("is_highlighted") is False
        assert tag.label.property("is_highlighted") is False


def test_newly_added_tag_is_unhighlighted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "newly added tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    for tag in widget.tagsList.tags:
        if tag.label.text() == "newly added tag":
            assert tag.property("is_highlighted") is False
            assert tag.label.property("is_highlighted") is False


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


def test_first_delete_tag_button_shown_at_beginning(qtbot, db_temp):
    widget = MainWindow(db_temp)
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


def test_first_delete_tag_button_has_correct_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    assert widget.firstDeleteTagButton.text() == "Delete a tag"


def test_second_delete_tag_entry_hidden_at_beginning(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_clicking_first_tag_delete_button_shows_second_entry(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.isHidden() is False


def test_clicking_first_tag_delete_button_puts_focus_on_entry(
    qtbot, db_temp, monkeypatch
):
    # I tried to test this directly, but was having trouble getting the tests to work
    # properly. Specifically, widget.hasFocus() was not working propertly in tests for
    # whatever reasonSo instead, I'll monkeypatch the setFocus method. I have tested
    # that this works in the actual interface
    setFocus_calls = []
    monkeypatch.setattr(QLineEdit, "setFocus", lambda x: setFocus_calls.append(True))

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    # assert widget.secondDeleteTagEntry.hasFocus() is True  # would be the best test
    assert setFocus_calls == [True]


def test_clicking_first_tag_delete_button_hides_first_button(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    assert widget.firstDeleteTagButton.isHidden() is True


def test_second_delete_tag_button_has_correct_font_size(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.font().pointSize() == 14


def test_second_delete_tag_button_has_correct_font_family(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.font().family() == "Cabin"


def test_second_delete_tag_entry_has_placeholder_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    text = "Tag to delete"
    assert widget.secondDeleteTagEntry.placeholderText() == text


def test_third_delete_tag_entry_hidden_at_beginning(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    assert widget.thirdDeleteTagButton.isHidden() is True


def test_third_cancel_tag_entry_hidden_at_beginning(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    assert widget.thirdDeleteTagCancelButton.isHidden() is True


def test_second_delete_tag_entry_is_hidden_when_entry_done(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_appears_when_first_entry_done(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagButton.isHidden() is False


def test_third_delete_tag_cancel_button_appears_when_first_entry_done(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagCancelButton.isHidden() is False


def test_delete_tag_entry_can_exit_with_escape_press_at_any_time(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Escape)
    assert widget.secondDeleteTagEntry.isHidden() is True
    assert widget.firstDeleteTagButton.isHidden() is False


def test_delete_tag_entry_can_exit_with_escape_press_at_any_time_clears_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Escape)
    assert widget.secondDeleteTagEntry.text() == ""


def test_delete_tag_entry_can_exit_with_backspace_when_empty(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "abc")
    # back out those three letters
    for _ in range(3):
        qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Backspace)
    # entry should still be visible
    assert widget.secondDeleteTagEntry.isHidden() is False
    assert widget.firstDeleteTagButton.isHidden() is True
    # with one more backspace, we exit
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Backspace)
    assert widget.secondDeleteTagEntry.isHidden() is True
    assert widget.firstDeleteTagButton.isHidden() is False


def test_third_delete_tag_button_has_correct_font_size(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagButton.font().pointSize() == 14


def test_third_delete_tag_button_has_correct_font_family(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagButton.font().family() == "Cabin"


def test_third_delete_tag_cancel_button_has_correct_font_size(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagCancelButton.font().pointSize() == 14


def test_third_delete_tag_cancel_button_has_correct_font_family(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagCancelButton.font().family() == "Cabin"


def test_third_delete_tag_button_text_is_accurate(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert (
        widget.thirdDeleteTagButton.text() == 'Click to confirm deletion of tag "Read"'
    )


def test_third_delete_tag_cancel_button_text_is_accurate(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert (
        widget.thirdDeleteTagCancelButton.text() == "Oops, don't delete tag " + '"Read"'
    )


def test_third_delete_tag_button_deletes_tag_from_db_when_pressed(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    original_tags = db_temp.get_all_tags()
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    # check that it's not in the database anymore
    new_tags = db_temp.get_all_tags()
    assert "Read" not in new_tags
    assert len(new_tags) == len(original_tags) - 1


def test_third_delete_tag_button_deletes_tag_from_list_when_pressed(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # first get the original number of tags
    num_original_tags = len([t.name for t in widget.tagsList.tags])
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    # Then see what tags are in the list now
    new_tags = [t.name for t in widget.tagsList.tags]
    assert len(new_tags) == num_original_tags - 1
    assert not "Read" in new_tags


def test_first_delete_tag_button_comes_back_once_tag_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    assert widget.firstDeleteTagButton.isHidden() is False


def test_second_delete_tag_entry_hidden_once_tag_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_hides_once_tag_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    assert widget.thirdDeleteTagButton.isHidden() is True


def test_third_delete_tag_cancel_button_hides_once_tag_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Read")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    assert widget.thirdDeleteTagCancelButton.isHidden() is True


def test_first_delete_tag_button_comes_back_once_cancelled(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    assert widget.firstDeleteTagButton.isHidden() is False


def test_second_delete_tag_entry_hidden_once_cancelled(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_third_delete_tag_button_hides_once_cancelled(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    assert widget.thirdDeleteTagButton.isHidden() is True


def test_third_delete_tag_cancel_button_hides_once_cancelled(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    assert widget.thirdDeleteTagCancelButton.isHidden() is True


def test_cancel_tag_delete_doesnt_delete_any_tags_db(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # first get the original tags
    original_tags = db_temp.get_all_tags()
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "tag_1")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagCancelButton, Qt.LeftButton)
    new_tags = db_temp.get_all_tags()
    assert len(original_tags) == len(new_tags)
    assert original_tags == new_tags


def test_cancel_tag_delete_doesnt_delete_any_tags_interface(qtbot, db_temp):
    widget = MainWindow(db_temp)
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


def test_invalid_tag_delete_entry_hides_entry(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagEntry.isHidden() is True


def test_invalid_tag_delete_entry_shows_first_button(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.firstDeleteTagButton.isHidden() is False


def test_invalid_tag_delete_entry_resets_entry(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.secondDeleteTagEntry.text() == ""


def test_invalid_tag_delete_entry_keeps_third_hidden(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagButton.isHidden() is True


def test_invalid_tag_delete_entry_keeps_third_cancel_hidden(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "sdfsdfadbsdf")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    assert widget.thirdDeleteTagCancelButton.isHidden() is True


def test_tag_checkboxes_are_hidden_when_paper_clicked(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # click on a paper, then click the edit tags button
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    # click on a different paper
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    # the tag edit checkboxes should all be hidden
    for t in widget.rightPanel.tags:
        assert t.isHidden()


def test_done_editing_button_is_hidden_when_paper_clicked(qtbot, db_temp):
    widget = MainWindow(db_temp)
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


def test_adding_tags_doesnt_duplicate_tags_in_right_panel(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    widget = MainWindow(db_empty)
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


def test_tag_export_button_has_correct_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    assert widget.tagsList.tags[0].exportButton.text() == "Export"


def test_show_all_tags_button_starts_with_export_button(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    assert widget.tagsList.showAllButton.exportButton.isHidden() is False


def test_all_tags_start_with_export_hidden(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # get a tag from the left panel to click on
    for tag in widget.tagsList.tags:
        assert tag.exportButton.isHidden() is True


def test_clicking_on_tag_in_left_panel_shows_export_button(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # get a tag from the left panel to click on
    tag = widget.tagsList.tags[0]
    qtbot.mouseClick(tag, Qt.LeftButton)
    assert tag.exportButton.isHidden() is False


def test_clicking_on_show_all_in_left_panel_shows_export_button(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.tags[0], Qt.LeftButton)
    qtbot.mouseClick(widget.tagsList.showAllButton, Qt.LeftButton)
    assert widget.tagsList.showAllButton.exportButton.isHidden() is False


def test_clicking_on_tag_in_left_panel_removes_export_button(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # Click on one tag, then another
    for tag in widget.tagsList.tags:
        qtbot.mouseClick(tag, Qt.LeftButton)
        for tag_comp in widget.tagsList.tags:
            if tag.label.text() == tag_comp.label.text():
                assert tag_comp.exportButton.isHidden() is False
            else:
                assert tag_comp.exportButton.isHidden() is True


def test_clicking_on_show_all_in_left_panel_removes_other_exports(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.showAllButton, Qt.LeftButton)
    for tag in widget.tagsList.tags:
        assert tag.exportButton.isHidden() is True


def test_newly_added_tag_has_hidden_export(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "newly added tag")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    for tag in widget.tagsList.tags:
        if tag.label.text() == "newly added tag":
            assert tag.exportButton.isHidden() is True


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


def test_user_notes_fields_are_not_shown_on_initialization(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    assert widget.rightPanel.userNotesText.isHidden() is True
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is True
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_user_notes_are_appropriately_shown_once_paper_clicked(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.userNotesText.isHidden() is False
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is False
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_user_notes_has_correct_text(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.userNotesText.text() == "abc123"


def test_user_notes_has_correct_text_if_originally_blank(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.userNotesText.text() == "No notes yet"


def test_user_notes_has_word_wrap_on(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.userNotesText.wordWrap()


def test_edit_user_notes_button_has_correct_text(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.userNotesTextEditButton.text() == "Edit Notes"


def test_user_notes_finished_editing_button_has_correct_text(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert (
        widget.rightPanel.userNotesTextEditFinishedButton.text() == "Done Editing Notes"
    )


def test_notes_static_text_disappears_when_edit_button_clicked(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesText.isHidden() is True


def test_notes_edit_button_disappears_when_edit_button_clicked(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is True


def test_notes_finished_edit_button_appears_when_edit_button_clicked(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is False


def test_notes_edit_field_has_original_text(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesTextEditField.toPlainText() == "abc123"


def test_notes_edit_field_is_blank_if_there_are_no_notes(qtbot, db_empty):
    db_empty.add_paper(u.mine.bibcode)
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesTextEditField.toPlainText() == ""


def test_notes_edit_field_changes_database_when_finished(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    # simulate the user deleting the current into, then adding their own
    widget.rightPanel.userNotesTextEditField.clear()
    qtbot.keyClicks(widget.rightPanel.userNotesTextEditField, "987XYZ")
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditFinishedButton, Qt.LeftButton)
    assert db_notes.get_paper_attribute(u.mine.bibcode, "user_notes") == "987XYZ"


def test_notes_edit_field_changes_shown_text(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    # simulate the user deleting the current into, then adding their own
    widget.rightPanel.userNotesTextEditField.clear()
    qtbot.keyClicks(widget.rightPanel.userNotesTextEditField, "987XYZ")
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditFinishedButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesText.text() == "987XYZ"


def test_notes_user_enters_blank_doesnt_print_blank(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    # simulate the user deleting the current into, then adding their own
    widget.rightPanel.userNotesTextEditField.clear()
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditFinishedButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesText.text() == "No notes yet"


def test_notes_edit_finished_button_disappears_when_clicked(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.userNotesTextEditField, "987XYZ")
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditFinishedButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_notes_edit_field_disappears_when_editing_done(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.userNotesTextEditField, "987XYZ")
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditFinishedButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True


def test_notes_edit_button_reappears_when_editing_done(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.userNotesTextEditField, "987XYZ")
    qtbot.mouseClick(widget.rightPanel.userNotesTextEditFinishedButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is False


def test_user_notes_are_appropriately_shown_once_paper_deleted(qtbot, db_notes):
    widget = MainWindow(db_notes)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.userNotesText.isHidden() is True
    assert widget.rightPanel.userNotesTextEditButton.isHidden() is True
    assert widget.rightPanel.userNotesTextEditField.isHidden() is True
    assert widget.rightPanel.userNotesTextEditFinishedButton.isHidden() is True


def test_spacers_are_hidden_at_initialization(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    for spacer in widget.rightPanel.spacers:
        assert spacer.isHidden() is True


def test_spacers_are_shown_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    for spacer in widget.rightPanel.spacers:
        assert spacer.isHidden() is False


def test_spacers_are_hidden_once_paper_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    for spacer in widget.rightPanel.spacers:
        assert spacer.isHidden() is True


def test_left_panel_tags_are_sorted_alphabetically(qtbot, db_empty):
    # add tags to database before we initialize interface
    # add tags
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    for t in tags:
        db_empty.add_new_tag(t)

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    tag_names = [tag.name for tag in widget.tagsList.tags]
    assert tag_names == sorted(tags, key=lambda t: t.lower())


def test_left_panel_tags_are_sorted_alphabetically_after_adding(qtbot, db_empty):
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # add tags
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    for tag in tags:
        qtbot.keyClicks(widget.tagsList.addTagBar, tag)
        qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    tag_names = [tag.name for tag in widget.tagsList.tags]
    # in comparison, include read and unread, since those were included on widet
    # initialization too
    assert tag_names == sorted(tags + ["Read", "Unread"], key=lambda w: w.lower())


def test_paper_tag_list_is_sorted_alphabetically_not_case_sensitive(qtbot, db_empty):
    # set up tags to check
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    db_empty.add_paper(u.mine.bibcode)
    for t in tags:
        db_empty.add_new_tag(t)
        db_empty.tag_paper(u.mine.bibcode, t)

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
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

    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    # then add the final tag in the list
    to_add = tags[-1]
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    for tag_item in widget.rightPanel.tags:
        if tag_item.text() == to_add:
            tag_item.setChecked(True)
    qtbot.mouseClick(widget.rightPanel.doneEditingTagsButton, Qt.LeftButton)

    expected_tags = tags[:3] + [tags[-1]]
    expected = "Tags: " + ", ".join(sorted(expected_tags, key=lambda x: x.lower()))
    assert widget.rightPanel.tagText.text() == expected


def test_tag_checkboxes_are_sorted_alphabetically_not_case_sensitive(qtbot, db_temp):
    # set up tags to check
    tags = ["abc", "zyx", "Aye", "Test", "ZAA"]
    for t in tags:
        db_temp.add_new_tag(t)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    tags = [tag.text() for tag in widget.rightPanel.tags]
    assert tags == sorted(tags, key=lambda x: x.lower())


def test_tag_checkboxes_are_sorted_properly_after_adding_new_tag(qtbot, db_temp):
    # set up tags to check
    tags = ["abc", "zyx", "Test", "ZAA"]
    for t in tags:
        db_temp.add_new_tag(t)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # click to show the checkboxes
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    # then add one in the left panel
    qtbot.mouseClick(widget.tagsList.addTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.tagsList.addTagBar, "Aye")
    qtbot.keyPress(widget.tagsList.addTagBar, Qt.Key_Enter)
    # then ensure this new checkbox was added appropriately
    tags = [tag.text() for tag in widget.rightPanel.tags]
    assert "Aye" in tags
    assert tags == sorted(tags, key=lambda x: x.lower())


def test_tag_checkboxes_are_sorted_properly_after_deleting_tag(qtbot, db_temp):
    # set up tags to check
    tags = ["abc", "zyx", "Test", "ZAA"]
    for t in tags:
        db_temp.add_new_tag(t)

    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # click to show the checkboxes
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editTagsButton, Qt.LeftButton)
    # then delete a tag from the left panel
    qtbot.mouseClick(widget.firstDeleteTagButton, Qt.LeftButton)
    qtbot.keyClicks(widget.secondDeleteTagEntry, "Test")
    qtbot.keyPress(widget.secondDeleteTagEntry, Qt.Key_Enter)
    qtbot.mouseClick(widget.thirdDeleteTagButton, Qt.LeftButton)
    # then ensure this new checkbox was removed appropriately
    tags = [tag.text() for tag in widget.rightPanel.tags]
    assert "Test" not in tags
    assert tags == sorted(tags, key=lambda x: x.lower())


def test_db_update_reflected_in_interface(qtbot, db_update):
    widget = MainWindow(db_update)
    qtbot.addWidget(widget)
    cite_strings = [paper.citeText.text() for paper in widget.papersList.papers]
    assert "Brown, Gnedin, Li, 2018, ApJ, 864, 94" in cite_strings
    assert "Brown, Gnedin, Li, 2022, arXiv:1804.09819" not in cite_strings
    assert "Brown, Gnedin, 2022, MNRAS, 514, 280" in cite_strings
    assert "Brown, Gnedin, 2022, arXiv:2203.00559" not in cite_strings


def test_papers_are_in_sorted_order_to_begin(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    dates = [
        db.get_paper_attribute(paper.bibcode, "pubdate")
        for paper in widget.papersList.papers
    ]

    assert dates == sorted(dates)


def test_papers_are_in_sorted_order_after_adding(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # add two papers: one very old, one very recent
    for bibcode in [u.mine_recent.bibcode, u.bbfh.bibcode]:
        qtbot.keyClicks(widget.searchBar, bibcode)
        qtbot.keyPress(widget.searchBar, Qt.Key_Enter)
    # then check sorting
    dates = [
        db_temp.get_paper_attribute(paper.bibcode, "pubdate")
        for paper in widget.papersList.papers
    ]
    assert dates == sorted(dates)


def test_paper_sort_is_initially_by_date(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    bibcodes = [paper.bibcode for paper in widget.papersList.papers]
    assert bibcodes == [u.tremonti.bibcode, u.mine.bibcode]


def test_paper_sort_dropdown_can_sort_by_author(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by First Author")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.papers]
    assert bibcodes == [u.mine.bibcode, u.tremonti.bibcode]


def test_paper_sort_dropdown_can_sort_by_author_same_last_name(qtbot, db_temp):
    # add another paper by Warren Brown, should be sorted after me (Gillen Brown)
    db_temp.add_paper("2015ApJ...804...49B")
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by First Author")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.papers]
    assert bibcodes == [u.mine.bibcode, "2015ApJ...804...49B", u.tremonti.bibcode]


def test_paper_sort_dropdown_can_sort_in_both_directions(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by First Author")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.papers]
    assert bibcodes == [u.mine.bibcode, u.tremonti.bibcode]
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by Date")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.papers]
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
    widget = MainWindow(db_empty)
    qtbot.addWidget(widget)
    # find the dropdown to sort by date
    index = widget.papersList.sortChooser.findText("Sort by First Author")
    widget.papersList.sortChooser.setCurrentIndex(index)
    # # then check the papers in the list
    bibcodes = [paper.bibcode for paper in widget.papersList.papers]
    # since these are all one author, they should be in date order
    assert bibcodes == [
        u.mine.bibcode,
        "2021NewA...8401501B",
        "2021MNRAS.508.5935B",
        u.mine_recent.bibcode,
    ]


def test_edit_citation_keyword_button_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True


def test_citation_keyword_text_shown_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.citeKeyText.isHidden() is True


def test_edit_citation_keyword_edit_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True


def test_edit_citation_keyword_edit_error_text_hidden_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_button_shown_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False


def test_edit_citation_keyword_button_text_is_correct(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.editCiteKeyButton.text() == "Edit Citation Keyword"


def test_citation_keyword_text_shown_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.citeKeyText.isHidden() is False


def test_citation_keyword_text_is_correct(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    paper = widget.papersList.papers[0]
    qtbot.mouseClick(paper, Qt.LeftButton)
    true_cite_key = db.get_paper_attribute(paper.bibcode, "citation_keyword")
    assert widget.rightPanel.citeKeyText.text() == f"Citation Keyword: {true_cite_key}"


def test_edit_citation_keyword_edit_hidden_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True


def test_edit_citation_keyword_edit_error_text_hidden_when_paper_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_button_hidden_when_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True


def test_citation_keyword_text_not_hidden_when_button_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    assert widget.rightPanel.citeKeyText.isHidden() is False


def test_citation_keyword_text_has_placeholder_text(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    correct_placeholder = "e.g. yourname_etal_2022"
    assert widget.rightPanel.editCiteKeyEntry.placeholderText() == correct_placeholder


def test_edit_citation_keyword_entry_shown_when_button_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is False


def test_edit_citation_keyword_error_text_not_shown_when_button_clicked(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_good_entry_updates_database(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    new_key = db_temp.get_paper_attribute(
        widget.papersList.papers[0].bibcode, "citation_keyword"
    )
    assert new_key == "test_key"


def test_edit_citation_keyword_good_entry_updates_shown_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.citeKeyText.text() == "Citation Keyword: test_key"


def test_edit_citation_keyword_good_entry_resets_buttons(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_good_entry_clears_entry(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.editCiteKeyEntry.text() == ""


def test_edit_citation_keyword_spaces_not_allowed(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.text() == "Spaces not allowed"


def test_edit_citation_keyword_duplicates_not_allowed(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is False
    assert (
        widget.rightPanel.editCiteKeyErrorText.text()
        == "Another paper already uses this"
    )


def test_edit_citation_keyword_spaces_doesnt_reset_buttons(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is False
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is False


def test_edit_citation_keyword_duplicates_doesnt_reset_buttons(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is False
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is False


def test_edit_citation_keyword_spaces_doesnt_clear_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.editCiteKeyEntry.text() == "test key"


def test_edit_citation_keyword_duplicates_doesnt_clear_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    assert widget.rightPanel.editCiteKeyEntry.text() == "test_key"


def test_edit_citation_keyword_spaces_doesnt_update_database(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    bibcode = widget.papersList.papers[0].bibcode
    assert db_temp.get_paper_attribute(bibcode, "citation_keyword") == bibcode


def test_edit_citation_keyword_duplicates_doesnt_update_database(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    qtbot.mouseClick(widget.papersList.papers[1], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "test_key")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Return)
    bibcode_update = widget.papersList.papers[0].bibcode
    assert db_temp.get_paper_attribute(bibcode_update, "citation_keyword") == "test_key"
    bibcode_dup = widget.papersList.papers[1].bibcode
    assert db_temp.get_paper_attribute(bibcode_dup, "citation_keyword") == bibcode_dup


def test_edit_citation_keyword_buttons_hidden_when_paper_deleted(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.firstDeletePaperButton, Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.secondDeletePaperButton, Qt.LeftButton)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is True
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_entry_escape_exit_resets_buttons(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "abc")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Escape)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_entry_backspace_exit_resets_buttons(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "abc")
    # back out the text we entered
    for _ in range(3):
        qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Backspace)
    # buttons should not be reset yet
    assert widget.rightPanel.editCiteKeyButton.isHidden() is True
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is False
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True
    # buttons should reset after one more backspace
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Backspace)
    assert widget.rightPanel.editCiteKeyButton.isHidden() is False
    assert widget.rightPanel.editCiteKeyEntry.isHidden() is True
    assert widget.rightPanel.citeKeyText.isHidden() is False
    assert widget.rightPanel.editCiteKeyErrorText.isHidden() is True


def test_edit_citation_keyword_entry_escape_exit_clears_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "abc")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Escape)
    assert widget.rightPanel.editCiteKeyEntry.text() == ""


def test_edit_citation_keywored_entry_backspace_exit_clears_text(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "abc")
    # back out the text we entered
    for _ in range(3):
        qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Backspace)
    # buttons should reset after one more backspace
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Backspace)

    assert widget.rightPanel.editCiteKeyEntry.text() == ""


def test_edit_citation_keywored_entry_escape_exit_doesnt_change_db(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "abc")
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Escape)
    bibcode = widget.papersList.papers[0].bibcode
    assert db_temp.get_paper_attribute(bibcode, "citation_keyword") == bibcode


def test_edit_citation_keywored_entry_backspace_exit_doesnt_change_db(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    qtbot.mouseClick(widget.rightPanel.editCiteKeyButton, Qt.LeftButton)
    qtbot.keyClicks(widget.rightPanel.editCiteKeyEntry, "abc")
    # back out the text we entered
    for _ in range(3):
        qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Backspace)
    # buttons should reset after one more backspace
    qtbot.keyPress(widget.rightPanel.editCiteKeyEntry, Qt.Key_Backspace)
    bibcode = widget.papersList.papers[0].bibcode
    assert db_temp.get_paper_attribute(bibcode, "citation_keyword") == bibcode


def test_widgets_dont_go_outside_of_splitter(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
    # get the original positions
    o_sizes = widget.splitter.sizes()
    # check examples in each panel
    assert widget.tagsList.addTagBar.size().width() <= o_sizes[0]
    assert widget.papersList.papers[0].size().width() <= o_sizes[1]
    assert widget.rightPanel.titleText.size().width() <= o_sizes[2]


def test_resizing_splitter_resizes_widgets(qtbot, db_temp):
    widget = MainWindow(db_temp)
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.papersList.papers[0], Qt.LeftButton)
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
        new_sizes[1] * 0.7 <= widget.papersList.papers[0].size().width() <= new_sizes[1]
    )
    assert (
        new_sizes[2] * 0.7 <= widget.rightPanel.titleText.size().width() <= new_sizes[2]
    )
