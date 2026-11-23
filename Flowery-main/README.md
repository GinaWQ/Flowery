# 🌸 Flowery — вебзастосунок квіткового магазину

Лабораторні роботи 03–05. Сайт на Flask, база даних SQLite, REST API.

## Склад команди
- GinaWQ — тімлід, база даних, відгуки, API-каркас, версія v2, документація
- [Ім'я учасника B] — товари та замовлення (API і адмінка)
- [Ім'я учасника C] — клієнти та промокоди (API і адмінка)

## Технології
Python 3, Flask, SQLite, Jinja2, Tailwind CSS, Flasgger (Swagger), Postman.

## Запуск
1. `git clone https://github.com/GinaWQ/Flowery.git`
2. `python -m venv .venv` і активація (`source .venv/Scripts/activate` у Git Bash)
3. `pip install -r requirements.txt`
4. `python app.py`
5. Сайт: http://127.0.0.1:5000, API: http://127.0.0.1:5000/api/v1/, документація: http://127.0.0.1:5000/apidocs/

## Про API
Усі відповіді у форматі JSON. Помилки мають вигляд `{"error": "текст"}` і відповідний код статусу.
Версіонування: `/api/v1` (основна) та `/api/v2` (товари з іншими назвами полів).
Ключ адміністратора для видалення відгуків передається в заголовку `X-Admin-Key`.

## Таблиця ендпоінтів
Повні таблиці за ресурсами:
- [Відгуки та версії](docs/api/feedback.md)
- [Товари та замовлення](docs/api/products_orders.md)
- [Клієнти та промокоди](docs/api/customers_promo.md)

## Тестування в Postman
Колекції в папці `postman/`. Імпорт: **Import → File**, середовище `flowery_local_env.json`.

| Колекція | Файл |
|---|---|
| Відгуки та версії | `postman/collection_A_feedback_v2.json` |
| Товари та замовлення | `postman/collection_B_products_orders.json` |
| Клієнти та промокоди | `postman/collection_C_customers_promo.json` |

Скріншоти результатів (успішний запит і запит з помилкою) — у папці `docs/screenshots/`.

### Приклади
![Товари: успішний запит](docs/screenshots/products-ok.png)
![Товари: помилка валідації](docs/screenshots/products-error.png)
![Swagger UI](docs/screenshots/apidocs.png)

## Валідація і помилки
- Перевірка типів і діапазонів у кожному ресурсі (ціна > 0, рейтинг 1–5, телефон від 10 цифр).
- Коди статусу: 200, 201, 204; 400 некоректні дані; 401/403 доступ до видалення відгуків; 404 немає ресурсу; 409 конфлікт унікальності.

## Висновки
Пишемо 2–3 речення від команди: що вдалось, що було складним, що б покращили (наприклад, автентифікацію через токени).