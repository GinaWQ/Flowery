from flask import Flask, render_template

# Створюємо екземпляр додатку Flask
app = Flask(__name__)


@app.route('/')
def index():
    """Головна сторінка"""
    return render_template('index.html')


@app.route('/catalog')
def catalog():
    """Каталог букетів"""
    return render_template('catalog.html')


@app.route('/delivery')
def delivery():
    """Доставка та оплата"""
    return render_template('delivery.html')


@app.route('/about')
def about():
    """Про нас"""
    return render_template('about.html')


@app.route('/contacts')
def contacts():
    """Контакти"""
    return render_template('contacts.html')


if __name__ == '__main__':
    # debug=True — автоперезапуск сервера при зміні коду
    app.run(debug=True)