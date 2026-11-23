
// ============================================
// Блок клієнтів і промокодів (учасник C)
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const customerForm = document.getElementById('customer-form');
    const customersList = document.getElementById('customers-list');
    const customersMessage = document.getElementById('customers-message');
    const customersLoading = document.getElementById('customers-loading');

    const promoForm = document.getElementById('promo-form');
    const promoMessage = document.getElementById('promo-message');

    // Якщо блок клієнтів відсутній на сторінці — нічого не виконуємо.
    if (!customerForm || !customersList || !promoForm) {
        return;
    }

    // Завантаження та відображення списку клієнтів.
    async function loadCustomers() {
        setLoading(customersLoading, true);

        try {
            const data = await apiRequest('/customers');

            // API може повертати як масив, так і об'єкт із customers.
            const customers = Array.isArray(data)
                ? data
                : (data.customers || []);

            customersList.innerHTML = '';

            if (customers.length === 0) {
                customersList.textContent = 'Клієнтів поки немає.';
                return;
            }

            customers.forEach(customer => {
                const card = document.createElement('div');
                card.className = 'border rounded-lg p-3';

                const name = document.createElement('strong');
                name.textContent = customer.full_name || 'Без імені';

                const phone = document.createElement('p');
                phone.textContent = customer.phone || '';

                card.append(name, phone);

                if (customer.email) {
                    const email = document.createElement('p');
                    email.textContent = customer.email;
                    card.append(email);
                }

                customersList.appendChild(card);
            });
        } catch (error) {
            showMessage(customersMessage, error.message, 'error');
        } finally {
            setLoading(customersLoading, false);
        }
    }

    // Додавання нового клієнта.
    customerForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const fullName = document.getElementById('customer-name').value.trim();
        const phone = document.getElementById('customer-phone').value.trim();
        const email = document.getElementById('customer-email').value.trim();

        const digits = phone.replace(/\D/g, '');

        if (fullName.length < 2) {
            showMessage(customersMessage, 'Введіть ім’я та прізвище.', 'error');
            return;
        }

        if (digits.length < 10) {
            showMessage(customersMessage, 'Телефон повинен містити щонайменше 10 цифр.', 'error');
            return;
        }

        const button = customerForm.querySelector('button[type="submit"]');
        button.disabled = true;

        try {
            await apiRequest('/customers', {
                method: 'POST',
                body: JSON.stringify({
                    full_name: fullName,
                    phone: phone,
                    email: email || null
                })
            });

            showMessage(customersMessage, 'Клієнта успішно додано!', 'success');
            customerForm.reset();
            await loadCustomers();
        } catch (error) {
            showMessage(customersMessage, error.message, 'error');
        } finally {
            button.disabled = false;
        }
    });

    // Перевірка промокоду та розрахунок знижки.
    promoForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const code = document.getElementById('promo-code').value.trim();
        const subtotal = Number(
            document.getElementById('promo-subtotal').value
        );

        if (!code) {
            showMessage(promoMessage, 'Введіть промокод.', 'error');
            return;
        }

        if (!Number.isFinite(subtotal) || subtotal < 0) {
            showMessage(promoMessage, 'Введіть коректну суму замовлення.', 'error');
            return;
        }

        const button = promoForm.querySelector('button[type="submit"]');
        button.disabled = true;

        try {
            const result = await apiRequest('/promo/validate', {
                method: 'POST',
                body: JSON.stringify({
                    code: code,
                    subtotal: subtotal
                })
            });

            const message =
                `Промокод ${result.code} дійсний! ` +
                `Знижка: ${result.discount_percent}%. ` +
                `Економія: ${result.discount_amount} грн. ` +
                `До сплати: ${result.total} грн.`;

            showMessage(promoMessage, message, 'success');
        } catch (error) {
            showMessage(promoMessage, error.message, 'error');
        } finally {
            button.disabled = false;
        }
    });

    // Початкове завантаження клієнтів.
    loadCustomers();
});
