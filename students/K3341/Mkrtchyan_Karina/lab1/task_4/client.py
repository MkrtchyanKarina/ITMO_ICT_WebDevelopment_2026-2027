import socket
import threading

host = '127.0.0.1'
port = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

name = input("Введите ваше имя: ")

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except:
            print("Соединение с сервером разорвано.")
            client.close()
            break

def send_messages():
    # отправляем имя при подключении
    while True:
        message = input()
        if message.lower() == 'exit':
            client.close()
            break
        full_message = f"{name}: {message}"
        try:
            client.send(full_message.encode('utf-8'))
        except:
            break

# запуск потока для приема сообщений
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# запуск отправки сообщений в главном потоке
send_messages()
