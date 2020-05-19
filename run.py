import sys
from pathlib import Path

from PySide2.QtWidgets import QApplication

from library import lib, interface

if __name__ == "__main__":
    if len(sys.argv) == 1:  # no specified path
        db_path = Path(__file__).parent.absolute() / "USER_DATA_DO_NOT_DELETE.db"
    else:
        db_path = Path(sys.argv[1]).absolute()
    lib = lib.Library(db_path)

    # The application is what starts QT
    app = QApplication()

    # then set up the fonts
    interface.set_up_fonts()

    # The MainWindow class holds all the structure
    window = interface.MainWindow(lib)

    # Execute application
    sys.exit(app.exec_())
