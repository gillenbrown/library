"""
test_interface.py

Perform tests on the GUI using pytest-qt
"""
from pathlib import Path
import random

import pytest
import pytestqt
from PySide2.QtCore import Qt
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QApplication, QFileDialog

from library.interface import MainWindow, get_fonts, set_up_fonts, Paper
from library.database import Database
import test_utils as u


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


def test_right_panel_abstract_is_empty_at_beginning(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    assert widget.rightPanel.abstractText.text() == ""


def test_right_panel_title_can_be_set(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    widget.rightPanel.setPaperDetails("Test Title", "")
    assert widget.rightPanel.titleText.text() == "Test Title"


def test_right_panel_abstract_can_be_set(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    widget.rightPanel.setPaperDetails("", "Test Abstract")
    assert widget.rightPanel.abstractText.text() == "Test Abstract"


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


def test_clicking_on_paper_puts_title_in_right_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    rightPanel = widget.rightPanel
    new_paper = Paper(u.my_bibcode, db, rightPanel)
    qtbot.mouseClick(new_paper, Qt.LeftButton)
    assert widget.rightPanel.titleText.text() == u.my_title


def test_clicking_on_paper_puts_abstract_in_right_panel(qtbot, db):
    widget = MainWindow(db)
    qtbot.addWidget(widget)
    rightPanel = widget.rightPanel
    new_paper = Paper(u.my_bibcode, db, rightPanel)
    qtbot.mouseClick(new_paper, Qt.LeftButton)
    assert widget.rightPanel.abstractText.text() == u.my_abstract


def test_double_clicking_on_paper_without_pdf_link_asks_user(
    qtbot, empty_db, monkeypatch
):
    # Here we need to use monkeypatch to simulate user input
    test_loc = "/Users/gillenb/test.pdf"
    # create a mock function to get the file. It needs to have the filter kwarg, since
    # that is used in the actual call
    def mock_get_file(filter=""):
        return test_loc

    monkeypatch.setattr(QFileDialog, "getOpenFileName", mock_get_file)

    widget = MainWindow(empty_db)
    qtbot.addWidget(widget)
    # add a paper to this empty database to match the paper object
    empty_db.add_paper(u.my_bibcode)
    # add a new paper to click on
    rightPanel = widget.rightPanel
    new_paper = Paper(u.my_bibcode, empty_db, rightPanel)
    qtbot.mouseDClick(new_paper, Qt.LeftButton)
    assert empty_db.get_paper_attribute(u.my_bibcode, "local_file") == test_loc


def test_double_clicking_on_paper_but_not_choosing_paper_doesnt_add_it(
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
    # add a paper to this empty database to match the paper object
    empty_db.add_paper(u.my_bibcode)
    # add a new paper to click on
    rightPanel = widget.rightPanel
    new_paper = Paper(u.my_bibcode, empty_db, rightPanel)
    qtbot.mouseDClick(new_paper, Qt.LeftButton)
    assert empty_db.get_paper_attribute(u.my_bibcode, "local_file") == None
