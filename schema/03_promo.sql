
CREATE TABLE IF NOT EXISTS promo_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    discount_percent INTEGER NOT NULL
        CHECK (discount_percent > 0 AND discount_percent <= 100),
    min_order_amount REAL NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    expires_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

INSERT OR IGNORE INTO promo_codes
    (id, code, discount_percent, min_order_amount, is_active, expires_at)
VALUES
    (1, 'FLOWER10', 10, 500, 1, '2026-12-31'),
    (2, 'SPRING15', 15, 1000, 1, '2026-12-31');
