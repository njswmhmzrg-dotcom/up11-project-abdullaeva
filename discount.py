import psycopg2

def calculate_price(product_id, base_price):
    #  (Задание 4)
    try:
        #  (Задание 1)
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="orders_db",
            user="postgres",
            password="123"
        )
        cursor = conn.cursor()

        #  (Задание 2)
        query = """
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.order_id 
            WHERE oi.stock_item_id IN (SELECT stock_item_id FROM stock_items WHERE product_id = %s)
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """
        # В БД связь идет через stock_items, запрос немного изменен
        cursor.execute(query, (product_id,))
        
        #  Проверка результата
        result = cursor.fetchone()
        orders_count = result[0]

        # (Задание 3)
        if orders_count == 0:
            final_price = float(base_price) * 0.75
        else:
            final_price = base_price

        return final_price

    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None
    finally:
        # Закрытие соединения
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

#  (Задание 3.2)
if __name__ == "__main__":
    test_price = calculate_price(1, 1000)
    print(f"Результат для товара 1: {test_price}")