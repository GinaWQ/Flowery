
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    address TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

INSERT OR IGNORE INTO customers
    (id, full_name, phone, email, address, notes)
VALUES
    (1, 'Олена Коваленко', '+380501234567',
     'olena.kovalenko@example.com', 'м. Луцьк',
     'Постійна клієнтка'),
    (2, 'Максим Шевченко', '+380679876543',
     'maks.shevchenko@example.com', 'м. Луцьк',
     'Замовляє букети на свята');
