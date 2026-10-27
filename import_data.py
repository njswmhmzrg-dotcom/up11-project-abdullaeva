import csv
import psycopg2

# ВАШ ПАРОЛЬ ОТ POSTGRESQL
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mir_moto",
    "user": "postgres",
    "password": "123" # <--- Проверьте пароль!
}

def import_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Подключение к БД успешно.")

        # Создаем таблицы, если их нет
        cursor.execute("""
            DROP TABLE IF EXISTS stock_items CASCADE;
            DROP TABLE IF EXISTS models CASCADE;
            DROP TABLE IF EXISTS variants CASCADE;

            CREATE TABLE variants (
                variant_id SERIAL PRIMARY KEY,
                variant_name VARCHAR(50) UNIQUE
            );

            CREATE TABLE models (
                model_id SERIAL PRIMARY KEY,
                category VARCHAR(100),
                subcategory VARCHAR(100),
                image_path VARCHAR(255),
                name VARCHAR(100),
                manufacturer VARCHAR(100),
                description TEXT,
                composition TEXT,
                base_price NUMERIC(10, 2)
            );

            CREATE TABLE stock_items (
                stock_id SERIAL PRIMARY KEY,
                model_id INTEGER REFERENCES models(model_id),
                variant_id INTEGER REFERENCES variants(variant_id),
                quantity INTEGER,
                price NUMERIC(10, 2)
            );
        """)
        conn.commit()
        print("Таблицы созданы.")

        # Импорт вариантов
        try:
            with open('Variants_import.csv', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row: cursor.execute("INSERT INTO variants (variant_name) VALUES (%s) ON CONFLICT DO NOTHING", (row[0],))
        except FileNotFoundError:
            print("Файл Variants_import.csv не найден!")

        # Импорт моделей
        try:
            with open('Products_import.csv', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row:
                        cursor.execute("""
                            INSERT INTO models (category, subcategory, image_path, name, manufacturer, description, composition, base_price)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (row[0], row[1], row[2], row[3], row[4], row[5], row[6], float(row[7])))
        except FileNotFoundError:
            print("Файл Products_import.csv не найден!")

        # Импорт остатков
        try:
            with open('Stock_Items_import.csv', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row:
                        cursor.execute("SELECT model_id FROM models WHERE name=%s AND manufacturer=%s", (row[0], row[1]))
                        model_res = cursor.fetchone()
                        cursor.execute("SELECT variant_id FROM variants WHERE variant_name=%s", (row[2],))
                        variant_res = cursor.fetchone()
                        if model_res and variant_res:
                            cursor.execute("""
                                INSERT INTO stock_items (model_id, variant_id, quantity, price)
                                VALUES (%s, %s, %s, %s)
                            """, (model_res[0], variant_res[0], int(row[3]), float(row[4])))
        except FileNotFoundError:
            print("Файл Stock_Items_import.csv не найден!")

        conn.commit()
        print("✅ Данные успешно загружены в БД!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    import_data()