import socket

host, port = '127.0.0.1', 8888
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))  # инициация соединения с сервером
print('Подключено к серверу')

try:
    while True:
        message = input('Введите параметры (a h) или (a b угол), exit для выхода:\n> ')
        if message.lower() == 'exit':
            break
        client_socket.sendall(message.encode('utf-8'))
        data = client_socket.recv(1024).decode('utf-8')
        print(f'Ответ сервера: {data}')
finally:
    client_socket.close()
    print('Соединение закрыто.')