import socket
import threading

host = '127.0.0.1'
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []  # список подключенных клиентов


def broadcast(message, sender):
    for client in clients:
        if client != sender:
            try:
                client.send(message)
            except:  # если клиент отключен, можем его удалить из списка и закрыть сокет
                client.close()
                if client in clients:
                    clients.remove(client)


def handle_client(client):
    while True:
        try:
            message = client.recv(1024)  # получаем сообщение от клиента
            if not message:
                break
            broadcast(message, client)  # делаем рассылку всем, кроме него
        except:
            if client in clients:
                clients.remove(client)
            client.close()
            break


def receive():
    print(f"Сервер запущен на {host}:{port}")
    while True:
        client, address = server.accept()
        print(f"Подключено: {address}")

        clients.append(client)

        # запуск отдельного потока для клиента
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.daemon = True  # чтобы при отключении сервера, потоки для пользователей завершились
        thread.start()


if __name__ == '__main__':
    receive()
