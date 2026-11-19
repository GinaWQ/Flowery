"""Робота з базою даних SQLite: з'єднання для запиту та створення таблиць.

Таблиці описані в SQL-файлах папки schema/. Ці файли виконуються у порядку
імен, тому кожна команда пише свій файл і не змінює чужі.
"""
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA_DIR = Path(__file__).parent / 'schema'


def get_db():
    """Повертає з'єднання для поточного запиту. Створюється один раз на запит."""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        # Рядки можна читати за назвою стовпця: row['name']
        g.db.row_factory = sqlite3.Row
        # SQLite за замовчуванням не перевіряє FOREIGN KEY, вмикаємо явно
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(exception=None):
    """Закриває з'єднання після завершення запиту (викликається Flask автоматично)."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Створює всі таблиці та заповнює стартові дані з файлів schema/*.sql."""
    db = sqlite3.connect(current_app.config['DATABASE'])
    try:
        for path in sorted(SCHEMA_DIR.glob('*.sql')):
            db.executescript(path.read_text(encoding='utf-8'))
    finally:
        db.close()