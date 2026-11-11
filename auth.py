"""Захист адмін-панелі: доступ лише після входу за паролем."""
from functools import wraps

from flask import redirect, request, session, url_for


def admin_required(view):
    """Декоратор: якщо адміністратор не увійшов, перенаправляє на сторінку входу."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin.login', next=request.path))
        return view(*args, **kwargs)
    return wrapper