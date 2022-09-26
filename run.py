import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from library import database, interface

# Add this to be sure the interface shows up on Mac
# https://apple.stackexchange.com/q/413361
os.environ["QT_MAC_WANTS_LAYER"] = "1"

if __name__ == "__main__":
    home_path = Path(__file__).parent.absolute()
    if len(sys.argv) == 1:  # no specified path
        db_path = home_path / "USER_DATA_DO_NOT_DELETE.db"
    else:
        db_path = Path(sys.argv[1]).absolute()
    db = database.Database(db_path)

    # The application is what starts QT
    app = QApplication()

    # then set up the fonts
    interface.set_up_fonts()

    # set up app icon
    app.setWindowIcon(QIcon(str(home_path / "icon.png")))

    # The MainWindow class holds all the structure
    window = interface.MainWindow(db)

    # Execute application
    sys.exit(app.exec_())
