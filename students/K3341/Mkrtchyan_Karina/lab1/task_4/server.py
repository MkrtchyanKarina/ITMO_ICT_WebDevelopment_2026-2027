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
            except:
                client.close()
                if client in clients:
                    clients.remove(client)


def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            broadcast(message, client)
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
        thread.daemon = True
        thread.start()


if __name__ == '__main__':
    receive()
