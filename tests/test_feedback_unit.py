"""Unit тести валідації відгуків. Файл учасника A."""
import pytest

from routes.api_feedback import validate_feedback


def valid_feedback(**changes):
    """Допоміжна функція: повертає коректний відгук, у якому можна змінити поля."""
    data = {'name': 'Марина', 'message': 'Троянди чудові 🌹', 'rating': 5}
    data.update(changes)
    return data


def test_valid_feedback_has_no_errors():
    assert validate_feedback(valid_feedback()) == []


@pytest.mark.parametrize('rating', [1, 5])
def test_boundary_ratings_are_valid(rating):
    # Межі шкали: 1 і 5 дозволені
    assert validate_feedback(valid_feedback(rating=rating)) == []


@pytest.mark.parametrize('rating', [0, 6, '5', True, None])
def test_invalid_ratings_are_errors(rating):
    # 0 і 6 — поза межами, '5' — рядок, True — bool, None — відсутнє
    assert validate_feedback(valid_feedback(rating=rating))


def test_empty_message_is_error():
    assert validate_feedback(valid_feedback(message='   '))


def test_message_longer_than_1000_is_error():
    assert validate_feedback(valid_feedback(message='а' * 1001))


def test_message_of_1000_chars_is_valid():
    # Межа: рівно 1000 символів ще допустимо
    assert validate_feedback(valid_feedback(message='а' * 1000)) == []


def test_email_without_at_is_error():
    assert validate_feedback(valid_feedback(email='marina.example.com'))


def test_none_body_is_error():
    assert validate_feedback(None) == ['Тіло запиту має бути JSON-обʼєктом']