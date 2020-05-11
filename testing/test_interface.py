"""
test_interface.py

Perform tests on the GUI using pytest-qt
"""
from pathlib import Path
import random

import pytest
import pytestqt
from PySide2.QtCore import Qt

from library.interface import MainWindow, get_fonts
from library.lib import Library
import test_utils as u


@pytest.fixture(name="empty_lib")
def temporary_library():
    file_path = Path(f"{random.randint(0, 1000000000)}.db")
    db = Library(file_path)
    yield db
    file_path.unlink()  # removes this file


def test_get_all_fonts():
    font_dir = Path("/Users/gillenb/code/library/fonts/")
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


def test_add_paper(qtbot, empty_lib):
    assert len(empty_lib.get_all_bibcodes()) == 0
    widget = MainWindow(empty_lib)
    widget.show()
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.searchBar, u.my_bibcode)
    qtbot.mouseClick(widget.addButton, Qt.LeftButton)
    assert len(empty_lib.get_all_bibcodes()) == 1
    assert u.my_bibcode in empty_lib.get_all_bibcodes()
