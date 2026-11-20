"""API товарів: CRUD (GET, POST, PUT, PATCH, DELETE). Файл учасника B."""
import sqlite3

from flask import Blueprint, jsonify, request

from models import get_db
from routes.api_core import json_error

api_products_bp = Blueprint('api_products', __name__, url_prefix='/api/v1')

PRODUCT_COLUMNS = 'id, name, category, price, emoji, description, stock, is_active'


def _validate(data, partial=False):
    """Перевіряє тіло запиту. Повертає (очищені_дані, список_помилок).

    partial=False — для POST і PUT: обовʼязкові name, category, price.
    partial=True  — для PATCH: передані поля перевіряються, решта ігнорується.
    """
    if not isinstance(data, dict):
        return None, ['Тіло запиту має бути JSON-обʼєктом']

    errors, clean = [], {}

    if not partial:
        missing = [f for f in ('name', 'category', 'price') if f not in data]
        if missing:
            errors.append('Відсутні поля: ' + ', '.join(missing))

    for field in ('name', 'category'):
        if field in data:
            value = data[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f'{field}: потрібен непорожній рядок')
            else:
                clean[field] = value.strip()

    if 'price' in data:
        price = data['price']
        if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
            errors.append('price: ціле число більше 0')
        else:
            clean['price'] = price

    if 'stock' in data:
        stock = data['stock']
        if not isinstance(stock, int) or isinstance(stock, bool) or stock < 0:
            errors.append('stock: ціле число не менше 0')
        else:
            clean['stock'] = stock

    if 'emoji' in data:
        if not isinstance(data['emoji'], str) or not data['emoji'].strip():
            errors.append('emoji: непорожній рядок')
        else:
            clean['emoji'] = data['emoji'].strip()

    if 'description' in data:
        if data['description'] is not None and not isinstance(data['description'], str):
            errors.append('description: рядок або null')
        else:
            clean['description'] = data['description']

    return clean, errors


def _get_product(pid):
    row = get_db().execute(
        f'SELECT {PRODUCT_COLUMNS} FROM products WHERE id = ?', (pid,)
    ).fetchone()
    return dict(row) if row else None


@api_products_bp.route('/products', methods=['GET'])
def list_products():
    """Список активних товарів.
    ---
    tags: [Товари]
    parameters:
      - name: category
        in: query
        type: string
        required: false
        description: Фільтр за категорією, наприклад Букети
    responses:
      200:
        description: Список товарів
        schema:
          type: object
          properties:
            products:
              type: array
              items:
                type: object
            count:
              type: integer
    """
    category = request.args.get('category')
    db = get_db()
    if category:
        rows = db.execute(
            f'SELECT {PRODUCT_COLUMNS} FROM products WHERE is_active = 1 AND category = ? ORDER BY id',
            (category,),
        ).fetchall()
    else:
        rows = db.execute(
            f'SELECT {PRODUCT_COLUMNS} FROM products WHERE is_active = 1 ORDER BY id'
        ).fetchall()
    return jsonify({'products': [dict(r) for r in rows], 'count': len(rows)}), 200


@api_products_bp.route('/products/<int:pid>', methods=['GET'])
def get_product(pid):
    """Один товар за ID.
    ---
    tags: [Товари]
    parameters:
      - name: pid
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Дані товару
      404:
        description: Товар не знайдено
    """
    product = _get_product(pid)
    if product is None or not product['is_active']:
        return json_error('Товар не знайдено', 404)
    return jsonify(product), 200


