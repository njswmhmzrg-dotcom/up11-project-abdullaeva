import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QScrollArea, QPushButton, QFrame, 
                               QGraphicsDropShadowEffect, QLineEdit, QComboBox, QDialog, QTableWidget, QTableWidgetItem)
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import Qt
from src.app.database import Database
from src.app.login_window import LoginWindow

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(APP_DIR)
RES_DIR = os.path.join(SRC_DIR, "resources")
IMG_DIR = os.path.join(RES_DIR, "Images")

class OrdersWindow(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Список заказов")
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Дата", "Клиент"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        orders = self.db.get_orders()
        self.table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(order[0])))
            self.table.setItem(row, 1, QTableWidgetItem(str(order[1])))
            self.table.setItem(row, 2, QTableWidgetItem(str(order[2])))
            
        layout.addWidget(self.table)
        
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)

def create_card(product):
    card = QFrame()
    card.setObjectName("productCard")
    
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setColor(QColor(0, 0, 0, 30))
    shadow.setOffset(0, 4)
    card.setGraphicsEffect(shadow)
    
    card_layout = QHBoxLayout(card)
    card_layout.setContentsMargins(20, 20, 20, 20)
    
    image_label = QLabel()
    img_name = product[6] 
    img_path = ""
    
    if img_name:
        clean_name = os.path.basename(img_name)
        path_img = os.path.join(IMG_DIR, clean_name)
        if os.path.exists(path_img):
            img_path = path_img

    if not img_path:
        pic_path = os.path.join(IMG_DIR, "picture.png")
        img_path = pic_path if os.path.exists(pic_path) else ""

    pixmap = QPixmap(img_path)
    if not pixmap.isNull():
        image_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    else:
        image_label.setText("Нет фото")
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("background-color: #f0f0f0; border-radius: 8px; color: #888;")
        
    image_label.setFixedSize(120, 120)
    card_layout.addWidget(image_label)
    
    text_layout = QVBoxLayout()
    text_layout.setSpacing(5)
    
    title_label = QLabel(product[1]) 
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
    text_layout.addWidget(title_label)
    
    text_layout.addWidget(QLabel(f"Категория: {product[2]} | Производитель: {product[3]}"))
    text_layout.addWidget(QLabel(f"Состав: {product[4]}"))
    
    qty = product[7]
    qty_label = QLabel(f"В наличии: {qty} шт.")
    qty_label.setStyleSheet("font-weight: bold;")
    text_layout.addWidget(qty_label)
    
    card_layout.addLayout(text_layout)
    card_layout.addStretch() 
    
    base_price = float(product[5])
    orders_count = product[8]
    
    if orders_count == 0:
        final_price = round(base_price * 0.75, 2)
        price_html = f"""
            <div style='text-align: right;'>
                <span style='color: red; text-decoration: line-through;'>от {base_price:,.2f} руб.</span><br>
                <span style='color: black; font-weight: bold; font-size: 20px;'>от {final_price:,.2f} руб.</span>
                <br><span style='color: #2E8B57; font-weight: bold; font-size: 12px;'>-25%</span>
            </div>
        """
    else:
        price_html = f"<span style='color: #70B2AF; font-weight: bold; font-size: 20px;'>от {base_price:,.2f} руб.</span>"

    price_html = price_html.replace(',', ' ')
    price_label = QLabel(price_html)
    price_label.setTextFormat(Qt.RichText)
    price_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
    card_layout.addWidget(price_label)
    
    if qty == 0:
        card.setStyleSheet("QFrame#productCard { background-color: #ADD8E6; border-radius: 12px; }") 
    elif qty <= 3:
        card.setStyleSheet("QFrame#productCard { background-color: #FF8080; border-radius: 12px; }") 
    else:
        card.setStyleSheet("QFrame#productCard { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E0E0E0; }")
        
    return card

