import os
import eel
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import logging
import time
import requests
import pygame
from pygame import mixer
import json
import hashlib
import sqlite3
import socket
from flask import Flask, jsonify
import smtplib
from email.mime.text import MIMEText
import traceback

import serial
import serial.tools.list_ports


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


logging.basicConfig(level=logging.INFO)
pygame.init()

eel.init("web")

con = sqlite3.connect("users.db", check_same_thread=False)
cur = con.cursor()

app = Flask(__name__)
CORS(app)

SCHEDULES_FILE = "schedules.json"

LOCAL_IP = get_local_ip()

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 19780

EEL_HOST = LOCAL_IP
EEL_PORT = 19781

bell_serial_port = None


def load_all_profiles():
    if not os.path.exists(SCHEDULES_FILE):
        return {}
    try:
        with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Помилка читання schedules.json:", e)
        return {}


def save_all_profiles(data):
    try:
        with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Помилка запису у schedules.json:", e)


@app.route("/api/schedule", methods=["POST"])
def receive_schedule():
    profile = request.args.get("profile", "1")
    try:
        data = request.json
        schedule_arr = data.get("schedule", [])
        headers = data.get("headers", {})

        all_profiles = load_all_profiles()

        if profile not in all_profiles:
            all_profiles[profile] = {}

        all_profiles[profile]["schedule"] = schedule_arr
        all_profiles[profile]["headers"] = headers

        save_all_profiles(all_profiles)

        return jsonify({"status": "OK", "message": f"Profile {profile} saved!"}), 200
    except Exception as e:
        print("Помилка receive_schedule:", e)
        return jsonify({"status": "Error", "message": str(e)}), 500


@app.route("/api/schedule", methods=["GET"])
def get_schedule():
    profile = request.args.get("profile", "1")
    try:
        all_profiles = load_all_profiles()
        if profile not in all_profiles:
            return jsonify({"schedule": [], "headers": {}}), 200

        return jsonify({
            "schedule": all_profiles[profile].get("schedule", []),
            "headers": all_profiles[profile].get("headers", {})
        }), 200
    except Exception as ex:
        print("Помилка get_schedule:", ex)
        return jsonify({"schedule": [], "headers": {}}), 200


url = (
    "https://api.alerts.in.ua/v1/alerts/active.json?"
    "token=e8fed684ba6a86cfe4177bac23f8e7712b0d6933ab2203"
)

active_regions_lock = threading.Lock()
active_regions = set()


