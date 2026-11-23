// ============================================
// Спільні функції для всіх блоків сторінки /api-demo.
// Файл учасника A. Інші учасники ЛИШЕ використовують ці функції.
// ============================================

const API_BASE = '/api/v1';

/**
 * Надсилає запит до API і повертає розібрану відповідь.
 * Кидає Error з текстом для користувача, якщо сталась помилка.
 *
 * fetch() не вважає 404 чи 500 помилкою, тому перевіряємо response.ok.
 */
async function apiRequest(path, options = {}) {
    let response;
    try {
        response = await fetch(API_BASE + path, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
    } catch (networkError) {
        // Сюди потрапляємо, якщо сервер вимкнено або немає звʼязку
        throw new Error('немає звʼязку з сервером. Перевірте, чи запущено python app.py');
    }

    // 204 No Content: тіла немає
    if (response.status === 204) {
        return null;
    }

    const body = await response.json().catch(() => null);

    if (!response.ok) {
        // Наш API повертає {"error": "текст"}
        const text = (body && body.error) || `помилка сервера (код ${response.status})`;
        throw new Error(text);
    }
    return body;
}

/**
 * Показує повідомлення у вказаному блоці (success або error).
 * Зникає через 6 секунд.
 */
function showMessage(box, text, type) {
    box.textContent = text;
    box.className = `block-message ${type}`;
    clearTimeout(box._hideTimer);
    box._hideTimer = setTimeout(() => box.classList.add('hidden'), 6000);
}

/** Показує або ховає індикатор завантаження у вказаному блоці. */
function setLoading(box, show) {
    box.classList.toggle('hidden', !show);
}