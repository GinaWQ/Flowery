| Метод | Адреса | Призначення | Коди | Хто |
|---|---|---|---|---|
| GET | `/api/v1/` | Довідка по API | 200 | A |
| GET | `/api/v1/products` | Список активних товарів (`?category=`) | 200 | B |
| GET | `/api/v1/products/<id>` | Один товар | 200, 404 | B |
| POST | `/api/v1/products` | Створити товар | 201, 400, 409 | B |
| PUT | `/api/v1/products/<id>` | Повністю замінити товар | 200, 400, 404, 409 | B |
| PATCH | `/api/v1/products/<id>` | Частково змінити товар | 200, 400, 404, 409 | B |
| DELETE | `/api/v1/products/<id>` | Видалити товар | 204, 404 | B |
| GET | `/api/v1/orders` | Список замовлень (`?status=`) | 200, 400 | B |
| GET | `/api/v1/orders/<id>` | Замовлення з товарами | 200, 404 | B |
| PATCH | `/api/v1/orders/<id>` | Змінити статус замовлення | 200, 400, 404 | B |
| GET | `/api/v1/customers` | Список клієнтів | 200 | C |
| GET | `/api/v1/customers/<id>` | Один клієнт | 200, 404 | C |
| POST | `/api/v1/customers` | Створити клієнта | 201, 400, 409 | C |
| PUT | `/api/v1/customers/<id>` | Оновити клієнта | 200, 400, 404, 409 | C |
| DELETE | `/api/v1/customers/<id>` | Видалити клієнта | 204, 404 | C |
| POST | `/api/v1/promo/validate` | Перевірити промокод | 200, 400, 404 | C |
| GET | `/api/v1/feedback` | Опубліковані відгуки | 200 | A |
| POST | `/api/v1/feedback` | Залишити відгук | 201, 400 | A |
| DELETE | `/api/v1/feedback/<id>` | Видалити відгук (ключ адміна) | 204, 401, 403, 404 | A |
| GET | `/api/v2/products` | Товари, версія 2 | 200 | A |