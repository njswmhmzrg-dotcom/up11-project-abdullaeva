from database import Database

def main():
    print("--- ТЕСТ ПОДКЛЮЧЕНИЯ К БД ---")
    db = Database()
    
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM motorcycles")
            count = cursor.fetchone()[0] # type: ignore
            print(f"✅ Количество записей в таблице: {count}")
            cursor.close()
        except Exception as e:
            print(f"❌ Ошибка при выполнении запроса: {e}")
        finally:
            # Возвращаем соединение в пул
            db.release_connection(conn)
    else:
        print("❌ Не удалось получить соединение (проверьте настройки в database.py).")
        
    db.close_all()

if __name__ == "__main__":
    main()