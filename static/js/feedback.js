const feedbackUI = {
    list: document.getElementById('feedback-list'),
    message: document.getElementById('feedback-message'),
    loading: document.getElementById('feedback-loading'),
    form: document.getElementById('feedback-form'),
};

/** GET /api/v1/feedback */
async function loadFeedback() {
    setLoading(feedbackUI.loading, true);
    try {
        const data = await apiRequest('/feedback');
        renderFeedback(data.feedback);
    } catch (error) {
        showMessage(feedbackUI.message, '❌ Не вдалося завантажити відгуки: ' + error.message, 'error');
    } finally {
        setLoading(feedbackUI.loading, false);
    }
}

function renderFeedback(items) {
    feedbackUI.list.innerHTML = '';

    if (!items || items.length === 0) {
        feedbackUI.list.textContent = 'Відгуків ще немає. Будьте першим!';
        return;
    }

    items.forEach((item) => {
        const card = document.createElement('article');
        card.className = 'rounded-xl bg-pink-50 p-4';

        const head = document.createElement('p');
        head.className = 'font-semibold';
        head.textContent = `${item.name} `;

        const stars = document.createElement('span');
        stars.className = 'text-yellow-500';
        stars.textContent = '★'.repeat(item.rating);
        head.appendChild(stars);

        const text = document.createElement('p');
        text.className = 'text-gray-700 mt-1';
        text.textContent = item.message;

        card.append(head, text);
        feedbackUI.list.appendChild(card);
    });
}

/** POST /api/v1/feedback */
feedbackUI.form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = document.getElementById('feedback-name').value.trim();
    const message = document.getElementById('feedback-message-text').value.trim();
    const rating = Number(document.getElementById('feedback-rating').value);

    if (name.length < 2) {
        showMessage(feedbackUI.message, '❌ Введіть імʼя (щонайменше 2 символи)', 'error');
        return;
    }
    if (message.length < 5) {
        showMessage(feedbackUI.message, '❌ Відгук має містити щонайменше 5 символів', 'error');
        return;
    }
    if (!rating) {
        showMessage(feedbackUI.message, '❌ Оцініть букет від 1 до 5', 'error');
        return;
    }

    setLoading(feedbackUI.loading, true);
    try {
        await apiRequest('/feedback', {
            method: 'POST',
            body: JSON.stringify({ name: name, message: message, rating: rating }),
        });
        showMessage(feedbackUI.message, '✅ Дякуємо за відгук!', 'success');
        feedbackUI.form.reset();
        await loadFeedback();
    } catch (error) {
        showMessage(feedbackUI.message, '❌ Помилка надсилання: ' + error.message, 'error');
    } finally {
        setLoading(feedbackUI.loading, false);
    }
});

// Початкове завантаження
loadFeedback();

// Блок відгуків. Заповнює A на етапі 1.
