
"""REST API для керування промокодами Flowery."""

import sqlite3
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app

api_promo_bp = Blueprint(
    'api_promo', __name__, url_prefix='/api/v1'
)


def get_db():
    """Підключення до бази даних."""
    db = sqlite3.connect(current_app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def validate_promo(data):
    """Перевірка даних промокоду."""
    code = data.get('code')
    discount = data.get('discount_percent')
    min_amount = data.get('min_order_amount', 0)
    is_active = data.get('is_active', 1)
    expires_at = data.get('expires_at')

    if not isinstance(code, str) or not code.strip():
        return None, 'Вкажіть код промокоду'

    if (
        not isinstance(discount, int)
        or isinstance(discount, bool)
        or not 1 <= discount <= 100
    ):
        return None, 'Знижка має бути цілим числом від 1 до 100'

    if (
        not isinstance(min_amount, (int, float))
        or isinstance(min_amount, bool)
        or min_amount < 0
    ):
        return None, 'Мінімальна сума не може бути від’ємною'

    if is_active not in (0, 1, True, False):
        return None, 'Поле is_active має бути 0 або 1'

    if expires_at is not None:
        if not isinstance(expires_at, str):
            return None, 'Некоректна дата завершення'

        try:
            datetime.strptime(expires_at, '%Y-%m-%d')
        except ValueError:
            return None, 'Дата має бути у форматі YYYY-MM-DD'

    return {
        'code': code.strip().upper(),
        'discount_percent': discount,
        'min_order_amount': min_amount,
        'is_active': int(is_active),
        'expires_at': expires_at
    }, None


@api_promo_bp.route('/promo', methods=['GET'])
def get_promos():
    """
    Отримати список усіх промокодів.
    ---
    tags:
      - Промокоди
    responses:
      200:
        description: Список промокодів
    """
    db = get_db()
    promos = db.execute(
        'SELECT * FROM promo_codes ORDER BY id'
    ).fetchall()
    db.close()

    return jsonify([dict(promo) for promo in promos]), 200


@api_promo_bp.route('/promo/<int:promo_id>', methods=['GET'])
def get_promo(promo_id):
    """
    Отримати промокод за ID.
    ---
    tags:
      - Промокоди
    parameters:
      - name: promo_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Промокод знайдено
      404:
        description: Промокод не знайдено
    """
    db = get_db()
    promo = db.execute(
        'SELECT * FROM promo_codes WHERE id = ?',
        (promo_id,)
    ).fetchone()
    db.close()

    if promo is None:
        return jsonify({'error': 'Промокод не знайдено'}), 404

    return jsonify(dict(promo)), 200


@api_promo_bp.route('/promo', methods=['POST'])
def create_promo():
    """
    Створити новий промокод.
    ---
    tags:
      - Промокоди
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - code
            - discount_percent
          properties:
            code:
              type: string
              example: TEST20
            discount_percent:
              type: integer
              example: 20
            min_order_amount:
              type: number
              example: 500
            is_active:
              type: integer
              example: 1
            expires_at:
              type: string
              example: 2026-12-31
    responses:
      201:
        description: Промокод створено
      400:
        description: Помилка перевірки даних
      409:
        description: Такий промокод уже існує
    """
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Потрібно передати JSON'}), 400

    promo, error = validate_promo(data)

    if error:
        return jsonify({'error': error}), 400

    db = get_db()

    try:
        cursor = db.execute(
            '''INSERT INTO promo_codes
               (code, discount_percent, min_order_amount,
                is_active, expires_at)
               VALUES (?, ?, ?, ?, ?)''',
            (
                promo['code'],
                promo['discount_percent'],
                promo['min_order_amount'],
                promo['is_active'],
                promo['expires_at']
            )
        )
        db.commit()

        created = db.execute(
            'SELECT * FROM promo_codes WHERE id = ?',
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify(dict(created)), 201

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({'error': 'Такий промокод уже існує'}), 409

    finally:
        db.close()


@api_promo_bp.route('/promo/<int:promo_id>', methods=['PATCH'])
def update_promo(promo_id):
    """
    Частково оновити промокод.
    ---
    tags:
      - Промокоди
    consumes:
      - application/json
    parameters:
      - name: promo_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            code:
              type: string
              example: NEWCODE
            discount_percent:
              type: integer
              example: 25
            min_order_amount:
              type: number
              example: 700
            is_active:
              type: integer
              example: 1
            expires_at:
              type: string
              example: 2026-12-31
    responses:
      200:
        description: Промокод оновлено
      400:
        description: Некоректні дані
      404:
        description: Промокод не знайдено
      409:
        description: Такий промокод уже існує
    """
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            'error': 'Потрібно передати JSON з даними'
        }), 400

    db = get_db()

    try:
        existing = db.execute(
            'SELECT * FROM promo_codes WHERE id = ?',
            (promo_id,)
        ).fetchone()

        if existing is None:
            return jsonify({'error': 'Промокод не знайдено'}), 404

        allowed = {
            'code', 'discount_percent', 'min_order_amount',
            'is_active', 'expires_at'
        }

        if not set(data).issubset(allowed):
            return jsonify({'error': 'Передано невідоме поле'}), 400

        updated_data = dict(existing)
        updated_data.update(data)

        promo, error = validate_promo(updated_data)

        if error:
            return jsonify({'error': error}), 400

        db.execute(
            '''UPDATE promo_codes
               SET code = ?, discount_percent = ?,
                   min_order_amount = ?, is_active = ?,
                   expires_at = ?
               WHERE id = ?''',
            (
                promo['code'],
                promo['discount_percent'],
                promo['min_order_amount'],
                promo['is_active'],
                promo['expires_at'],
                promo_id
            )
        )
        db.commit()

        updated = db.execute(
            'SELECT * FROM promo_codes WHERE id = ?',
            (promo_id,)
        ).fetchone()

        return jsonify(dict(updated)), 200

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({'error': 'Такий промокод уже існує'}), 409

    finally:
        db.close()


