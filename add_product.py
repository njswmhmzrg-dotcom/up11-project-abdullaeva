import psycopg2

def add_product(name, price, category_id):
    if not name:
        print("Ошибка: имя не может быть пустым")
        return None
    if not isinstance(price, (int, float)) or price <= 0:
        print("Ошибка: цена должна быть числом > 0")
        return None
    if not isinstance(category_id, int):
        print("Ошибка: category_id должен быть числом")
        return None

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="orders_db", user="postgres", password="123"
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, price, category_id)
            VALUES (%s, %s, %s) RETURNING product_id;
        """, (name, price, category_id))
        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Товар успешно добавлен с ID: {new_id}")
        return new_id
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("--- Тесты для Задания 5.2 ---")
    add_product("", 1000, 1)         # Пустое имя
    add_product("Часы", -100, 1)     # Цена < 0
    add_product("Часы", 1000, 99999) # Категории нет
    add_product("Мотоцикл Тест", 50000, 1) # Всё правильно