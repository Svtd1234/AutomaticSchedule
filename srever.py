import eel
import json
import os

# Ініціалізуємо Eel з папкою 'web'
eel.init('web')

# Глобальні змінні для зберігання розкладу та вибору області
saved_schedule = []
selected_oblast = None

# Файл для збереження розкладу
DATA_FILE = 'schedule.json'


@eel.expose
def send_lesson_data(schedule):
    """
    Приймає розклад з index.html та зберігає його.
    """
    global saved_schedule
    saved_schedule = schedule
    save_schedule_to_file()
    print("Розклад збережено:", saved_schedule)
    return "Розклад успішно збережено!"


@eel.expose
def get_saved_schedule():
    """
    Повертає збережений розклад для 3site.html
    """
    return saved_schedule


@eel.expose
def process_selection(oblast_id):
    """
    Приймає вибір області з index.html та зберігає його.
    """
    global selected_oblast
    selected_oblast = oblast_id
    print(f"Обрана область: {selected_oblast}")
    return f"Область {selected_oblast} збережена!"


@eel.expose
def notify_3site_ready():
    """
    Викликається з 3site.html, коли вона готова приймати дані.
    """
    print("3site.html готовий приймати дані.")
    if saved_schedule:
        eel.fill_table_on_3site(saved_schedule)
    if selected_oblast:
        eel.display_selected_oblast(selected_oblast)


def save_schedule_to_file():
    """
    Зберігає розклад у файл.
    """
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(saved_schedule, f, ensure_ascii=False, indent=4)
        print(f"Розклад збережено у файл {DATA_FILE}")


def load_schedule_from_file():
    """
    Завантажує розклад з файлу, якщо він існує.
    """
    global saved_schedule
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            saved_schedule = json.load(f)
            print("Розклад завантажено з файлу.")
    else:
        print("Файл розкладу не знайдено.")


def start_eel():
    # Завантажуємо розклад з файлу при запуску
    load_schedule_from_file()

    # Запускаємо основне вікно (index.html) у неблокуючому режимі
    eel.start('index.html', size=(1200, 800), port=8080, block=False)

    # Запускаємо додаткове вікно (3site.html) у неблокуючому режимі
    eel.start('3site.html', size=(800, 600), block=False)

    # Утримуємо програму відкритою
    while True:
        eel.sleep(10)


if __name__ == '__main__':
    start_eel()
