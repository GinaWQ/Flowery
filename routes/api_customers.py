"""Заглушка. Реальний код пише учасник C."""
from flask import Blueprint

api_customers_bp = Blueprint('api_customers', __name__, url_prefix='/api/v1')