"""Flowery: вебзастосунок квіткового магазину (ЛР 03 і ЛР 04)."""
import os

from flask import Flask, render_template

from models import close_db, init_db
from routes.admin import admin_bp
from routes.admin_shop import admin_shop_bp
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

for bp in (feedback_bp, admin_bp, search_bp, shop_bp,
           admin_shop_bp, customers_bp, promo_bp):
    app.register_blueprint(bp)


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

@app.errorhandler(404)
def page_not_found(error):
    """Власна сторінка помилки 404."""
    return render_template("404.html"), 404


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)