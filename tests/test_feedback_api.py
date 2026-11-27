"""Integration тести API відгуків. Файл учасника A."""
from models import get_db


def create_feedback(client, **changes):
    """Допоміжна функція: створює відгук через API і повертає відповідь."""
    payload = {'name': 'Марина', 'message': 'Троянди свіжі 🌹', 'rating': 5}
    payload.update(changes)
    return client.post('/api/v1/feedback', json=payload)


def test_get_feedback_empty_database(client):
    response = client.get('/api/v1/feedback')

    assert response.status_code == 200
    assert response.json == {'feedback': [], 'count': 0}


def test_create_feedback_returns_201(client):
    response = create_feedback(client)

    assert response.status_code == 201
    assert response.json['name'] == 'Марина'
    assert response.headers['Location'].startswith('/api/v1/feedback/')


def test_invalid_rating_returns_400(client):
    response = create_feedback(client, rating=9)

    assert response.status_code == 400
    assert 'rating' in response.json['error']


def test_hidden_feedback_is_not_listed(client):
    # Arrange: створюємо відгук і ховаємо його напряму в тестовій базі
    fid = create_feedback(client).json['id']
    with client.application.app_context():
        db = get_db()
        db.execute('UPDATE feedback SET is_published = 0 WHERE id = ?', (fid,))
        db.commit()

    # Act
    response = client.get('/api/v1/feedback')

    # Assert
    assert response.json['count'] == 0


def test_delete_without_key_returns_401(client):
    fid = create_feedback(client).json['id']

    response = client.delete(f'/api/v1/feedback/{fid}')

    assert response.status_code == 401


def test_delete_with_wrong_key_returns_403(client):
    fid = create_feedback(client).json['id']

    response = client.delete(f'/api/v1/feedback/{fid}', headers={'X-Admin-Key': 'wrong'})

    assert response.status_code == 403


def test_delete_with_key_returns_204_then_404(client):
    # Arrange
    fid = create_feedback(client).json['id']
    headers = {'X-Admin-Key': 'admin123'}

    # Act: перший раз видаляємо, другий раз відгуку вже немає
    first = client.delete(f'/api/v1/feedback/{fid}', headers=headers)
    second = client.delete(f'/api/v1/feedback/{fid}', headers=headers)

    # Assert
    assert first.status_code == 204
    assert second.status_code == 404