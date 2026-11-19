"""Заглушка. Реальний код пише A на етапі 1."""
from flask import Blueprint

api_v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')