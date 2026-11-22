"""API v2: товари у новому форматі. Файл учасника A (рівень 3, версіонування)."""
from flask import Blueprint, jsonify

from models import get_db
from routes.api_core import json_error

api_v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')


@api_v2_bp.route('/products', methods=['GET'])
def list_products_v2():
    """Товари, версія 2: поля перейменовано, додано наявність.
    ---
    tags: [Версія 2]
    responses:
      200:
        description: Список товарів у форматі v2
    """
    rows = get_db().execute(
        'SELECT id, name, price, stock FROM products WHERE is_active = 1 ORDER BY id'
    ).fetchall()
    items = [
        {
            'id': r['id'],
            'title': r['name'],
            'price_uah': r['price'],
            'in_stock': r['stock'] > 0,
        }
        for r in rows
    ]
    return jsonify({'data': items, 'meta': {'total': len(items), 'version': 'v2'}}), 200