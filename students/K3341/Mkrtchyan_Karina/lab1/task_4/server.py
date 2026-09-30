import socket
import threading

host = '127.0.0.1'
port = 9090
encoding = 'utf-8'

# словарь активных клиентов: {сокет: имя}, общий для всех потоков -> доступен только под локом
clients = {}
lock = threading.Lock()


def send(conn, text):
    """Отправить одному клиенту текст (предварительно кодируем в байты)."""
    conn.sendall(text.encode(encoding))


def broadcast(message, exclude=None):
    """Отправить сообщение всем клиентам, кроме exclude (если он задан)."""
    data = message.encode(encoding)
    # копируем список под локом, чтобы рассылка шла по неизмененным ключам в словаре клиентов
    with lock:
        targets = list(clients)
    for conn in targets:
        if conn is exclude:  # если клиент отправил данное сообщение, то мы ему ничего не отправляем в ответ
            continue
        try:
            conn.sendall(data)
        except OSError:  # если нет соединения, то поток сам уберет клиента
            pass


def handle_client(conn, addr):
    """Обслуживание одного клиента в отдельном потоке."""
    name = f'user_{addr[1]}'  # запасное имя на случай, если клиент пришлёт пустую строку
    peer = f'{addr[0]}:{addr[1]}'  # адрес клиента строкой, чтобы в логах не было скобок кортежа
    print(f'[+] Подключение: {peer}')

    try:
        # 1. Регистрация: спрашиваем имя и запоминаем сокет в общем словаре
        send(conn, 'Введите имя: ')
        name = conn.recv(1024).decode(encoding).strip() or name
        with lock:
            clients[conn] = name
        print(f'[+] {name} ({peer}) вошёл в чат')

        # 2. Приветствия: остальным — о новом клиенте, ему — счётчик участников
        broadcast(f'[СИСТЕМА] {name} присоединился к чату\n', exclude=conn)
        send(conn, f'[СИСТЕМА] Добро пожаловать, {name}!\n')
        with lock:
            count = len(clients)
        broadcast(f'[СИСТЕМА] Сейчас в чате: {count} чел.\n')

        # 3. Основной цикл: читаем сообщение клиента и рассылаем его остальным
        while True:
            data = conn.recv(1024)
            if not data:
                break  # пустой recv() = клиент закрыл соединение

            text = data.decode(encoding).strip()
            if not text:
                continue  # пустые Enter'ы игнорируем
            if text == '/quit':
                break  # выход по команде

            print(f'{name}: {text}')
            broadcast(f'[{name}] {text}\n', exclude=conn)

    except OSError as e:
        print(f'[!] Ошибка у {peer}: {e}')

    finally:
        # 4. Выход: убираем клиента и один раз сообщаем остальным, что он ушёл
        with lock:
            clients.pop(conn, None)  # мог быть удалён раньше
        broadcast(f'[СИСТЕМА] {name} покинул чат\n')
        print(f'[-] {name} ({peer}) отключился')
        conn.close()


def main():
    # слушающий сокет: AF_INET — IPv4, SOCK_STREAM — TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        # ждём подключения не дольше 0.5 с, иначе Ctrl+C не смог бы прервать accept()
        server.settimeout(0.5)
        print(f'Сервер чата запущен на {host}:{port}')

        try:
            while True:
                try:
                    conn, addr = server.accept()  # блокируем сервер, пока кто-то не подключится
                except socket.timeout:
                    continue  # подключения не было, просто начинаем ждать заново
                # на каждого клиента — свой поток (демон, чтобы не блокировал выход)
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print('Остановка сервера...')
            # разрываем все соединения
            with lock:
                for conn in clients:
                    conn.close()


if __name__ == '__main__':
    main()
