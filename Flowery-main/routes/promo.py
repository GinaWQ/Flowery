"""Керування промокодами та розрахунок знижок для магазину."""
from datetime import datetime
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import get_db

promo_bp = Blueprint('promo', __name__, url_prefix='/admin/promo')


def _require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Увійдіть в адмін-панель, щоб керувати промокодами.', 'warning')
            return redirect(url_for('admin.login'))
        return view(*args, **kwargs)

    return wrapped


def find_valid_promo(db, code, subtotal):
    """Перевіряє промокод за кодом, активністю, мінімальною сумою та строком дії."""
    clean_code = (code or '').strip().upper()
    if not clean_code:
        return None

    promo = db.execute(
        'SELECT * FROM promo_codes WHERE UPPER(code) = ? AND is_active = 1',
        (clean_code,),
    ).fetchone()
    if not promo:
        return None

    try:
        amount = float(subtotal or 0)
    except (TypeError, ValueError):
        amount = 0.0

    min_amount = float(promo['min_order_amount'] or 0)
    if amount < min_amount:
        return None

    expires_at = (promo['expires_at'] or '').strip()
    if expires_at:
        today_str = datetime.now().strftime('%Y-%m-%d')
        if expires_at[:10] < today_str:
            return None

    return promo


def promo_discount(promo, subtotal):
    """Повертає суму знижки у гривнях (округлену до копійок)."""
    if not promo:
        return 0.0
    try:
        amount = float(subtotal or 0)
        percent = float(promo['discount_percent'] or 0)
    except (TypeError, ValueError):
        return 0.0

    if amount <= 0 or percent <= 0:
        return 0.0
    return round(amount * percent / 100.0, 2)


@promo_bp.route('/')
@_require_admin
def promo_list():
    db = get_db()
    promos = db.execute('SELECT * FROM promo_codes ORDER BY id DESC').fetchall()
    try:
        return render_template('admin/promo.html', promos=promos)
    except Exception:
        items = [
            f"<li><b>{p['code']}</b> — -{p['discount_percent']}% (від {p['min_order_amount']} грн)</li>"
            for p in promos
        ]
        return f"<h2>Промокоди</h2><ul>{''.join(items)}</ul>"


@promo_bp.route('/add', methods=['POST'])
@_require_admin
def add_promo():
    code = (request.form.get('code') or '').strip().upper()
    expires_at = (request.form.get('expires_at') or '').strip() or None

    try:
        discount_percent = int(request.form.get('discount_percent') or 0)
        min_order_amount = float(request.form.get('min_order_amount') or 0)
    except ValueError:
        flash('Перевірте коректність відсотка знижки та мінімальної суми.', 'error')
        return redirect(url_for('promo.promo_list'))

    if not code or not (1 <= discount_percent <= 100) or min_order_amount < 0:
        flash('Код обовʼязковий, знижка — від 1% до 100%, мін. сума >= 0.', 'error')
        return redirect(url_for('promo.promo_list'))

    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO promo_codes (code, discount_percent, min_order_amount, is_active, expires_at)
            VALUES (?, ?, ?, 1, ?)
            """,
            (code, discount_percent, min_order_amount, expires_at),
        )
        db.commit()
        flash(f'Промокод {code} створено.', 'success')
    except Exception:
        flash('Такий промокод уже існує.', 'error')
    return redirect(url_for('promo.promo_list'))


@promo_bp.route('/<int:promo_id>/toggle', methods=['POST'])
@_require_admin
def toggle_promo(promo_id):
    db = get_db()
    db.execute(
        'UPDATE promo_codes SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?',
        (promo_id,),
    )
    db.commit()
    flash('Статус промокоду оновлено.', 'success')
    return redirect(url_for('promo.promo_list'))


@promo_bp.route('/<int:promo_id>/delete', methods=['POST'])
@_require_admin
def delete_promo(promo_id):
    db = get_db()
    db.execute('DELETE FROM promo_codes WHERE id = ?', (promo_id,))
    db.commit()
    flash('Промокод видалено.', 'success')
    return redirect(url_for('promo.promo_list'))