"""Відгуки клієнтів: створення і показ опублікованих (CRUD: C і R)."""
from flask import Blueprint, redirect, render_template, request, url_for

from models import get_db

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def leave_feedback():
    errors = []
    values = {}

    if request.method == 'POST':
        values = {
            'name': request.form.get('name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'message': request.form.get('message', '').strip(),
        }
        rating = request.form.get('rating', type=int)

        if not values['name']:
            errors.append("Вкажіть ваше ім'я.")
        if not values['message']:
            errors.append('Напишіть відгук.')
        elif len(values['message']) > 1000:
            errors.append('Відгук не більше 1000 символів.')
        if rating not in (1, 2, 3, 4, 5):
            errors.append('Оцініть від 1 до 5.')

        if not errors:
            db = get_db()
            # Параметризований запит захищає від SQL-ін'єкцій
            db.execute(
                'INSERT INTO feedback (name, email, message, rating) VALUES (?, ?, ?, ?)',
                (values['name'], values['email'] or None, values['message'], rating),
            )
            db.commit()
            return redirect(url_for('feedback.leave_feedback', sent=1))

    reviews = get_db().execute(
        'SELECT name, rating, message, created_at FROM feedback '
        'WHERE is_published = 1 ORDER BY id DESC LIMIT 20'
    ).fetchall()
    return render_template('feedback.html', errors=errors, values=values,
                           reviews=reviews, sent=request.args.get('sent'))