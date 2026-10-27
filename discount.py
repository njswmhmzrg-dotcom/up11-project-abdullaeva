import psycopg2

def calculate_price(product_id, base_price):
    # Проверка типов (Задание 3)
    if not isinstance(product_id, int):
        print("Ошибка: product_id должен быть числом")
        return None
    if not isinstance(base_price, (int, float)):
        print("Ошибка: base_price должен быть числом")
        return None
    if base_price <= 0:
        print("Ошибка: цена должна быть > 0")
        return None

    conn = None
    cursor = None
    
    # Обработка ошибок БД (Задание 2)
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="orders_db", user="postgres", password="wrong"
        )
        cursor = conn.cursor()
        
        query = """
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.order_id 
            WHERE oi.stock_item_id IN (SELECT stock_item_id FROM stock_items WHERE product_id = %s)
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()

        # Проверка fetchone() на None (Задание 4)
        if result is None:
            print("Ошибка: нет результата")
            return None
            
        orders_count = result[0]

        if orders_count == 0:
            return float(base_price) * 0.75
        else:
            return float(base_price)
            
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Тесты для Задания 3.2 и 4.2
if __name__ == "__main__":
    print("--- Тесты на неправильные данные (3.2) ---")
    calculate_price("abc", 1000) 
    calculate_price(1, "abc")   
    calculate_price(1, -100)    
    calculate_price(1, None)    
    
    print("\n--- Тест для Задания 4.2 ---")
    print("Результат для несуществующего ID:", calculate_price(99999, 1000))