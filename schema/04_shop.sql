   CREATE TABLE IF NOT EXISTS products (
       id          INTEGER PRIMARY KEY AUTOINCREMENT,
       name        TEXT    NOT NULL UNIQUE,
       category    TEXT    NOT NULL,
       price       INTEGER NOT NULL CHECK (price > 0),
       emoji       TEXT    NOT NULL DEFAULT '💐',
       description TEXT,
       stock       INTEGER NOT NULL DEFAULT 10 CHECK (stock >= 0),
       is_active   INTEGER NOT NULL DEFAULT 1
   );