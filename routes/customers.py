
"""Керування клієнтами магазину."""
import re
import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth import admin_required
from models import get_db

customers_bp = Blueprint(
    'customers',
    __name__,
    url_prefix='/admin/customers'
)


def normalize_phone(raw):
    """Залишає в номері телефону лише цифри."""
    return re.sub(r'\D', '', raw or '')


def get_or_create_customer(db, full_name, phone, address=None,
                           email=None, notes=None):
    """Знаходить клієнта за телефоном або створює нового."""
    clean_phone = normalize_phone(phone)
    name = (full_name or '').strip()

    if not name or len(clean_phone) < 9:
        return None

    customer = db.execute(
        'SELECT id FROM customers WHERE phone = ?',
        (clean_phone,)
    ).fetchone()

    if customer:
        db.execute(
            """
            UPDATE customers
            SET full_name = ?,
                address = COALESCE(NULLIF(?, ''), address),
                email = COALESCE(NULLIF(?, ''), email)
            WHERE id = ?
            """,
            (name, (address or '').strip(),
             (email or '').strip(), customer['id'])
        )
        return customer['id']

    cursor = db.execute(
        """
        INSERT INTO customers (full_name, phone, email, address, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            clean_phone,
            (email or '').strip() or None,
            (address or '').strip() or None,
            (notes or '').strip() or None
        )
    )
    return cursor.lastrowid


@customers_bp.route('/')
@admin_required
def customers_list():
    db = get_db()
    query = (request.args.get('q') or '').strip()

    if query:
        like = f'%{query}%'
        customers = db.execute(
            """
            SELECT * FROM customers
            WHERE full_name LIKE ?
               OR phone LIKE ?
               OR COALESCE(email, '') LIKE ?
            ORDER BY id DESC
            """,
            (like, like, like)
        ).fetchall()
    else:
        customers = db.execute(
            'SELECT * FROM customers ORDER BY id DESC'
        ).fetchall()

    return render_template(
        'admin/customers.html',
        customers=customers,
        query=query
    )


@customers_bp.route('/add', methods=['POST'])
@admin_required
def add_customer():
    full_name = (request.form.get('full_name') or '').strip()
    phone = normalize_phone(request.form.get('phone'))
    email = (request.form.get('email') or '').strip() or None
    address = (request.form.get('address') or '').strip() or None
    notes = (request.form.get('notes') or '').strip() or None

    if not full_name or len(phone) < 9:
        flash("Вкажіть ім'я та коректний номер телефону.", 'error')
        return redirect(url_for('customers.customers_list'))

    db = get_db()

    try:
        db.execute(
            """
            INSERT INTO customers
                (full_name, phone, email, address, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, phone, email, address, notes)
        )
        db.commit()
        flash('Клієнта успішно додано.', 'success')
    except sqlite3.IntegrityError:
        flash('Клієнт із таким номером телефону вже існує.', 'error')

    return redirect(url_for('customers.customers_list'))


@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@admin_required
def delete_customer(customer_id):
    db = get_db()
    db.execute(
        'DELETE FROM customers WHERE id = ?',
        (customer_id,)
    )
    db.commit()

    flash('Клієнта видалено.', 'success')
    return redirect(url_for('customers.customers_list'))
