import eel
import requests

eel.init('front')  # Папка з вашими html/js файлами

@eel.expose
def send_lesson_data_to_other_site(schedule):
    """
    schedule – список списків (розклад),
    який нам прилітає з JavaScript (через eel).
    """
    try:
        # Приклад POST-запиту на інший сайт (IP:port):
        url = "http://localhost:63342/pythonProject/.venv/lib/front/3site.html?_ijt=rvtr1d4q4fn0v89lvh2v3pknoj&_ij_reload=RELOAD_ON_SAVE"
        response = requests.post(url, json=schedule, timeout=5)
        if response.status_code == 200:
            return "Розклад успішно відправлено!"
        else:
            return f"Помилка при відправці: {response.status_code}"
    except Exception as e:
        return f"Виникла помилка: {str(e)}"

eel.start('index.html', size=(1000,800))
