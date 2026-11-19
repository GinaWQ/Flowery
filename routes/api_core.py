"""Спільні елементи API: blueprint версії v1, хелпер помилок, індекс API."""
from flask import Blueprint, jsonify

api_bp = Blueprint('api_core', __name__, url_prefix='/api/v1')


def json_error(message, status):
    """Єдиний формат помилки для всього API: {"error": "текст"}."""
    return jsonify({'error': message}), status


@api_bp.route('/', methods=['GET'])
def api_index():
    """Довідка по API.
    ---
    tags: [Загальне]
    responses:
      200:
        description: Список ресурсів API
    """
    return jsonify({
        'name': 'Flowery API',
        'version': 'v1',
        'resources': ['products', 'orders', 'customers', 'promo', 'feedback'],
        'docs': '/apidocs/',
    }), 200