import socket
import os

host = '127.0.0.1'
port = 8080

base_dir = os.path.dirname(os.path.abspath(__file__))  # ищем путь до папки (task_3)
html_path = os.path.join(base_dir, 'index.html')  # находим файл index.html

# чтение файла
with open(html_path, 'rb') as f:
    body = f.read()

headers = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=utf-8\r\n"
    f"Content-Length: {len(body)}\r\n"
    "Connection: close\r\n"
    "\r\n"
).encode('utf-8')

response = headers + body

# создание TCP-сокета
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# связь сокета с портом и адресом
server.bind((host, port))

server.listen(1)
print(f'Сервер запущен на http://{host}:{port}/')

try:
    while True:
        conn, addr = server.accept()
        print(f'Подключение: {addr}')
        try:
            conn.recv(1024)              # чтение запросв
            conn.sendall(response)       # передача данных одним пакетом
        finally:
            conn.close()
except KeyboardInterrupt:  # ctrl + f2
    print('Остановка сервера')
finally:
    server.close()