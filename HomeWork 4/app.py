from flask import Flask, render_template, request, redirect, url_for
import json
import socket
import threading
from datetime import datetime

app = Flask(__name__)

# Маршрут для главной страницы
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для страницы сообщения
@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        # Получение данных из формы
        username = request.form.get('username')
        message = request.form.get('message')

        # Отправка данных на Socket-сервер
        data = {
            'username': username,
            'message': message
        }
        send_message(data)

        return redirect(url_for('index'))

    return render_template('message.html')

# Отправка сообщения на Socket-сервер
def send_message(data):
    # Преобразование данных в байтовую строку
    message = json.dumps(data).encode()

    # Отправка сообщения на UDP-сокет
    UDP_IP = '127.0.0.1'  # IP-адрес Socket-сервера
    UDP_PORT = 5000  # Порт Socket-сервера

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message, (UDP_IP, UDP_PORT))

# Запуск HTTP-сервера и Socket-сервера в разных потоках
if __name__ == '__main__':
    # Запуск HTTP-сервера
    http_thread = threading.Thread(target=app.run, kwargs={'port': 3000})
    http_thread.start()

    # Запуск Socket-сервера
    def socket_server():
        UDP_IP = '127.0.0.1'  # IP-адрес Socket-сервера
        UDP_PORT = 5000  # Порт Socket-сервера

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((UDP_IP, UDP_PORT))
            while True:
                data, addr = sock.recvfrom(1024)
                data = json.loads(data.decode())

                # Добавление времени получения сообщения
                data['timestamp'] = str(datetime.now())

                # Сохранение данных в файл data.json
                with open('storage/data.json', 'a') as file:
                    file.write(json.dumps(data) + '\n')

    socket_thread = threading.Thread(target=socket_server)
    socket_thread.start()
