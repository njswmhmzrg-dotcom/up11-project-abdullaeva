import psycopg2
from discount import calculate_price

conn = psycopg2.connect(
    host="localhost", port=5432, database="orders_db", user="postgres", password="123"
)
cursor = conn.cursor()

cursor.execute("SELECT product_id, name, price FROM products LIMIT 3;")
products = cursor.fetchall()

print("Проверка первых 3 товаров:")
for p in products:
    product_id = p[0]
    name = p[1]
    price = p[2]
    final_price = calculate_price(product_id, price)
    discount = "Да" if final_price < price else "Нет"
    print(f"{name} | Цена: {price} | Итог: {final_price} | Скидка: {discount}")

cursor.close()
conn.close()
