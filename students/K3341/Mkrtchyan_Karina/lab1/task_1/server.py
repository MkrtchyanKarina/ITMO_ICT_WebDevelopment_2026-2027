import socket


host = '127.0.0.1'
port = 8888
# создание UDP-сокета: AF_INET - IPv4, SOCK_DGRAM - UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# связь сокета с адресом и портом
server_socket.bind((host, port))
print(f"UDP-сервер запущен на {host}:{port}")

# обмен сообщениями
try:
    while True:
        # получение данных и адреса клиента (размер буфера 1024 байта)
        data, client_addr = server_socket.recvfrom(1024)
        message = data.decode('utf-8')

        reply = "Hello, client!"
        server_socket.sendto(reply.encode('utf-8'), client_addr)
        print(f"Получено: {message} | Отправлено: {reply}")
finally:
    server_socket.close()
