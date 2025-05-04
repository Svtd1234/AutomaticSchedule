import eel
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import threading
import logging
from flask_caching import Cache

logging.basicConfig(level=logging.INFO)

eel.init("web")

app = Flask(__name__)
CORS(app)

# Налаштування кешу
app.config["CACHE_TYPE"] = "simple"
cache = Cache(app)

SCHEDULE_KEY = "saved_schedule"

# Список дозволених IP-адрес
ALLOWED_IPS = ["192.168.0.102", "192.168.0.105"]


@app.before_request
def limit_remote_addr():
    """
    Обмежуємо доступ лише до IP-адрес із білого списку.
    Якщо IP користувача відсутній у списку — повертаємо 403 (Forbidden).
    """
    if request.remote_addr not in ALLOWED_IPS:
        abort(403)  # Forbidden


@app.route("/api/schedule", methods=["POST"])
def receive_schedule():
    """
    Приймає розклад від клієнта (JSON), зберігає в кеш.
    """
    try:
        data = request.json  # список або об'єкт
        cache.set(SCHEDULE_KEY, data)
        return jsonify({"status": "OK", "message": "Schedule saved!"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500


@app.route("/api/schedule", methods=["GET"])
def get_schedule():
    """
    Повертає збережений у кеші розклад.
    """
    data = cache.get(SCHEDULE_KEY) or []
    return jsonify(data), 200


@eel.expose
def get_cached_schedule():
    """
    Повертає розклад, збережений у кеші.
    """
    return cache.get(SCHEDULE_KEY) or []


# Запуск Flask-сервера в окремому потоці
def run_flask():
    # Зверніть увагу, що при такому налаштуванні host="0.0.0.0"
    # додаток буде доступний ззовні, але ми перевіряємо IP у limit_remote_addr.
    app.run(host="192.168.0.105", port=19780)


# Запуск Eel
def run_eel():
    eel.start("index.html", size=(800, 600), port=19781, host="192.168.0.105", block=True)


if __name__ == "__main__":
    # Запускаємо Flask у фоні
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаємо Eel (відкриє вікно з index.html)
    run_eel()
