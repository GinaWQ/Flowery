"""Адмін-панель: вхід, перегляд, перемикання публікації і видалення відгуків."""
from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from auth import admin_required
from models import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == current_app.config['ADMIN_PASSWORD']:
            session['is_admin'] = True
            nxt = request.args.get('next', '')
            # Лише внутрішні адреси, щоб не було відкритого перенаправлення
            if not nxt.startswith('/') or nxt.startswith('//'):
                nxt = url_for('admin.dashboard')
            return redirect(nxt)
        error = 'Невірний пароль.'
    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))


@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')


@admin_bp.route('/feedback')
@admin_required
def feedback_list():
    """READ: усі відгуки, включно з прихованими."""
    rows = get_db().execute('SELECT * FROM feedback ORDER BY id DESC').fetchall()
    return render_template('admin/feedback.html', rows=rows)


@admin_bp.route('/feedback/<int:fid>/toggle', methods=['POST'])
@admin_required
def feedback_toggle(fid):
    """UPDATE: показати або сховати відгук (перемикання 0 ↔ 1)."""
    db = get_db()
    db.execute('UPDATE feedback SET is_published = 1 - is_published WHERE id = ?', (fid,))
    db.commit()
    return redirect(url_for('admin.feedback_list'))


@admin_bp.route('/feedback/<int:fid>/delete', methods=['POST'])
@admin_required
def feedback_delete(fid):
    """DELETE: видалення. Тільки POST, щоб видалення не спрацювало від простого переходу за посиланням."""
    db = get_db()
    db.execute('DELETE FROM feedback WHERE id = ?', (fid,))
    db.commit()
    return redirect(url_for('admin.feedback_list'))