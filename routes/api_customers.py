
"""REST API для керування клієнтами Flowery."""

import sqlite3

from flask import Blueprint, jsonify, request, current_app

api_customers_bp = Blueprint(
    'api_customers', __name__, url_prefix='/api/v1'
)


def get_db():
    """Підключення до бази даних."""
    db = sqlite3.connect(current_app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


@api_customers_bp.route('/customers', methods=['GET'])
def get_customers():
    """
    Отримати список клієнтів.
    ---
    tags:
      - Клієнти
    responses:
      200:
        description: Список усіх клієнтів
    """
    db = get_db()
    customers = db.execute(
        'SELECT * FROM customers ORDER BY id'
    ).fetchall()
    db.close()

    return jsonify([dict(c) for c in customers]), 200


@api_customers_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    Отримати клієнта за ID.
    ---
    tags:
      - Клієнти
    parameters:
      - name: customer_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Дані клієнта
      404:
        description: Клієнта не знайдено
    """
    db = get_db()
    customer = db.execute(
        'SELECT * FROM customers WHERE id = ?', (customer_id,)
    ).fetchone()
    db.close()

    if customer is None:
        return jsonify({'error': 'Клієнта не знайдено'}), 404

    return jsonify(dict(customer)), 200


@api_customers_bp.route('/customers', methods=['POST'])
def create_customer():
    """
    Додати нового клієнта.
    ---
    tags:
      - Клієнти
    parameters:
      - in: body
        name: customer
        required: true
        schema:
          type: object
          required:
            - full_name
            - phone
          properties:
            full_name:
              type: string
              example: Іван Петренко
            phone:
              type: string
              example: "+380991112233"
            email:
              type: string
              example: test@example.com
            address:
              type: string
              example: м. Луцьк
            notes:
              type: string
              example: Постійний клієнт
    responses:
      201:
        description: Клієнта створено
      400:
        description: Некоректні дані
      409:
        description: Номер телефону вже існує
    """
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Потрібно передати JSON'}), 400

    full_name = data.get('full_name')
    phone = data.get('phone')

    if not isinstance(full_name, str) or not full_name.strip():
        return jsonify({'error': 'Вкажіть ім’я клієнта'}), 400

    if not isinstance(phone, str) or len(
        ''.join(filter(str.isdigit, phone))
    ) < 9:
        return jsonify({'error': 'Некоректний номер телефону'}), 400

    db = get_db()

    try:
        cursor = db.execute(
            '''INSERT INTO customers
               (full_name, phone, email, address, notes)
               VALUES (?, ?, ?, ?, ?)''',
            (
                full_name.strip(), phone.strip(),
                data.get('email'), data.get('address'),
                data.get('notes')
            )
        )
        db.commit()

        customer = db.execute(
            'SELECT * FROM customers WHERE id = ?',
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify(dict(customer)), 201

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({'error': 'Такий номер телефону вже існує'}), 409

    finally:
        db.close()


@api_customers_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """
    Оновити дані клієнта.
    ---
    tags:
      - Клієнти
    parameters:
      - name: customer_id
        in: path
        type: integer
        required: true
      - in: body
        name: customer
        required: true
        schema:
          type: object
          required:
            - full_name
            - phone
          properties:
            full_name:
              type: string
            phone:
              type: string
            email:
              type: string
            address:
              type: string
            notes:
              type: string
    responses:
      200:
        description: Дані оновлено
      400:
        description: Некоректні дані
      404:
        description: Клієнта не знайдено
      409:
        description: Номер телефону вже існує
    """
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'error': 'Потрібно передати JSON'}), 400

    full_name = data.get('full_name')
    phone = data.get('phone')

    if not isinstance(full_name, str) or not full_name.strip():
        return jsonify({'error': 'Вкажіть ім’я клієнта'}), 400

    if not isinstance(phone, str) or len(
        ''.join(filter(str.isdigit, phone))
    ) < 9:
        return jsonify({'error': 'Некоректний номер телефону'}), 400

    db = get_db()

    try:
        existing = db.execute(
            'SELECT id FROM customers WHERE id = ?', (customer_id,)
        ).fetchone()

        if existing is None:
            return jsonify({'error': 'Клієнта не знайдено'}), 404

        db.execute(
            '''UPDATE customers
               SET full_name = ?, phone = ?, email = ?,
                   address = ?, notes = ?
               WHERE id = ?''',
            (
                full_name.strip(), phone.strip(),
                data.get('email'), data.get('address'),
                data.get('notes'), customer_id
            )
        )
        db.commit()

        customer = db.execute(
            'SELECT * FROM customers WHERE id = ?', (customer_id,)
        ).fetchone()

        return jsonify(dict(customer)), 200

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({'error': 'Такий номер телефону вже існує'}), 409

    finally:
        db.close()


@api_customers_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """
    Видалити клієнта.
    ---
    tags:
      - Клієнти
    parameters:
      - name: customer_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Клієнта видалено
      404:
        description: Клієнта не знайдено
    """
    db = get_db()

    try:
        cursor = db.execute(
            'DELETE FROM customers WHERE id = ?', (customer_id,)
        )
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Клієнта не знайдено'}), 404

        return '', 204

    finally:
        db.close()