@api_promo_bp.route('/promo/<int:promo_id>', methods=['DELETE'])
def delete_promo(promo_id):
    """
    Видалити промокод.
    ---
    tags:
      - Промокоди
    parameters:
      - name: promo_id
        in: path
        required: true
        type: integer
    responses:
      204:
        description: Промокод видалено
      404:
        description: Промокод не знайдено
    """
    db = get_db()

    try:
        cursor = db.execute(
            'DELETE FROM promo_codes WHERE id = ?',
            (promo_id,)
        )
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Промокод не знайдено'}), 404

        return '', 204

    finally:
        db.close()

@api_promo_bp.route('/promo/validate', methods=['POST'])
def check_promo():
    """Перевірити промокод і розрахувати знижку."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Потрібно передати JSON'}), 400

    code = data.get('code')
    subtotal = data.get('subtotal')

    if not isinstance(code, str) or not code.strip():
        return jsonify({'error': 'Вкажіть промокод'}), 400

    if (
        not isinstance(subtotal, (int, float))
        or isinstance(subtotal, bool)
        or not (0 <= subtotal < float('inf'))
    ):
        return jsonify({'error': 'Некоректна сума замовлення'}), 400

    db = get_db()

    try:
        promo = db.execute(
            'SELECT * FROM promo_codes WHERE code = ?',
            (code.strip().upper(),)
        ).fetchone()

        if promo is None:
            return jsonify({'error': 'Промокод не знайдено'}), 404

        if not promo['is_active']:
            return jsonify({'error': 'Промокод неактивний'}), 400

        if subtotal < promo['min_order_amount']:
            return jsonify({
                'error': 'Не досягнуто мінімальної суми замовлення'
            }), 400

        if promo['expires_at']:
            expiry_date = datetime.strptime(
                promo['expires_at'], '%Y-%m-%d'
            ).date()

            if expiry_date < datetime.now().date():
                return jsonify({'error': 'Термін дії промокоду завершився'}), 400

        discount_percent = promo['discount_percent']
        discount_amount = round(
            subtotal * discount_percent / 100, 2
        )
        total = round(subtotal - discount_amount, 2)

        return jsonify({
            'valid': True,
            'code': promo['code'],
            'discount_percent': discount_percent,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'total': total
        }), 200

    finally:
        db.close()

