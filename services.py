"""Спільна бізнес-логіка магазину (використовують адмінка і API)."""

ORDER_STATUSES = ['new', 'paid', 'assembling', 'delivering', 'done', 'cancelled']


def set_order_status(db, order_id, new_status):
    """Змінює статус замовлення. Повертає False, якщо замовлення не існує.

    Скасування повертає товари на склад. Commit робить викликач,
    щоб зміна була частиною однієї транзакції.
    """
    order = db.execute('SELECT status FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order is None:
        return False

    if new_status == 'cancelled' and order['status'] != 'cancelled':
        items = db.execute(
            'SELECT product_id, quantity FROM order_items WHERE order_id = ?', (order_id,)
        ).fetchall()
        for item in items:
            if item['product_id'] is not None:
                db.execute('UPDATE products SET stock = stock + ? WHERE id = ?',
                           (item['quantity'], item['product_id']))

    db.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    return True