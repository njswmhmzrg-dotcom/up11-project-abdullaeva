DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS stock_items CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS statuses CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE
);

INSERT INTO roles (role_name) VALUES 
('Администратор'), 
('Менеджер'), 
('Клиент');

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    last_name VARCHAR(50),
    first_name VARCHAR(50),
    middle_name VARCHAR(50),
    role_id INTEGER REFERENCES roles(role_id)
);

INSERT INTO users (login, last_name, first_name, middle_name, role_id) VALUES
('admin', 'Иванов', 'Иван', 'Сергеевич', 1),
('manager1', 'Петров', 'Петр', 'Алексеевич', 2),
('client01', 'Сидоров', 'Алексей', 'Иванович', 3);

CREATE TABLE models (
    model_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    manufacturer VARCHAR(100),
    composition TEXT,
    base_price NUMERIC(10, 2) NOT NULL CHECK (base_price >= 0),
    image_path VARCHAR(255)
);

INSERT INTO models (name, category, manufacturer, composition, base_price, image_path) VALUES
('Road 125', 'Дорожные мотоциклы', 'Два колеса', 'Стальная рама; бензиновый двигатель; резиновые шины', 119000.00, 'IMG_12_001.png'),
('Road 150', 'Дорожные мотоциклы', 'МотоЛайн', 'Стальная рама; бензиновый двигатель; резиновые шины', 136000.00, 'IMG_12_002.png'),
('Trail 150', 'Мотоциклы эндуро', 'Два колеса', 'Стальная рама; подвеска увеличенного хода; внедорожные шины', 159000.00, 'IMG_12_017.png'),
('Scoot 50', 'Скутеры', 'Два колеса', 'Стальная рама; бензиновый двигатель; пластиковый корпус', 79000.00, 'IMG_12_025.png');

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(model_id) ON DELETE CASCADE,
    variant_id INTEGER,
    quantity INTEGER NOT NULL CHECK (quantity >= 0)
);

INSERT INTO stock_items (model_id, variant_id, quantity) VALUES
(1, 1, 10),
(1, 2, 5),
(2, 1, 2),
(2, 2, 8),
(3, 1, 0),
(3, 2, 4),
(4, 1, 1),
(4, 2, 15);

CREATE TABLE statuses (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50) UNIQUE
);

INSERT INTO statuses (status_name) VALUES 
('Новый'), 
('Подтверждён');

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(user_id),
    status_id INTEGER REFERENCES statuses(status_id)
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    stock_item_id INTEGER REFERENCES stock_items(stock_item_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);