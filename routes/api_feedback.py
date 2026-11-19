"""Заглушка. Реальний код пише A на етапі 1."""
from flask import Blueprint

api_feedback_bp = Blueprint('api_feedback', __name__, url_prefix='/api/v1')