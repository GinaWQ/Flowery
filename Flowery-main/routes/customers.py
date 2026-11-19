"""Керування клієнтами та допоміжні функції для роботи з таблицею customers."""
import re
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import get_db

customers_bp = Blueprint('customers', __name__, url_prefix='/admin/customers')


def _require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Увійдіть в адмін-панель, щоб керувати клієнтами.', 'warning')
            return redirect(url_for('admin.login'))
        return view(*args, **kwargs)

    return wrapped


def normalize_phone(raw):
    """Повертає лише цифри з номера телефону."""
    return re.sub(r'\D', '', raw or '')


def get_or_create_customer(db, full_name, phone, address=None, email=None, notes=None):
    """Знаходить клієнта за телефоном або створює нового. Повертає id клієнта."""
    clean_phone = normalize_phone(phone)
    name = (full_name or '').strip()
    if not name or not clean_phone:
        return None

    row = db.execute(
        'SELECT id, full_name, address, email FROM customers WHERE phone = ?',
        (clean_phone,),
    ).fetchone()

    if row:
        updates = []
        params = []
        if address and not row['address']:
            updates.append('address = ?')
            params.append(address.strip())
        if email and not row['email']:
            updates.append('email = ?')
            params.append(email.strip())
        if name and row['full_name'] != name:
            updates.append('full_name = ?')
            params.append(name)
        if updates:
            params.append(row['id'])
            db.execute(f"UPDATE customers SET {', '.join(updates)} WHERE id = ?", params)
        return row['id']

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
            (notes or '').strip() or None,
        ),
    )
    return cursor.lastrowid


@customers_bp.route('/')
@_require_admin
def customers_list():
    db = get_db()
    query = (request.args.get('q') or '').strip()
    if query:
        like = f'%{query}%'
        customers = db.execute(
            """
            SELECT * FROM customers
            WHERE full_name LIKE ? OR phone LIKE ? OR COALESCE(email, '') LIKE ?
            ORDER BY id DESC
            """,
            (like, like, like),
        ).fetchall()
    else:
        customers = db.execute('SELECT * FROM customers ORDER BY id DESC').fetchall()

    try:
        return render_template('admin/customers.html', customers=customers, query=query)
    except Exception:
        lines = [f"<li>#{c['id']} — {c['full_name']} ({c['phone']})</li>" for c in customers]
        return f"<h2>Клієнти</h2><ul>{''.join(lines)}</ul>"


@customers_bp.route('/add', methods=['POST'])
@_require_admin
def add_customer():
    full_name = (request.form.get('full_name') or '').strip()
    phone = normalize_phone(request.form.get('phone'))
    email = (request.form.get('email') or '').strip() or None
    address = (request.form.get('address') or '').strip() or None
    notes = (request.form.get('notes') or '').strip() or None

    if not full_name or len(phone) < 9:
        flash("Вкажіть коректне ім'я та номер телефону клієнта.", 'error')
        return redirect(url_for('customers.customers_list'))

    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO customers (full_name, phone, email, address, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, phone, email, address, notes),
        )
        db.commit()
        flash('Клієнта додано.', 'success')
    except Exception:
        flash('Клієнт з таким телефоном уже існує.', 'error')
    return redirect(url_for('customers.customers_list'))


@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@_require_admin
def delete_customer(customer_id):
    db = get_db()
    db.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    db.commit()
    flash('Запис клієнта видалено.', 'success')
    return redirect(url_for('customers.customers_list'))