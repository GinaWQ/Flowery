"""Заглушка. Реальний код пише C."""
from flask import Blueprint

promo_bp = Blueprint('promo', __name__, url_prefix='/admin/promo')


def find_valid_promo(db, code, subtotal):
    return None


def promo_discount(promo, subtotal):
    return 0


@promo_bp.route('/')
def promo_list():
    return 'Промокоди: у розробці'