@api_products_bp.route('/products', methods=['POST'])
def create_product():
    """Створити товар.
    ---
    tags: [Товари]
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [name, category, price]
          properties:
            name: {type: string, example: Білі піони}
            category: {type: string, example: Букети}
            price: {type: integer, example: 890}
            emoji: {type: string, example: "🌸"}
            description: {type: string, example: Двадцять білих піонів у крафтовому пакуванні}
            stock: {type: integer, example: 6}
    responses:
      201:
        description: Товар створено (у заголовку Location — адреса нового ресурсу)
      400:
        description: Помилка валідації
      409:
        description: Товар із такою назвою вже існує
    """
    clean, errors = _validate(request.get_json(silent=True))
    if errors:
        return json_error('; '.join(errors), 400)

    db = get_db()
    try:
        cur = db.execute(
            'INSERT INTO products (name, category, price, emoji, description, stock) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (clean['name'], clean['category'], clean['price'],
             clean.get('emoji', '💐'), clean.get('description'), clean.get('stock', 10)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return json_error('Товар з такою назвою вже існує', 409)

    new_id = cur.lastrowid
    return jsonify(_get_product(new_id)), 201, {'Location': f'/api/v1/products/{new_id}'}


@api_products_bp.route('/products/<int:pid>', methods=['PUT'])
def replace_product(pid):
    """Повністю замінити товар (усі обовʼязкові поля).
    ---
    tags: [Товари]
    parameters:
      - name: pid
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [name, category, price]
          properties:
            name: {type: string}
            category: {type: string}
            price: {type: integer}
            emoji: {type: string}
            description: {type: string}
            stock: {type: integer}
    responses:
      200:
        description: Оновлений товар
      400:
        description: Помилка валідації
      404:
        description: Товар не знайдено
      409:
        description: Назва вже зайнята
    """
    if _get_product(pid) is None:
        return json_error('Товар не знайдено', 404)

    clean, errors = _validate(request.get_json(silent=True))
    if errors:
        return json_error('; '.join(errors), 400)

    db = get_db()
    try:
        db.execute(
            'UPDATE products SET name=?, category=?, price=?, emoji=?, description=?, stock=? '
            'WHERE id=?',
            (clean['name'], clean['category'], clean['price'],
             clean.get('emoji', '💐'), clean.get('description'), clean.get('stock', 10), pid),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return json_error('Товар з такою назвою вже існує', 409)
    return jsonify(_get_product(pid)), 200


@api_products_bp.route('/products/<int:pid>', methods=['PATCH'])
def update_product(pid):
    """Частково змінити товар (наприклад, лише ціну або залишок).
    ---
    tags: [Товари]
    parameters:
      - name: pid
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            price: {type: integer, example: 750}
            stock: {type: integer, example: 12}
    responses:
      200:
        description: Оновлений товар
      400:
        description: Помилка валідації або порожнє тіло
      404:
        description: Товар не знайдено
    """
    if _get_product(pid) is None:
        return json_error('Товар не знайдено', 404)

    clean, errors = _validate(request.get_json(silent=True), partial=True)
    if errors:
        return json_error('; '.join(errors), 400)
    if not clean:
        return json_error('Немає полів для оновлення', 400)

    assignments = ', '.join(f'{column} = ?' for column in clean)
    db = get_db()
    try:
        db.execute(f'UPDATE products SET {assignments} WHERE id = ?', (*clean.values(), pid))
        db.commit()
    except sqlite3.IntegrityError:
        return json_error('Товар з такою назвою вже існує', 409)
    return jsonify(_get_product(pid)), 200


@api_products_bp.route('/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    """Видалити товар.
    ---
    tags: [Товари]
    parameters:
      - name: pid
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Товар видалено
      404:
        description: Товар не знайдено
    """
    db = get_db()
    cur = db.execute('DELETE FROM products WHERE id = ?', (pid,))
    db.commit()
    if cur.rowcount == 0:
        return json_error('Товар не знайдено', 404)
    return '', 204
```[cite: 1]

3. Збережи (`Ctrl + S`), закрий Блокнот, перевір синтаксис і закоміть:
```powershell
python -m py_compile routes\api_products.py
git add routes\api_products.py
git commit -m "feat(api): CRUD товарів: GET, POST, PUT, PATCH, DELETE з валідацією"
```[cite: 1]

Після цього відкривай `notepad routes\api_orders.py` і зроби те саме для замовлень[cite: 1].