class MainWindow(QMainWindow):
    def __init__(self, db, role_id=None, full_name="Гость"): 
        super().__init__()
        self.db = db
        self.role_id = role_id
        self.full_name = full_name
        
        self.all_products = self.db.get_products()
        
        self.setWindowTitle("Мир мотоциклов — Каталог")
        self.resize(1100, 800)
        
        icon_path = os.path.join(IMG_DIR, "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(RES_DIR, "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(IMG_DIR, "icon.png")
            
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; } 
            QWidget { font-family: Calibri; }
        """)
        
        self.setup_ui()
        self.apply_filters()

    def setup_ui(self):
        central = QWidget()
        self.main_layout = QVBoxLayout(central)
        
        header_layout = QHBoxLayout()
        
        logo_path = os.path.join(RES_DIR, "logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(IMG_DIR, "logo.png")
            
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_label.setPixmap(QPixmap(logo_path).scaledToHeight(40, Qt.SmoothTransformation))
            header_layout.addWidget(logo_label)
            header_layout.addSpacing(10)

        title_label = QLabel("Мир мотоциклов — Каталог")
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #70B2AF;")
        header_layout.addWidget(title_label)
        
        if self.role_id in [1, 2]:
            btn_orders = QPushButton("Заказы")
            btn_orders.setStyleSheet("background-color: #D2F6E7; padding: 5px 15px; border-radius: 5px; font-weight: bold;")
            btn_orders.clicked.connect(self.open_orders)
            header_layout.addWidget(btn_orders)
        
        header_layout.addStretch()
        
        user_label = QLabel(f"👤 {self.full_name}")
        user_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        header_layout.addWidget(user_label)
        
        btn_exit = QPushButton("Выход")
        btn_exit.setStyleSheet("background-color: #70B2AF; font-weight: bold; border-radius: 5px; padding: 5px 15px;")
        btn_exit.clicked.connect(self.logout)
        header_layout.addWidget(btn_exit)
        
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(10)
        
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или составу...")
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #70B2AF; border-radius: 5px;")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input, 2)
        
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("padding: 8px; border: 1px solid #70B2AF; border-radius: 5px;")
        self.category_combo.addItem("Все категории")
        for cat in self.db.get_categories():
            self.category_combo.addItem(cat)
        self.category_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.category_combo, 1)
        
        self.sort_combo = QComboBox()
        self.sort_combo.setStyleSheet("padding: 8px; border: 1px solid #70B2AF; border-radius: 5px;")
        self.sort_combo.addItem("По умолчанию")
        self.sort_combo.addItem("Цена: по возрастанию")
        self.sort_combo.addItem("Цена: по убыванию")
        self.sort_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.sort_combo, 1)
        
        self.main_layout.addLayout(filter_layout)
        self.main_layout.addSpacing(10)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(15)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)
        
        self.setCentralWidget(central)

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        category = self.category_combo.currentText()
        sort_index = self.sort_combo.currentIndex()
        
        filtered = []
        for p in self.all_products:
            name_match = search_text in p[1].lower() or search_text in (p[4] or "").lower()
            cat_match = (category == "Все категории") or (p[2] == category)
            
            if name_match and cat_match:
                filtered.append(p)
                
        if sort_index == 1:
            filtered.sort(key=lambda x: float(x[5]))
        elif sort_index == 2:
            filtered.sort(key=lambda x: float(x[5]), reverse=True)
            
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for p in filtered:
            self.scroll_layout.addWidget(create_card(p))
            
        if not filtered:
            self.scroll_layout.addWidget(QLabel("Ничего не найдено"))
            
        self.scroll_layout.addStretch()

    def open_orders(self):
        self.orders_win = OrdersWindow(self.db)
        self.orders_win.exec()

    def logout(self):
        self.close()
        self.login_window = LoginWindow(self.db)
        self.login_window.show()

    def closeEvent(self, event):
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    window = LoginWindow(db)
    window.show()
    exit_code = app.exec()
    db.close_all()
    sys.exit(exit_code)