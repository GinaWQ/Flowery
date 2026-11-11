"""Заглушка. Реальний код пише B."""
from flask import Blueprint

admin_shop_bp = Blueprint('admin_shop', __name__, url_prefix='/admin')


@admin_shop_bp.route('/products')
def products():
    return 'Товари: у розробці'


@admin_shop_bp.route('/orders')
def orders():
    return 'Замовлення: у розробці'