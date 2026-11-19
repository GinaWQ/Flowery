"""Flowery: сайт магазину квітів + REST API (ЛР 03, 04, 05)."""
import os

from flasgger import Swagger
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from models import close_db, init_db
from routes.admin import admin_bp
from routes.admin_shop import admin_shop_bp
from routes.api_core import api_bp
from routes.api_customers import api_customers_bp
from routes.api_feedback import api_feedback_bp
from routes.api_orders import api_orders_bp
from routes.api_products import api_products_bp
from routes.api_promo import api_promo_bp
from routes.api_v2 import api_v2_bp
from routes.customers import customers_bp
from routes.feedback import feedback_bp
from routes.promo import promo_bp
from routes.search import search_bp
from routes.shop import get_popular, shop_bp

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.root_path, 'db.sqlite')
app.config['SECRET_KEY'] = os.environ.get('FLOWERY_SECRET', 'dev-secret-change-me')
app.config['ADMIN_PASSWORD'] = os.environ.get('FLOWERY_ADMIN_PASSWORD', 'admin123')

app.teardown_appcontext(close_db)

# Swagger UI на /apidocs/ (рівень 2)
swagger = Swagger(app, template={
    'info': {
        'title': 'Flowery API',
        'version': '1.0',
        'description': 'REST API квіткового магазину Flowery',
    },
})

for bp in (admin_bp, admin_shop_bp, feedback_bp, search_bp, shop_bp,
           customers_bp, promo_bp,
           api_bp, api_products_bp, api_orders_bp, api_customers_bp,
           api_promo_bp, api_feedback_bp, api_v2_bp):
    app.register_blueprint(bp)


@app.errorhandler(Exception)
def handle_error(err):
    """Для /api/... повертає JSON. Для сторінок сайту лишає звичайні HTML-сторінки."""
    is_api = request.path.startswith('/api/')
    if isinstance(err, HTTPException):
        if not is_api:
            return err
        return jsonify({'error': err.description, 'status': err.code}), err.code
    if is_api:
        return jsonify({'error': 'Внутрішня помилка сервера', 'status': 500}), 500
    return 'Внутрішня помилка сервера', 500


@app.route('/')
def index():
    return render_template('index.html', popular=get_popular(3))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/delivery')
def delivery():
    return render_template('delivery.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)