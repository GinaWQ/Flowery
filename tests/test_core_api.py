"""Integration тести базових адрес API. Файл учасника A."""


def test_api_index_lists_resources(client):
    # Arrange: клієнт уже підготовлено fixture

    # Act
    response = client.get('/api/v1/')

    # Assert
    assert response.status_code == 200
    assert 'products' in response.json['resources']


def test_unknown_api_address_returns_json_404(client):
    # Act
    response = client.get('/api/v1/nothing')

    # Assert: помилка має бути у форматі JSON, а не HTML
    assert response.status_code == 404
    assert 'error' in response.json