import sys
from PySide6.QtWidgets import QApplication
import os

from database.db_manager import DatabaseManager
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    
    db = DatabaseManager('data_motomaintenance.db')
    
    style_path = os.path.join(os.path.dirname(__file__), "style", "app.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
            
    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()