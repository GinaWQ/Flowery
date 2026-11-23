// ============================================
// Блок «Букети». Файл учасника B.
// Використовує функції з api-common.js: apiRequest, showMessage, setLoading.
// ============================================

const productsUI = {
    list: document.getElementById('products-list'),
    message: document.getElementById('products-message'),
    loading: document.getElementById('products-loading'),
    form: document.getElementById('product-form'),
};

/** GET /api/v1/products: отримує і показує список букетів */
async function loadProducts() {
    setLoading(productsUI.loading, true);
    try {
        const data = await apiRequest('/products');
        renderProducts(data.products);
    } catch (error) {
        showMessage(productsUI.message, '❌ Не вдалося завантажити букети: ' + error.message, 'error');
    } finally {
        setLoading(productsUI.loading, false);
    }
}

/** Малює картки. Дані від сервера вставляємо через textContent, не innerHTML. */
function renderProducts(products) {
    productsUI.list.innerHTML = '';

    if (!products || products.length === 0) {
        productsUI.list.textContent = 'Букетів поки немає. Додайте перший!';
        return;
    }

    products.forEach((p) => {
        const card = document.createElement('article');
        card.className = 'rounded-xl bg-pink-50 p-4';

        const title = document.createElement('h3');
        title.className = 'font-semibold text-lg';
        title.textContent = `${p.emoji} ${p.name}`;

        const category = document.createElement('p');
        category.className = 'text-sm text-gray-600';
        category.textContent = p.category;

        const price = document.createElement('p');
        price.className = 'font-bold text-brand mt-2';
        price.textContent = `${p.price} грн`;

        card.append(title, category, price);
        productsUI.list.appendChild(card);
    });
}

/** Валідація форми до відправки на сервер */
function validateProduct(name, price) {
    if (name.length < 2) {
        return 'Назва має містити щонайменше 2 символи';
    }
    if (!Number.isInteger(price) || price <= 0) {
        return 'Ціна має бути цілим числом більше 0';
    }
    return null;
}

/** POST /api/v1/products: додає новий букет */
productsUI.form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = document.getElementById('product-name').value.trim();
    const price = Number(document.getElementById('product-price').value);

    const problem = validateProduct(name, price);
    if (problem) {
        showMessage(productsUI.message, '❌ ' + problem, 'error');
        return;
    }

    const newProduct = {
        name: name,
        category: document.getElementById('product-category').value,
        price: price,
        emoji: document.getElementById('product-emoji').value,
        description: document.getElementById('product-description').value.trim() || null,
    };

    setLoading(productsUI.loading, true);
    try {
        await apiRequest('/products', {
            method: 'POST',
            body: JSON.stringify(newProduct),
        });
        showMessage(productsUI.message, `✅ Букет «${name}» додано!`, 'success');
        productsUI.form.reset();
        await loadProducts();
    } catch (error) {
        showMessage(productsUI.message, '❌ Помилка додавання: ' + error.message, 'error');
    } finally {
        setLoading(productsUI.loading, false);
    }
});

// Початкове завантаження
loadProducts();