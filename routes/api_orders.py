"""Заглушка. Реальний код пише учасник B."""
from flask import Blueprint

api_orders_bp = Blueprint('api_orders', __name__, url_prefix='/api/v1')