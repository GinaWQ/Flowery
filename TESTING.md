# Тестування застосунку Flowery

## Як запустити тести
```bash
source .venv/Scripts/activate
pytest
```
Покриття коду:
```bash
pytest --cov=app --cov=models --cov=routes --cov-report=term-missing
```

## Учасник A: відгуки і core API
### Core API
| Тест | Що перевіряє | Очікуваний результат |
|---|---|---|
| test_api_index_lists_resources | GET /api/v1/ | 200, є список ресурсів |
| test_unknown_api_address_returns_json_404 | GET /api/v1/nothing | 404 у форматі JSON |

### Відгуки: unit
| Тест | Що перевіряє | Очікуваний результат |
|---|---|---|
| test_valid_feedback_has_no_errors | Коректний відгук | Немає помилок |
| test_boundary_ratings_are_valid (параметр) | Оцінки 1 і 5 | Без помилок |
| test_invalid_ratings_are_errors (параметр) | 0, 6, '5', True, None | Помилка |
| test_empty_message_is_error | Текст з пробілів | Помилка |
| test_message_longer_than_1000_is_error | 1001 символ | Помилка |
| test_message_of_1000_chars_is_valid | 1000 символів (межа) | Без помилок |
| test_email_without_at_is_error | Email без @ | Помилка |
| test_none_body_is_error | Немає тіла | Повідомлення про JSON |

### Відгуки: integration
| Тест | Запит | Очікуваний результат |
|---|---|---|
| test_get_feedback_empty_database | GET /api/v1/feedback | 200, порожній список |
| test_create_feedback_returns_201 | POST | 201, заголовок Location |
| test_invalid_rating_returns_400 | POST з rating 9 | 400 |
| test_hidden_feedback_is_not_listed | Прихований відгук | Не в списку |
| test_delete_without_key_returns_401 | DELETE без ключа | 401 |
| test_delete_with_wrong_key_returns_403 | DELETE з хибним ключем | 403 |
| test_delete_with_key_returns_204_then_404 | DELETE двічі | 204, потім 404 |

## Учасник B: товари
<!-- Заповнює B -->

## Учасник C: клієнти і промокоди
<!-- Заповнює C -->

## Результати
<!-- Скріншоти і покриття: A -->