import socket
from math import sin, radians

host, port = '127.0.0.1', 8888

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((host, port))
server_socket.listen(1)
print(f'Сервер запущен на {host}:{port}')

conn, address = server_socket.accept()  # принятие запроса на подключение от клиента
print(f'Подключено: {address}')

try:
    while True:
        data = conn.recv(1024).decode('utf-8')  # получение данных
        if not data:
            break

        parts = data.split()
        try:
            if len(parts) == 2:
                a, h = map(float, parts)
                answer = a * h
            elif len(parts) == 3:
                a, b, angle = map(float, parts)
                answer = a * b * sin(radians(angle))
            else:
                conn.sendall("Нужно 2 или 3 числа через пробел".encode('utf-8'))
                continue
            conn.sendall(f'Площадь равна: {answer}'.encode('utf-8'))
        except ValueError:
            conn.sendall("Ошибка: введите числа".encode('utf-8'))
finally:
    conn.close()
    server_socket.close()
    print('Сервер остановлен.')