import psycopg2
from psycopg2 import pool

class Database:
    def __init__(self):
        self.connection_pool = None
        try:
            # Создаем пул соединений
            self.connection_pool = pool.SimpleConnectionPool(
                1, 10, # minconn=1, maxconn=10
                host="localhost",
                port=5432,
                database="mir_moto", # Имя вашей БД
                user="postgres",
                password="123"       # Ваш пароль
            )
            print("✅ Пул соединений успешно создан.")
        except psycopg2.Error as e:
            print(f"❌ Ошибка БД: {e}")
            self.connection_pool = None

    def get_connection(self):
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None

    def release_connection(self, conn):
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Пул соединений закрыт.")

    # --- ГЛАВНЫЙ МЕТОД ДЛЯ ВЫВОДА КАТАЛОГА ---
    def get_products(self):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            # Запрос с LEFT JOIN и COALESCE (из теории к паре 33)
            sql = """
                SELECT 
                    m.model_id, 
                    m.name, 
                    m.category, 
                    m.manufacturer, 
                    m.composition, 
                    m.base_price, 
                    m.image_path, 
                    COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM models m
                LEFT JOIN stock_items si ON m.model_id = si.model_id
                GROUP BY m.model_id
                ORDER BY m.model_id;
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении товаров: {e}")
            return []
        finally:
            self.release_connection(conn)