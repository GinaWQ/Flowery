"""Заглушка. Реальний код пише учасник C."""
from flask import Blueprint

api_promo_bp = Blueprint('api_promo', __name__, url_prefix='/api/v1')