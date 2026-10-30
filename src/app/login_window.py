import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QMessageBox)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from src.app.database import Database

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(APP_DIR)
RES_DIR = os.path.join(SRC_DIR, "resources")
IMG_DIR = os.path.join(RES_DIR, "Images")

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.logged_in = False
        
        self.setWindowTitle("Авторизация — Мир мотоциклов")
        self.resize(400, 300)
        
        icon_path = os.path.join(IMG_DIR, "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(IMG_DIR, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet("""
            QWidget { background-color: #FFFFFF; font-family: Calibri; color: #000000; }
            QLineEdit { background-color: #F5FAF8; border: 1px solid #70B2AF; border-radius: 6px; padding: 10px; font-size: 16px; }
            QPushButton { background-color: #70B2AF; color: #000000; font-weight: bold; border-radius: 6px; padding: 10px; font-size: 16px; }
            QPushButton:hover { background-color: #5A9592; }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        title = QLabel("Вход в систему")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #70B2AF;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Введите логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("admin или client01")
        self.login_input.returnPressed.connect(self.check_login) 
        layout.addWidget(self.login_input)
        
        btn_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        btn_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Войти как гость")
        self.cancel_button.setStyleSheet("background-color: #E0E0E0;")
        self.cancel_button.clicked.connect(self.enter_as_guest)
        btn_layout.addWidget(self.cancel_button)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def check_login(self):
        login = self.login_input.text().strip()
        if not login:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите логин!")
            return
            
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка БД", "Нет подключения к базе данных.")
            return
            
        try:
            cursor = conn.cursor()
            sql = "SELECT user_id, role_id, last_name, first_name, middle_name FROM users WHERE login = %s"
            cursor.execute(sql, (login,))
            result = cursor.fetchone()
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {e}")
            return
        finally:
            self.db.release_connection(conn)
            
        if result is None:
            QMessageBox.warning(self, "Ошибка входа", "Неверный логин. Попробуйте снова.")
        else:
            self.role_id = result[1]
            middle = result[4] if result[4] else ""
            full_name = f"{result[2]} {result[3]} {middle}".strip()
            
            from src.app.main import MainWindow 
            self.main_window = MainWindow(db=self.db, role_id=self.role_id, full_name=full_name)
            self.main_window.show()
            self.logged_in = True
            self.close()

    def enter_as_guest(self):
        from src.app.main import MainWindow
        self.main_window = MainWindow(db=self.db, role_id=None, full_name="Гость")
        self.main_window.show()
        self.logged_in = True
        self.close()

    def closeEvent(self, event):
        if not self.logged_in:
            self.enter_as_guest()
        event.accept()