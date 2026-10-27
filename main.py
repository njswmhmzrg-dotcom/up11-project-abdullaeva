import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QScrollArea, QPushButton, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import Qt
from database import Database

def create_card(product):
    # product: (0:id, 1:name, 2:cat, 3:manuf, 4:comp, 5:price, 6:img_path, 7:qty)
    card = QFrame()
    card.setObjectName("productCard")
    
    # Добавляем легкую тень для красоты
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setColor(QColor(0, 0, 0, 30))
    shadow.setOffset(0, 4)
    card.setGraphicsEffect(shadow)
    
    card_layout = QHBoxLayout(card)
    card_layout.setContentsMargins(20, 20, 20, 20)
    
    # --- 1. ИЗОБРАЖЕНИЕ ---
    image_label = QLabel()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Берем картинку из БД или ставим заглушку
    img_name = product[6] if product[6] else "picture.png"
    
    # Формируем путь
    img_path = os.path.join(base_dir, "Images", img_name)
    
    # ДИАГНОСТИКА (выведется в терминал)
    print(f"Ищу картинку: {img_path}")
    
    pixmap = QPixmap(img_path)
    if not pixmap.isNull():
        image_label.setPixmap(pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_label.setStyleSheet("background-color: transparent;")
    else:
        # Если картинки нет, ставим заглушку
        img_path_fallback = os.path.join(base_dir, "picture.png")
        pixmap_fallback = QPixmap(img_path_fallback)
        if not pixmap_fallback.isNull():
            image_label.setPixmap(pixmap_fallback.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            image_label.setText("Нет фото")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("background-color: #f0f0f0; border-radius: 8px; color: #888;")
        
    image_label.setFixedSize(140, 140)
    card_layout.addWidget(image_label)
    
    # --- 2. ТЕКСТОВАЯ ЧАСТЬ ---
    text_layout = QVBoxLayout()
    text_layout.setSpacing(8)
    
    # Производство | Наименование
    title_label = QLabel(f"{product[3]} | {product[1]}") 
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
    text_layout.addWidget(title_label)
    
    # Категория
    category_label = QLabel(f"Категория: {product[2]}")
    category_label.setStyleSheet("color: #555555; font-size: 14px;")
    text_layout.addWidget(category_label)
    
    # Количество (с проверкой на остаток)
    qty = product[7]
    if qty == 0:
        qty_text = "Недоступно для заказа"
        qty_style = "color: #ff8080; font-weight: bold; font-size: 14px;"
    elif qty <= 3:
        qty_text = f"Осталось мало: {qty} шт."
        qty_style = "color: #ff8080; font-weight: bold; font-size: 14px;"
    else:
        qty_text = f"В наличии: {qty} шт."
        qty_style = "color: #228B22; font-weight: bold; font-size: 14px;"
        
    qty_label = QLabel(qty_text)
    qty_label.setStyleSheet(qty_style)
    text_layout.addWidget(qty_label)
    
    # Состав
    comp_label = QLabel(f"Состав: {product[4]}")
    comp_label.setStyleSheet("color: #777777; font-size: 13px;")
    comp_label.setWordWrap(True) # Чтобы длинный текст переносился
    text_layout.addWidget(comp_label)
    
    card_layout.addLayout(text_layout)
    card_layout.addStretch() 
    
    # --- 3. ЦЕНА ---
    # Форматируем с 2 знаками после запятой и знаком рубля (руб.)
    price_str = f"от {product[5]:,.2f} руб.".replace(',', ' ')
    price_label = QLabel(price_str)
    price_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #70B2AF;")
    price_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
    card_layout.addWidget(price_label)
    
    # --- СТИЛИЗАЦИЯ КАРТОЧКИ ---
    # Если остаток <= 3, красим фон в #ff8080 (по гайдлайну)
    if qty <= 3:
        card.setStyleSheet("""
            QFrame#productCard {
                background-color: #ff8080;
                border-radius: 12px;
                border: 1px solid #e06b6b;
            }
            QLabel { background-color: transparent; }
        """)
    else:
        card.setStyleSheet("""
            QFrame#productCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
            QLabel { background-color: transparent; }
        """)
        
    return card

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.db = Database()
        
        self.setWindowTitle("Мир мотоциклов — Каталог")
        self.resize(950, 750)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Общий фон окна - дополнительный фон из гайдлайна (#D2F6E7) для контраста с белыми карточками
        self.setStyleSheet("""
            QMainWindow { background-color: #F5FAF8; } 
            QWidget { font-family: Calibri; }
            QScrollArea { border: none; background-color: transparent; }
        """)
        
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # --- ШАПКА (Заголовок и Кнопка Выход) ---
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Мир мотоциклов")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #70B2AF;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch() 
        
        # Кнопка Выхода (по гайдлайну: акцентный фон #70B2AF, черный текст)
        btn_exit = QPushButton("Выход")
        btn_exit.setFixedSize(120, 45)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #70B2AF;
                color: #000000;
                font-weight: bold;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5A9592;
            }
        """)
        btn_exit.clicked.connect(self.close)
        header_layout.addWidget(btn_exit)
        
        main_layout.addLayout(header_layout)
        
        # --- СПИСОК ТОВАРОВ ---
        self.products = self.db.get_products()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20) # Расстояние между карточками
        
        if not self.products:
            error_label = QLabel("База данных пуста или нет подключения.")
            error_label.setStyleSheet("font-size: 18px; color: red;")
            scroll_layout.addWidget(error_label)
        else:
            for product in self.products:
                card = create_card(product)
                scroll_layout.addWidget(card)
                
        scroll_layout.addStretch() 
        scroll.setWidget(scroll_content)
        
        main_layout.addWidget(scroll)
        self.setCentralWidget(central)

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()