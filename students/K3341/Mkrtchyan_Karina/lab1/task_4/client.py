import socket
import threading

host = '127.0.0.1'
port = 9090
encoding = 'utf-8'


def receive_loop(sock):
    """Постоянно слушаем сервер в отдельном потоке, пока он не закроет связь."""
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break  # сокет уже закрыт нашей же main()
        if not data:
            print('\n[СИСТЕМА] Соединение с сервером закрыто.')
            break
        # печатаем ответ сервера
        print('\r' + data.decode(encoding).rstrip())


def main():
    # клиентский TCP-сокет и подключение к серверу
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f'Подключено к {host}:{port}')

    # первое сообщение от сервера — запрос имени, отвечаем до старта потока
    print(sock.recv(1024).decode(encoding), end='')
    sock.sendall(input().strip().encode(encoding))

    # поток принимает чужие сообщения, пока мы сами печатаем в терминал
    threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

    print('Введите сообщение (или /quit для выхода):')
    try:
        while True:
            text = input().strip()
            if not text:
                continue  # игнорируем переносы строки
            if text == '/quit':
                sock.sendall(b'/quit')  # команда выхода, которую ждёт сервер
                break
            sock.sendall(text.encode(encoding))  # остальное — просто текст в общий чат
    except (KeyboardInterrupt, EOFError):
        pass  # ctrl+f2 или конец ввода — выход
    finally:
        sock.close()
        print('Вы вышли из чата.')


if __name__ == '__main__':
    main()
