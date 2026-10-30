import psycopg2
from psycopg2 import pool

class Database:
    def __init__(self):
        self.connection_pool = None
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 10,
                host="localhost",
                port=5432,
                database="mir_moto",
                user="postgres",
                password="123"
            )
        except psycopg2.Error:
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
            self.connection_pool = None

    def get_categories(self):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM models ORDER BY category;")
            return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []
        finally:
            self.release_connection(conn)

    def get_products(self):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            sql = """
                SELECT 
                    m.model_id, 
                    m.name, 
                    m.category, 
                    m.manufacturer, 
                    m.composition, 
                    m.base_price AS price, 
                    m.image_path, 
                    COALESCE(SUM(si.quantity), 0) AS total_quantity,
                    (SELECT COUNT(*) 
                     FROM order_items oi 
                     JOIN stock_items s ON oi.stock_item_id = s.stock_item_id 
                     JOIN orders o ON oi.order_id = o.order_id
                     WHERE s.model_id = m.model_id 
                       AND o.order_date >= '2026-09-01' 
                       AND o.order_date < '2026-10-01'
                    ) as orders_count
                FROM models m
                LEFT JOIN stock_items si ON m.model_id = si.model_id
                GROUP BY m.model_id
                ORDER BY m.model_id;
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception:
            conn.rollback()
            try:
                cursor.execute("""
                    SELECT 
                        m.model_id, 
                        m.name, 
                        m.category, 
                        m.manufacturer, 
                        m.composition, 
                        m.base_price AS price, 
                        m.image_path, 
                        COALESCE(SUM(si.quantity), 0) AS total_quantity,
                        0 as orders_count
                    FROM models m
                    LEFT JOIN stock_items si ON m.model_id = si.model_id
                    GROUP BY m.model_id
                    ORDER BY m.model_id;
                """)
                return cursor.fetchall()
            except Exception:
                return []
        finally:
            self.release_connection(conn)

    def get_orders(self):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            sql = """
                SELECT 
                    o.order_id, 
                    o.order_date, 
                    u.last_name || ' ' || u.first_name || ' ' || COALESCE(u.middle_name, '') AS client_name
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                ORDER BY o.order_date DESC;
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            self.release_connection(conn)