import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from library import database, interface


# exclude this run function from test coverage, as it just launches the app. Some test
# can be done, but they require a ton of monkeypatching and can really only test that
# I called the functions here. Just test this by running the application
def run():  # pragma: no cover
    home_path = Path(__file__).parent.parent.absolute()
    db_path = home_path / "USER_DATA_DO_NOT_DELETE.db"
    db = database.Database(db_path)

    # The application is what starts QT
    app = QApplication()

    # then set up the fonts
    interface.set_up_fonts()

    # set up app icon
    app.setWindowIcon(QIcon(str(home_path / "library" / "resources" / "icon.png")))

    # The MainWindow class holds all the structure
    window = interface.MainWindow(db)

    # Execute application
    sys.exit(app.exec())
