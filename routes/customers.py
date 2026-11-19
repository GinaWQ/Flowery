"""Заглушка. Реальний код пише C."""
import re

from flask import Blueprint

customers_bp = Blueprint('customers', __name__, url_prefix='/admin/customers')


def normalize_phone(raw):
    return re.sub(r'\D', '', raw or '')


def get_or_create_customer(db, full_name, phone, address=None):
    return None


@customers_bp.route('/')
def customers_list():
    return 'Клієнти: у розробці'