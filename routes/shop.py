"""Заглушка. Реальний код пише B."""
from flask import Blueprint

shop_bp = Blueprint('shop', __name__)


def get_popular(limit=3):
    return []


@shop_bp.route('/catalog')
def catalog():
    return 'Каталог: у розробці'