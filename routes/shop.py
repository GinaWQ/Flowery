"""Каталог, кошик і оформлення замовлень."""
from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from models import get_db

MAX_QUANTITY = 99
shop_bp = Blueprint('shop', __name__)


def get_popular(limit=3):
    """Повертає активні товари для головної сторінки."""
    limit = max(1, min(int(limit), 20))
    return get_db().execute(
        'SELECT id, name, category, description, emoji, price '
        'FROM products WHERE is_active = 1 ORDER BY id DESC LIMIT ?',
        (limit,),
    ).fetchall()


@shop_bp.route('/catalog')
def catalog():
    products = get_db().execute(
        'SELECT id, name, category, description, emoji, price '
        'FROM products WHERE is_active = 1 ORDER BY category, name'
    ).fetchall()
    return render_template('catalog.html', products=products)


def _cart_lines():
    """Перевіряє вміст кошика й додає до товарів кількість і суму."""
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    products = get_db().execute(
        'SELECT id, name, category, description, emoji, price '
        'FROM products WHERE is_active = 1'
    ).fetchall()
    products_by_id = {str(product['id']): product for product in products}

    lines = []
    clean_cart = {}
    for raw_id, raw_quantity in cart.items():
        try:
            product_id = str(int(raw_id))
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            continue

        product = products_by_id.get(product_id)
        if product is None or quantity <= 0:
            continue

        quantity = min(quantity, MAX_QUANTITY)
        clean_cart[product_id] = quantity
        line = dict(product)
        line['quantity'] = quantity
        line['line_total'] = round(float(product['price']) * quantity, 2)
        lines.append(line)

    session['cart'] = clean_cart
    lines.sort(key=lambda line: line['name'])
    total = round(sum(line['line_total'] for line in lines), 2)
    return lines, total


@shop_bp.route('/cart')
def cart():
    cart_items, total = _cart_lines()
    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total,
        added=request.args.get('added'),
        empty=request.args.get('empty'),
    )


@shop_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    product = get_db().execute(
        'SELECT id FROM products WHERE id = ? AND is_active = 1',
        (product_id,),
    ).fetchone()
    if product is None:
        abort(404)

    quantity = request.form.get('quantity', default=1, type=int)
    quantity = max(1, min(quantity or 1, MAX_QUANTITY))
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    key = str(product_id)
    cart[key] = min(int(cart.get(key, 0)) + quantity, MAX_QUANTITY)
    session['cart'] = cart
    return redirect(url_for('shop.cart', added=1))


@shop_bp.route('/cart/update/<int:product_id>', methods=['POST'])
def cart_update(product_id):
    quantity = request.form.get('quantity', type=int)
    if quantity is None:
        abort(400)

    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    key = str(product_id)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = min(quantity, MAX_QUANTITY)
    session['cart'] = cart
    return redirect(url_for('shop.cart'))


@shop_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    cart = session.get('cart', {})
    if isinstance(cart, dict):
        cart.pop(str(product_id), None)
        session['cart'] = cart
    return redirect(url_for('shop.cart'))


@shop_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items, total = _cart_lines()
    if not cart_items:
        return redirect(url_for('shop.cart', empty=1))

    values = {'name': '', 'phone': '', 'email': '', 'address': ''}
    errors = []

    if request.method == 'POST':
        values = {
            'name': request.form.get('name', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'email': request.form.get('email', '').strip(),
            'address': request.form.get('address', '').strip(),
        }

        if len(values['name']) < 2 or len(values['name']) > 100:
            errors.append("Вкажіть ім'я (від 2 до 100 символів).")
        if len(values['phone']) < 7 or len(values['phone']) > 30:
            errors.append('Вкажіть номер телефону.')
        if len(values['address']) < 5 or len(values['address']) > 250:
            errors.append('Вкажіть адресу доставки (від 5 до 250 символів).')
        if len(values['email']) > 254:
            errors.append('Email занадто довгий.')

        db = get_db()
        current_items = []
        if not errors:
            for line in cart_items:
                product = db.execute(
                    'SELECT id, name, price FROM products '
                    'WHERE id = ? AND is_active = 1',
                    (line['id'],),
                ).fetchone()
                if product is None:
                    errors.append('Один із товарів більше недоступний. Оновіть кошик.')
                    break
                current_items.append((product, line['quantity']))

        if not errors:
            order_total = round(
                sum(float(product['price']) * quantity
                    for product, quantity in current_items),
                2,
            )
            with db:
                cursor = db.execute(
                    'INSERT INTO orders '
                    '(customer_name, phone, email, delivery_address, total) '
                    'VALUES (?, ?, ?, ?, ?)',
                    (values['name'], values['phone'], values['email'] or None,
                     values['address'], order_total),
                )
                order_id = cursor.lastrowid
                db.executemany(
                    'INSERT INTO order_items '
                    '(order_id, product_id, product_name, unit_price, quantity) '
                    'VALUES (?, ?, ?, ?, ?)',
                    [
                        (order_id, product['id'], product['name'],
                         product['price'], quantity)
                        for product, quantity in current_items
                    ],
                )

            session.pop('cart', None)
            return render_template(
                'order_success.html',
                order_id=order_id,
                customer_name=values['name'],
                total=order_total,
            )

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        total=total,
        values=values,
        errors=errors,
    )