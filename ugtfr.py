import socket


def get_wifi_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:

        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

IP = get_wifi_ip()
PORT = 19779

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind((IP, PORT))
listener.listen(0)

print(f"Server запущено на {IP}:{PORT}")

connection, address = listener.accept()
print(f"З'єднання встановлено з {address}")

connection.send("Привіт, підключайся!".encode('utf8'))

while True:
    try:
        data_output = ""
        while True:
            data = connection.recv(1024).decode("utf8")
            if not data:
                break
            data_output += data

        if data_output:
            print(f"Отримано: {data_output}")
        else:
            print("Клієнт закрив з'єднання")
            break

    except socket.timeout:
        print("Таймаут з'єднання")
        break
    except KeyboardInterrupt:
        print("Робота сервера завершена вручну")
        break
    except Exception as e:
        print(f"Сталася помилка: {e}")
        break

connection.close()
listener.close()
