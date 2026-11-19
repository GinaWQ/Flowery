"""Адмін-керування товарами та замовленнями."""
import math
import sqlite3

from flask import Blueprint, abort, redirect, render_template, request, url_for

from auth import admin_required
from models import get_db

admin_shop_bp = Blueprint('admin_shop', __name__, url_prefix='/admin')

STATUS_LABELS = {
    'new': 'Нове',
    'confirmed': 'Підтверджене',
    'in_delivery': 'У доставці',
    'completed': 'Виконане',
    'cancelled': 'Скасоване',
}


def _product_values(form):
    values = {
        'name': form.get('name', '').strip(),
        'category': form.get('category', '').strip(),
        'description': form.get('description', '').strip(),
        'emoji': form.get('emoji', '').strip() or '💐',
        'price': form.get('price', '').strip(),
    }
    errors = []

    if not values['name'] or len(values['name']) > 100:
        errors.append('Назва товару обов’язкова (до 100 символів).')
    if not values['category'] or len(values['category']) > 60:
        errors.append('Вкажіть категорію (до 60 символів).')
    if len(values['description']) > 1000:
        errors.append('Опис має бути не довший за 1000 символів.')
    if len(values['emoji']) > 12:
        errors.append('Позначення товару має бути не довшим за 12 символів.')

    try:
        price = float(values['price'])
        if not math.isfinite(price) or price <= 0:
            raise ValueError
    except ValueError:
        errors.append('Ціна має бути числом більшим за нуль.')
        price = 0

    return values, errors, price


@admin_shop_bp.route('/products')
@admin_required
def products():
    rows = get_db().execute(
        'SELECT id, name, category, price, is_active '
        'FROM products ORDER BY is_active DESC, name'
    ).fetchall()
    return render_template('admin/products.html', products=rows)


@admin_shop_bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
def product_new():
    if request.method == 'POST':
        values, errors, price = _product_values(request.form)
        if not errors:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO products (name, category, description, emoji, price) '
                    'VALUES (?, ?, ?, ?, ?)',
                    (values['name'], values['category'], values['description'],
                     values['emoji'], price),
                )
                db.commit()
                return redirect(url_for('admin_shop.products', saved=1))
            except sqlite3.IntegrityError as error:
                # Показуємо зрозумілу помилку для назви товару, що вже існує.
                if 'UNIQUE' in str(error).upper():
                    errors.append('Товар із такою назвою вже існує.')
                else:
                    raise
    else:
        values = {
            'name': '',
            'category': 'Букети',
            'description': '',
            'emoji': '💐',
            'price': '',
        }
        errors = []

    return render_template(
        'admin/product_form.html',
        values=values,
        errors=errors,
        page_title='Додати товар',
    )


@admin_shop_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def product_edit(product_id):
    db = get_db()
    product = db.execute(
        'SELECT * FROM products WHERE id = ?', (product_id,)
    ).fetchone()
    if product is None:
        abort(404)

    if request.method == 'POST':
        values, errors, price = _product_values(request.form)
        if not errors:
            try:
                db.execute(
                    'UPDATE products SET name = ?, category = ?, description = ?, '
                    'emoji = ?, price = ? WHERE id = ?',
                    (values['name'], values['category'], values['description'],
                     values['emoji'], price, product_id),
                )
                db.commit()
                return redirect(url_for('admin_shop.products', saved=1))
            except sqlite3.IntegrityError as error:
                if 'UNIQUE' in str(error).upper():
                    errors.append('Товар із такою назвою вже існує.')
                else:
                    raise
    else:
        values = {
            'name': product['name'],
            'category': product['category'],
            'description': product['description'],
            'emoji': product['emoji'],
            'price': product['price'],
        }
        errors = []

    return render_template(
        'admin/product_form.html',
        values=values,
        errors=errors,
        page_title='Редагувати товар',
    )


@admin_shop_bp.route('/products/<int:product_id>/toggle', methods=['POST'])
@admin_required
def product_toggle(product_id):
    db = get_db()
    cursor = db.execute(
        'UPDATE products SET is_active = 1 - is_active WHERE id = ?',
        (product_id,),
    )
    if cursor.rowcount == 0:
        abort(404)
    db.commit()
    return redirect(url_for('admin_shop.products'))


@admin_shop_bp.route('/orders')
@admin_required
def orders():
    rows = get_db().execute(
        'SELECT id, customer_name, phone, total, status, created_at '
        'FROM orders ORDER BY id DESC'
    ).fetchall()
    return render_template(
        'admin/orders.html',
        orders=rows,
        status_labels=STATUS_LABELS,
    )


@admin_shop_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    db = get_db()
    order = db.execute(
        'SELECT * FROM orders WHERE id = ?', (order_id,)
    ).fetchone()
    if order is None:
        abort(404)

    items = db.execute(
        'SELECT product_name, unit_price, quantity '
        'FROM order_items WHERE order_id = ? ORDER BY id',
        (order_id,),
    ).fetchall()
    return render_template(
        'admin/order_detail.html',
        order=order,
        items=items,
        statuses=STATUS_LABELS.items(),
        status_labels=STATUS_LABELS,
    )


@admin_shop_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def order_update_status(order_id):
    status = request.form.get('status', '')
    if status not in STATUS_LABELS:
        abort(400)

    db = get_db()
    cursor = db.execute(
        "UPDATE orders SET status = ?, updated_at = datetime('now', 'localtime') "
        'WHERE id = ?',
        (status, order_id),
    )
    if cursor.rowcount == 0:
        abort(404)
    db.commit()
    return redirect(url_for('admin_shop.order_detail', order_id=order_id))