"""Пошук і фільтрація товарів (додаткова функція рівня 3)."""
from flask import Blueprint, render_template, request

from models import get_db

search_bp = Blueprint('search', __name__)


@search_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    max_price = request.args.get('max_price', type=int)

    db = get_db()
    categories = [r['category'] for r in db.execute(
        'SELECT DISTINCT category FROM products WHERE is_active = 1 ORDER BY category'
    ).fetchall()]

    results = []
    if q or category or max_price is not None:
        # SQL-фрагменти фіксовані, значення передаються через ? (безпечно)
        sql = 'SELECT * FROM products WHERE is_active = 1'
        params = []
        if q:
            sql += ' AND (name LIKE ? OR description LIKE ?)'
            params += [f'%{q}%', f'%{q}%']
        if category:
            sql += ' AND category = ?'
            params.append(category)
        if max_price is not None:
            sql += ' AND price <= ?'
            params.append(max_price)
        sql += ' ORDER BY price'
        results = db.execute(sql, params).fetchall()

    return render_template('search.html', q=q, category=category, max_price=max_price,
                           categories=categories, results=results)