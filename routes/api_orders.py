"""API замовлень: список, деталі, зміна статусу. Файл учасника B."""
from flask import Blueprint, jsonify, request

from models import get_db
from routes.api_core import json_error
from services import ORDER_STATUSES, set_order_status

api_orders_bp = Blueprint('api_orders', __name__, url_prefix='/api/v1')

ORDER_COLUMNS = 'id, customer_name, phone, status, subtotal, discount, total, created_at'


def _order_with_items(db, oid):
    order = db.execute(f'SELECT {ORDER_COLUMNS} FROM orders WHERE id = ?', (oid,)).fetchone()
    if order is None:
        return None
    items = db.execute(
        'SELECT product_name, price, quantity FROM order_items WHERE order_id = ?', (oid,)
    ).fetchall()
    data = dict(order)
    data['items'] = [dict(i) for i in items]
    return data


@api_orders_bp.route('/orders', methods=['GET'])
def list_orders():
    """Список замовлень (новіші спочатку).
    ---
    tags: [Замовлення]
    parameters:
      - name: status
        in: query
        type: string
        required: false
        enum: [new, paid, assembling, delivering, done, cancelled]
    responses:
      200:
        description: Список замовлень
      400:
        description: Невідомий статус
    """
    status = request.args.get('status')
    db = get_db()
    if status:
        if status not in ORDER_STATUSES:
            return json_error('Невідомий статус: ' + status, 400)
        rows = db.execute(
            f'SELECT {ORDER_COLUMNS} FROM orders WHERE status = ? ORDER BY id DESC', (status,)
        ).fetchall()
    else:
        rows = db.execute(f'SELECT {ORDER_COLUMNS} FROM orders ORDER BY id DESC').fetchall()
    return jsonify({'orders': [dict(r) for r in rows], 'count': len(rows)}), 200


@api_orders_bp.route('/orders/<int:oid>', methods=['GET'])
def get_order(oid):
    """Замовлення з переліком товарів.
    ---
    tags: [Замовлення]
    parameters:
      - name: oid
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Замовлення і його товари
      404:
        description: Замовлення не знайдено
    """
    data = _order_with_items(get_db(), oid)
    if data is None:
        return json_error('Замовлення не знайдено', 404)
    return jsonify(data), 200


@api_orders_bp.route('/orders/<int:oid>', methods=['PATCH'])
def update_order_status(oid):
    """Змінити статус замовлення. При cancelled товари повертаються на склад.
    ---
    tags: [Замовлення]
    parameters:
      - name: oid
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [status]
          properties:
            status:
              type: string
              enum: [new, paid, assembling, delivering, done, cancelled]
              example: paid
    responses:
      200:
        description: Оновлене замовлення
      400:
        description: Невідомий або відсутній статус
      404:
        description: Замовлення не знайдено
    """
    payload = request.get_json(silent=True)
    status = payload.get('status') if isinstance(payload, dict) else None
    if status not in ORDER_STATUSES:
        return json_error('status має бути одним із: ' + ', '.join(ORDER_STATUSES), 400)

    db = get_db()
    if not set_order_status(db, oid, status):
        return json_error('Замовлення не знайдено', 404)
    db.commit()
    return jsonify(_order_with_items(db, oid)), 200
