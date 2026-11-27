"""API відгуків: список, створення, видалення з ключем адміна. Файл учасника A."""
import sqlite3

from flask import Blueprint, current_app, jsonify, request

from models import get_db
from routes.api_core import json_error

api_feedback_bp = Blueprint('api_feedback', __name__, url_prefix='/api/v1')


@api_feedback_bp.route('/feedback', methods=['GET'])
def list_feedback():
    """Опубліковані відгуки.
    ---
    tags: [Відгуки]
    responses:
      200:
        description: Список відгуків
    """
    rows = get_db().execute(
        'SELECT id, name, rating, message, created_at FROM feedback '
        'WHERE is_published = 1 ORDER BY id DESC'
    ).fetchall()
    return jsonify({'feedback': [dict(r) for r in rows], 'count': len(rows)}), 200

def validate_feedback(data):
    """Перевіряє відгук. Повертає список помилок (порожній, якщо дані коректні).

    Не звертається до бази і не використовує запит.
    """
    if not isinstance(data, dict):
        return ['Тіло запиту має бути JSON-обʼєктом']

    errors = []
    name = data.get('name')
    message = data.get('message')
    rating = data.get('rating')
    email = data.get('email')

    if not isinstance(name, str) or not name.strip():
        errors.append('name: непорожній рядок')
    if not isinstance(message, str) or not message.strip():
        errors.append('message: непорожній рядок')
    elif len(message) > 1000:
        errors.append('message: не більше 1000 символів')
    # bool — підклас int у Python, тому відсіюємо True/False окремо
    if not isinstance(rating, int) or isinstance(rating, bool) or not 1 <= rating <= 5:
        errors.append('rating: ціле число від 1 до 5')
    if email is not None and (not isinstance(email, str) or '@' not in email):
        errors.append('email: некоректна адреса або null')

    return errors


@api_feedback_bp.route('/feedback', methods=['POST'])
def create_feedback():
    """Залишити відгук. ..."""
    data = request.get_json(silent=True)
    errors = validate_feedback(data)
    if errors:
        return json_error('; '.join(errors), 400)

    db = get_db()
    cur = db.execute(
        'INSERT INTO feedback (name, email, message, rating) VALUES (?, ?, ?, ?)',
        (name.strip(), email, message.strip(), rating),
    )
    db.commit()
    new_id = cur.lastrowid
    return jsonify({'id': new_id, 'name': name.strip(), 'rating': rating}), 201, \
        {'Location': f'/api/v1/feedback/{new_id}'}


@api_feedback_bp.route('/feedback/<int:fid>', methods=['DELETE'])
def delete_feedback(fid):
    """Видалити відгук. Потрібен заголовок X-Admin-Key.
    ---
    tags: [Відгуки]
    parameters:
      - name: fid
        in: path
        type: integer
        required: true
      - name: X-Admin-Key
        in: header
        type: string
        required: true
        description: Пароль адміністратора (ADMIN_PASSWORD)
    responses:
      204:
        description: Відгук видалено
      401:
        description: Не передано ключ адміністратора
      403:
        description: Ключ неправильний
      404:
        description: Відгук не знайдено
    """
    key = request.headers.get('X-Admin-Key')
    if key is None:
        return json_error('Потрібен заголовок X-Admin-Key', 401)
    if key != current_app.config['ADMIN_PASSWORD']:
        return json_error('Недійсний ключ адміністратора', 403)

    db = get_db()
    cur = db.execute('DELETE FROM feedback WHERE id = ?', (fid,))
    db.commit()
    if cur.rowcount == 0:
        return json_error('Відгук не знайдено', 404)
    return '', 204