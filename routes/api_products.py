"""Заглушка. Реальний код пише учасник B."""
from flask import Blueprint

api_products_bp = Blueprint('api_products', __name__, url_prefix='/api/v1')