def update_active_regions():
    global active_regions
    print("Оновлення даних про тривоги...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        new_active_regions = set()
        if "alerts" in data:
            for alert in data["alerts"]:
                oblast = alert.get("location_uid")
                if oblast is not None and alert.get("finished_at") is None:
                    new_active_regions.add(str(oblast))

            with active_regions_lock:
                active_regions = new_active_regions
            print(f"Активні області (оновлено): {active_regions}")
        else:
            print("API не повернуло ключ 'alerts'.")

    except requests.exceptions.RequestException as ex:
        print(f"Помилка HTTP запиту до API: {ex}")
    except json.JSONDecodeError:
        print("Помилка декодування JSON відповіді від API.")
    except Exception as ex:
        print(f"Неочікувана помилка при оновленні активних областей: {ex}")


def periodic_update_alerts(interval_sec=5):
    update_active_regions()
    while True:
        time.sleep(interval_sec)
        update_active_regions()


lass = 0
ff = 0


@eel.expose
def process_selection(oblast):
    """Обробляє вибір області користувачем та перевіряє на тривогу."""
    global lass, ff
    oblast_str = str(oblast)

    if str(lass) != oblast_str:
        ff = 0
        lass = oblast_str

    with active_regions_lock:
        is_active_alert = oblast_str in active_regions

    print(f"Область: {oblast_str}, ff={ff}, Активні: {active_regions}")

    if is_active_alert and ff == 0:
        ff = 1
        print("ТРИВОГА! Сирена...")
        try:
            mixer.init()
            siren_sound_file = "vozdushnaya-sirena-trevoga-vozdushnogo-naleta-air-siren-alarm-26679.mp3"
            if os.path.exists(siren_sound_file):
                mixer.music.load(siren_sound_file)
                mixer.music.play()
            else:
                print(f"Файл сирени не знайдено: {siren_sound_file}")
        except Exception as e:
            print(f"Помилка відтворення сирени: {e}")


@eel.expose
def login(dates):
    username = dates[0]
    password = hashlib.md5(dates[1].encode()).hexdigest()
    try:
        row = cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return 404
        userpass = row[0]
        if userpass == password:
            return 200
        else:
            return 405
    except Exception as e:
        print("Помилка SQL:", e)
        return 500


@eel.expose
def send_emails(senderEmail, smtpLogin, senderPassword, smtpServer, smtpPort, recipients, subject, body):
    server = None
    try:
        receiver_emails_list = [email.strip() for email in recipients.split(',') if email.strip()]

        if not receiver_emails_list:
            print("Помилка: Список отримувачів порожній.")
            return {"success": False, "error": "Список отримувачів порожній."}

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = senderEmail
        msg['To'] = ", ".join(receiver_emails_list)

        print(f"Спроба підключення до SMTP: {smtpServer}:{smtpPort}...")

        smtp_port_int = int(smtpPort)
        if smtp_port_int == 465:
            server = smtplib.SMTP_SSL(smtpServer, smtp_port_int)
        else:
            server = smtplib.SMTP(smtpServer, smtp_port_int)
            server.starttls()

        print("Підключення успішне. Вхід на сервер...")
        server.login(smtpLogin, senderPassword)
        print("Вхід успішний. Надсилання листа...")

        server.sendmail(senderEmail, receiver_emails_list, msg.as_string())

        print(f"Лист успішно відправлено до {', '.join(receiver_emails_list)}")
        return {"success": True}

    except smtplib.SMTPAuthenticationError:
        print("Помилка автентифікації SMTP: Неправильний логін або пароль.")
        return {"success": False, "error": "Помилка автентифікації: Неправильний логін або пароль."}
    except (smtplib.SMTPConnectError, ConnectionRefusedError, socket.gaierror) as e_connect:
        print(f"Помилка підключення до SMTP сервера {smtpServer}:{smtpPort}: {e_connect}")
        if isinstance(e_connect, socket.gaierror):
            error_message = f"Невідома адреса SMTP сервера: {smtpServer}"
        else:
            error_message = f"Помилка підключення до SMTP сервера: {e_connect}"
        return {"success": False, "error": error_message}
    except smtplib.SMTPException as e_smtp:
        print(f"Помилка SMTP: {e_smtp}")
        return {"success": False, "error": f"Помилка SMTP: {e_smtp}"}
    except Exception as e:
        print(f"Виникла неочікувана помилка при відправленні листа: {e}")
        return {"success": False, "error": f"Неочікувана помилка: {e}"}

    finally:
        if server:
            try:
                server.quit()
                print("З'єднання з SMTP сервером закрито.")
            except Exception as e_quit:
                print(f"Помилка при закритті SMTP з'єднання: {e_quit}")


@eel.expose
def ring_physical_bell(column_index):
    """
    Керує фізичним дзвінком через COM-порт, якщо для колонки
    не завантажено користувацький звук.
    Шукає перший доступний COM-порт та використовує його.
    Надсилає короткий сигнал на лінію DTR.

    :param column_index: Індекс колонки, для якої дзвонить дзвінок (1-4).
                         Не використовується в поточній реалізації сигналу,
                         але може бути корисно для логування.
    """
    global bell_serial_port

    print(f"Отримано запит на дзвінок фізичним дзвінком для колонки {column_index}...")

    SIGNAL_DURATION = 0.5

    if bell_serial_port is None or not bell_serial_port.isOpen():
        print("Порт не відкритий або був відключений. Шукаємо доступні порти...")
        ports = list(serial.tools.list_ports.comports())

        if not ports:
            print("Помилка: Доступні COM-порти не знайдені.")
            return {"success": False, "error": "COM-порт не знайдено"}

        chosen_port_info = ports[0]
        chosen_port_device = chosen_port_info.device
        print(f"Знайдено порти: {[p.device for p in ports]}. Вибрано: {chosen_port_device}")

        try:
            bell_serial_port = serial.Serial(chosen_port_device, baudrate=9600, timeout=0.1)
            print(f"COM-порт {chosen_port_device} успішно відкрито.")
            bell_serial_port.dtr = False
            bell_serial_port.rts = False
            time.sleep(0.1)

        except serial.SerialException as e:
            print(f"Помилка відкриття COM-порту {chosen_port_device}: {e}")
            bell_serial_port = None
            return {"success": False, "error": f"Помилка відкриття COM-порту: {e}"}
        except Exception as e:
            print(f"Неочікувана помилка при пошуку/відкритті COM-порту: {e}")
            bell_serial_port = None
            return {"success": False, "error": f"Неочікувана помилка COM-порту: {e}"}

    if bell_serial_port and bell_serial_port.isOpen():
        try:
            print(f"Надсилання сигналу дзвінка через {bell_serial_port.port}...")
            bell_serial_port.dtr = True
            time.sleep(SIGNAL_DURATION)
            bell_serial_port.dtr = False
            print("Сигнал дзвінка завершено.")
            return {"success": True}

        except serial.SerialException as e:
            print(f"Помилка при надсиланні сигналу через COM-порт: {e}")
            if bell_serial_port:
                try:
                    bell_serial_port.close()
                except:
                    pass
                bell_serial_port = None
            return {"success": False, "error": f"Помилка сигналу COM-порту: {e}"}
        except Exception as e:
            print(f"Неочікувана помилка при надсиланні сигналу дзвінка: {e}")
            return {"success": False, "error": f"Неочікувана помилка сигналу: {e}"}
    else:
        print("Порт не відкритий, сигнал не може бути надісланий (стан після помилки відкриття?).")
        return {"success": False, "error": "COM-порт не готовий"}


def run_flask():
    print(f"Flask сервер запущено на http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)


def run_eel():
    print(f"Eel сервер запущено. Доступно за адресою http://{EEL_HOST}:{EEL_PORT}")
    try:
        eel.start(
            "login.html",
            size=(900, 700),
            port=EEL_PORT,
            host=EEL_HOST,
            block=True,
        )
    except Exception as e:
        print(f"Помилка запуску Eel: {e}")
        print(
            "Переконайтесь, що в директорії 'web' є файл 'login.html' (або вказаний вами головний файл) та необхідні ресурси.")
        print("Можливо, порт Eel (19781) вже зайнятий.")


if __name__ == "__main__":
    if not os.path.exists("web"):
        print("Помилка: Директорія 'web' не знайдена.")
        print("Будь ласка, створіть директорію 'web' поруч з вашим Python скриптом і розмістіть там HTML/JS/CSS файли.")
        exit()

    main_html_file = "login.html"
    if not os.path.exists(os.path.join("web", main_html_file)):
        print(f"Помилка: Головний HTML файл '{main_html_file}' не знайдено в директорії 'web'.")
        exit()

    alerts_thread = threading.Thread(target=periodic_update_alerts, daemon=True)
    alerts_thread.start()
    print("Потік оновлення тривог запущено.")

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask потік запущено.")

    time.sleep(1)

    print("Запуск Eel...")
    run_eel()

    print("Eel завершив роботу.")

    if con:
        try:
            con.close()
            print("З'єднання з базою даних закрито.")
        except Exception as e:
            print(f"Помилка при закритті бази даних: {e}")

    if bell_serial_port and bell_serial_port.isOpen():
        try:
            bell_serial_port.close()
            print("COM-порт дзвінка закрито.")
        except Exception as e:
            print(f"Помилка при закритті COM-порту при завершенні: {e}")