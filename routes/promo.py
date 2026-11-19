
"""Керування промокодами та розрахунок знижок."""
import sqlite3
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth import admin_required
from models import get_db

promo_bp = Blueprint('promo', __name__, url_prefix='/admin/promo')


def find_valid_promo(db, code, subtotal):
    """Перевіряє, чи можна використати промокод."""
    clean_code = (code or '').strip().upper()

    if not clean_code:
        return None

    promo = db.execute(
        'SELECT * FROM promo_codes WHERE UPPER(code) = ? AND is_active = 1',
        (clean_code,)
    ).fetchone()

    if not promo:
        return None

    try:
        amount = float(subtotal or 0)
    except (TypeError, ValueError):
        return None

    if amount < float(promo['min_order_amount']):
        return None

    expires_at = (promo['expires_at'] or '').strip()

    if expires_at:
        try:
            if date.fromisoformat(expires_at[:10]) < date.today():
                return None
        except ValueError:
            return None

    return promo


def promo_discount(promo, subtotal):
    """Обчислює суму знижки у гривнях."""
    if not promo:
        return 0.0

    try:
        amount = float(subtotal or 0)
        percent = float(promo['discount_percent'])
    except (TypeError, ValueError, KeyError):
        return 0.0

    if amount <= 0 or not 0 < percent <= 100:
        return 0.0

    return round(amount * percent / 100, 2)


@promo_bp.route('/')
@admin_required
def promo_list():
    db = get_db()

    promos = db.execute(
        'SELECT * FROM promo_codes ORDER BY id DESC'
    ).fetchall()

    return render_template('admin/promo.html', promos=promos)


@promo_bp.route('/add', methods=['POST'])
@admin_required
def add_promo():
    code = (request.form.get('code') or '').strip().upper()
    expires_at = (request.form.get('expires_at') or '').strip() or None

    try:
        discount_percent = int(request.form.get('discount_percent') or 0)
        min_order_amount = float(request.form.get('min_order_amount') or 0)
    except ValueError:
        flash('Перевірте відсоток знижки та мінімальну суму.', 'error')
        return redirect(url_for('promo.promo_list'))

    if (
        not code
        or not (1 <= discount_percent <= 100)
        or min_order_amount < 0
    ):
        flash('Вкажіть код, знижку від 1% до 100% та мінімальну суму від 0.', 'error')
        return redirect(url_for('promo.promo_list'))

    if expires_at:
        try:
            date.fromisoformat(expires_at)
        except ValueError:
            flash('Некоректна дата завершення дії.', 'error')
            return redirect(url_for('promo.promo_list'))

    db = get_db()

    try:
        db.execute(
            """
            INSERT INTO promo_codes
                (code, discount_percent, min_order_amount, is_active, expires_at)
            VALUES (?, ?, ?, 1, ?)
            """,
            (code, discount_percent, min_order_amount, expires_at)
        )
        db.commit()
        flash(f'Промокод {code} успішно створено.', 'success')
    except sqlite3.IntegrityError:
        flash('Промокод із таким кодом уже існує.', 'error')

    return redirect(url_for('promo.promo_list'))


@promo_bp.route('/<int:promo_id>/toggle', methods=['POST'])
@admin_required
def toggle_promo(promo_id):
    db = get_db()

    db.execute(
        """
        UPDATE promo_codes
        SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
        WHERE id = ?
        """,
        (promo_id,)
    )
    db.commit()

    flash('Статус промокоду оновлено.', 'success')
    return redirect(url_for('promo.promo_list'))


@promo_bp.route('/<int:promo_id>/delete', methods=['POST'])
@admin_required
def delete_promo(promo_id):
    db = get_db()

    db.execute(
        'DELETE FROM promo_codes WHERE id = ?',
        (promo_id,)
    )
    db.commit()

    flash('Промокод видалено.', 'success')
    return redirect(url_for('promo.promo_list'))
