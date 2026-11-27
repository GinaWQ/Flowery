"""Спільні fixtures для всіх тестів. Файл учасника A."""
import pytest

from app import app as flask_app
from models import init_db


@pytest.fixture
def client(tmp_path):
    """Тестовий клієнт із окремою тимчасовою базою.

    tmp_path створює нову порожню папку для кожного тесту.
    """
    # 1. Вказуємо тестову базу ДО створення таблиць
    flask_app.config['TESTING'] = True
    flask_app.config['DATABASE'] = str(tmp_path / 'test.db')

    # 2. init_db() читає DATABASE з поточного застосунку, тому потрібен app_context
    with flask_app.app_context():
        init_db()

    # 3. Тестовий клієнт: надсилає запити без справжнього сервера
    with flask_app.test_client() as test_client:
        yield test_client