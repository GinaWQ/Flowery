"""Перевірки каталогу, оформлення замовлення та захисту адмін-розділу."""
import os
import tempfile
import unittest

from app import app
from models import get_db, init_db


class ShopTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        app.config.update(
            TESTING=True,
            DATABASE=os.path.join(self.temp_dir.name, 'test.sqlite'),
            SECRET_KEY='test-only-secret',
            ADMIN_PASSWORD='test-only-password',
        )
        with app.app_context():
            init_db()
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_catalog_uses_seeded_database_products(self):
        response = self.client.get('/catalog')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Ніжний світанок'.encode(), response.data)
        self.assertIn('У кошик'.encode(), response.data)

    def test_checkout_saves_order_and_related_product(self):
        with app.app_context():
            product = get_db().execute(
                'SELECT id, price FROM products ORDER BY id LIMIT 1'
            ).fetchone()

        self.client.post(
            f"/cart/add/{product['id']}",
            data={'quantity': '2'},
        )
        self.assertEqual(self.client.get('/cart').status_code, 200)
        self.assertEqual(self.client.get('/checkout').status_code, 200)
        response = self.client.post(
            '/checkout',
            data={
                'name': 'Тестовий клієнт',
                'phone': '+380000000000',
                'email': 'test@example.com',
                'address': 'Тестова адреса, 1',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Замовлення №'.encode(), response.data)
        with app.app_context():
            order = get_db().execute('SELECT * FROM orders').fetchone()
            item = get_db().execute('SELECT * FROM order_items').fetchone()
            self.assertIsNotNone(order)
            self.assertEqual(order['status'], 'new')
            self.assertEqual(item['order_id'], order['id'])
            self.assertEqual(item['product_id'], product['id'])
            self.assertEqual(item['quantity'], 2)
            self.assertAlmostEqual(order['total'], product['price'] * 2)

    def test_admin_can_add_and_archive_a_product(self):
        self.client.post(
            '/admin/login',
            data={'password': 'test-only-password'},
        )
        self.assertEqual(self.client.get('/admin/products').status_code, 200)
        self.assertEqual(self.client.get('/admin/products/new').status_code, 200)
        response = self.client.post(
            '/admin/products/new',
            data={
                'name': 'Тестовий букет',
                'category': 'Букети',
                'description': 'Букет для тесту.',
                'emoji': '💐',
                'price': '500',
            },
        )
        self.assertEqual(response.status_code, 302)

        with app.app_context():
            product = get_db().execute(
                "SELECT id FROM products WHERE name = 'Тестовий букет'"
            ).fetchone()
        self.assertIsNotNone(product)

        self.client.post(f"/admin/products/{product['id']}/toggle")
        with app.app_context():
            archived = get_db().execute(
                'SELECT is_active FROM products WHERE id = ?', (product['id'],)
            ).fetchone()
        self.assertEqual(archived['is_active'], 0)

    def test_admin_can_change_order_status(self):
        with app.app_context():
            product = get_db().execute(
                'SELECT id FROM products ORDER BY id LIMIT 1'
            ).fetchone()
        self.client.post(f"/cart/add/{product['id']}", data={'quantity': '1'})
        self.client.post(
            '/checkout',
            data={
                'name': 'Тестовий клієнт',
                'phone': '+380000000000',
                'email': '',
                'address': 'Тестова адреса, 1',
            },
        )
        with app.app_context():
            order = get_db().execute('SELECT id FROM orders').fetchone()

        self.client.post(
            '/admin/login',
            data={'password': 'test-only-password'},
        )
        self.assertEqual(self.client.get('/admin/orders').status_code, 200)
        self.assertEqual(
            self.client.get(f"/admin/orders/{order['id']}").status_code,
            200,
        )
        response = self.client.post(
            f"/admin/orders/{order['id']}/status",
            data={'status': 'confirmed'},
        )
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            updated = get_db().execute(
                'SELECT status FROM orders WHERE id = ?', (order['id'],)
            ).fetchone()
        self.assertEqual(updated['status'], 'confirmed')

    def test_admin_shop_requires_login(self):
        response = self.client.get('/admin/products')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login', response.headers['Location'])


if __name__ == '__main__':
    unittest.main()
