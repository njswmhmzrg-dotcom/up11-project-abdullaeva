import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from src.app.database import Database
from src.app.login_window import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    window = LoginWindow(db)
    window.show()
    exit_code = app.exec()
    db.close_all()
    sys.exit(exit_code)