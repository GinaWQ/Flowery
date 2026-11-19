-- Товари квіткового магазину.
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    category    TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    emoji       TEXT    NOT NULL DEFAULT '💐',
    price       REAL    NOT NULL CHECK (price > 0),
    is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Замовлення зберігає контактні дані на момент оформлення.
CREATE TABLE IF NOT EXISTS orders (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name    TEXT    NOT NULL,
    phone            TEXT    NOT NULL,
    email            TEXT,
    delivery_address TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'new'
                             CHECK (status IN (
                                 'new', 'confirmed', 'in_delivery',
                                 'completed', 'cancelled'
                             )),
    total            REAL    NOT NULL DEFAULT 0 CHECK (total >= 0),
    created_at       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Зв’язувальна таблиця реалізує зв’язок багато-до-багатьох
-- між замовленнями й товарами та зберігає ціну на момент покупки.
CREATE TABLE IF NOT EXISTS order_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id     INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id   INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    product_name TEXT    NOT NULL,
    unit_price   REAL    NOT NULL CHECK (unit_price > 0),
    quantity     INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (order_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);

-- Початковий асортимент для демонстрації магазину.
INSERT OR IGNORE INTO products (name, category, description, emoji, price) VALUES
    ('Ніжний світанок', 'Букети', 'Ніжна композиція у рожевих відтінках.', '🌸', 650),
    ('Червона класика', 'Букети', 'Червоні троянди для яскравих почуттів.', '🌹', 900),
    ('Сонячний настрій', 'Букети', 'Жовті квіти, які дарують тепло.', '🌻', 480),
    ('Тюльпани у кошику', 'Композиції', 'Весняні тюльпани у святковому оформленні.', '🌷', 560),
    ('Лавандова мрія', 'Композиції', 'Ніжна композиція з лавандовими відтінками.', '💜', 720),
    ('Орхідея в горщику', 'Рослини', 'Квітуча орхідея для дому або подарунка.', '🪻', 750);