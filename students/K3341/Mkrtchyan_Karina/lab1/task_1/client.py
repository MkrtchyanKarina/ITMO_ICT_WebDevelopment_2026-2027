import socket

host = '127.0.0.1'
port = 8888
server_addr = (host, port)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.connect((host, port))
try:
    for _ in range(5):
        message = "Hello, server!"
        client_socket.sendto(message.encode('utf-8'), server_addr)  # отправка данных

        data, server_addr = client_socket.recvfrom(1024)  # получение данных
        reply = data.decode('utf-8')

        print(f"Отправлено: {message} | Получено: {reply}")
finally:
    client_socket.close()

