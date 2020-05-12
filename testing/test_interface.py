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
from PySide2.QtWidgets import QApplication

from library.interface import MainWindow, get_fonts, set_up_fonts
from library.lib import Library
import test_utils as u


@pytest.fixture(name="empty_lib")
def temporary_library():
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Library(file_path)
    yield db
    file_path.unlink()  # removes this file


@pytest.fixture(name="lib")
def testing_library():
    return Library("./testing.db")


def test_get_all_fonts():
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


def test_setup_fonts(qtbot):
    """qtbot is needed to initialize the application"""
    fontDb = QFontDatabase()

    assert not fontDb.hasFamily("Lobster")
    assert not fontDb.hasFamily("Cabin")

    set_up_fonts()

    assert fontDb.hasFamily("Lobster")
    assert fontDb.hasFamily("Cabin")


def test_add_paper(qtbot, empty_lib):
    assert len(empty_lib.get_all_bibcodes()) == 0
    widget = MainWindow(empty_lib)
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.my_bibcode)
    qtbot.mouseClick(widget.addButton, Qt.LeftButton)
    assert len(empty_lib.get_all_bibcodes()) == 1
    assert u.my_bibcode in empty_lib.get_all_bibcodes()


def test_nonemtpy_lib_setup(lib):
    """Just tests that the testing database has some papers"""
    assert len(lib.get_all_bibcodes()) > 0


def test_exit_action(qtbot, lib, monkeypatch):
    # see https://pytest-qt.readthedocs.io/en/3.3.0/app_exit.html
    exit_calls = []
    monkeypatch.setattr(QApplication, "quit", lambda: exit_calls.append(1))

    widget = MainWindow(lib)
    qtbot.addWidget(widget)
    widget.exitAction.trigger()

    assert exit_calls == [1]


def test_exit_keyboard_shortcut(qtbot, lib, monkeypatch):
    # see https://pytest-qt.readthedocs.io/en/3.3.0/app_exit.html
    exit_calls = []
    monkeypatch.setattr(QApplication, "quit", lambda: exit_calls.append(1))

    widget = MainWindow(lib)
    qtbot.addWidget(widget)
    widget.show()  # needed to activate keyboard shortcuts
    qtbot.waitForWindowShown(widget)
    qtbot.keyPress(widget, "q", Qt.ControlModifier)

    assert exit_calls == [1]


# Testing the menu item itself is hard. I'll skip this for now
# https://github.com/pytest-dev/pytest-qt/issues/195
