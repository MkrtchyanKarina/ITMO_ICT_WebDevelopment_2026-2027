import socket
from html import escape
from urllib.parse import parse_qs

host = '127.0.0.1'
port = 8080

# журнал в памяти процесса: дисциплина (str) : список оценок (list[int]).
journal = {}


# страница журнала

def render_table() -> str:
    """Таблица со всеми оценками, сгруппированными по дисциплине (по алфавиту)."""
    if not journal:
        return '<p>Журнал пока пуст.</p>'

    rows = []
    for subject in sorted(journal):
        grades = journal[subject]
        average = sum(grades) / len(grades)  # средний балл по дисциплине
        rows.append(
            '<tr>'
            f'<td>{escape(subject)}</td>'  # escape — чтобы спецсимволы из формы не ломали HTML
            f'<td>{", ".join(map(str, grades))}</td>'
            f'<td>{len(grades)}</td>'
            f'<td>{average:.2f}</td>'
            '</tr>'
        )

    return (
        '<table border="1" cellpadding="8" cellspacing="0">'
        '<tr><th>Дисциплина</th><th>Оценки</th><th>Кол-во</th><th>Средний балл</th></tr>'
        + ''.join(rows) +
        '</table>'
    )


def render_page() -> bytes:
    """Вся страница журнала: таблица с оценками + форма для добавления."""
    table = render_table()
    page = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Журнал оценок</title>
</head>
<body>
    <h1>Журнал оценок</h1>
    {table}
    <hr>
    <h2>Добавить оценку</h2>
    <!-- Форма отправляет POST на /submit: браузер сам кодирует поля в urlencoded -->
    <form method="POST" action="/submit">
        <label>Дисциплина:
            <input type="text" name="subject" required>
        </label><br><br>
        <label>Оценка:
            <select name="grade">
                <option>5</option>
                <option>4</option>
                <option>3</option>
                <option>2</option>
            </select>
        </label><br><br>
        <button type="submit">Добавить</button>
    </form>
</body>
</html>'''
    return page.encode('utf-8')


# сборка ответа и чтение запроса

def build_response(status='200 OK', body=b'', content_type='text/html; charset=utf-8',
                   location=None) -> bytes:
    """Собрать ответ: строка статуса + заголовки + пустая строка + тело."""
    if isinstance(body, str):
        body = body.encode('utf-8')

    # заголовок Location нужен для редиректов
    redirect = f'Location: {location}\r\n' if location else ''

    head = (
        f'HTTP/1.1 {status}\r\n'
        f'Content-Type: {content_type}\r\n'
        f'Content-Length: {len(body)}\r\n' 
        f'Connection: close\r\n'            
        f'{redirect}'
        f'\r\n'
    )
    return head.encode('utf-8') + body


def error_response(status, message) -> bytes:
    """Короткая HTML-страница с ошибкой."""
    return build_response(status, f'<h1>{status}</h1><p>{escape(message)}</p>')


def read_request(conn) -> dict | None:
    """Прочитать запрос целиком (заголовки + тело). None — клиент закрыл связь молча."""
    buffer = b''

    # 1. Читаем, пока не увидим пустую строку \r\n\r\n — это конец заголовков
    while b'\r\n\r\n' not in buffer:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        buffer += chunk

    head, _, body = buffer.partition(b'\r\n\r\n')  # partition разрезает buffer по первому вхождению \r\n\r\n на три части
    lines = head.decode('utf-8', errors='replace').split('\r\n')

    # 2. Первая строка: "МЕТОД /путь HTTP/1.1"
    method, path, _ = lines[0].split(' ', 2)
    path = path.split('?')[0]

    # 3. Заголовки в словарь
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(':')
        if name:
            headers[name.strip().lower()] = value.strip()

    # 4. Для POST дочитываем тело до Content-Length: TCP не соблюдает границы сообщений
    #    и может прислать всё в одном recv() (или оборваться на середине)
    if method == 'POST':
        content_length = int(headers.get('content-length', 0))
        while len(body) < content_length:
            chunk = conn.recv(4096)
            if not chunk:
                break
            body += chunk

    return {
        'method': method,
        'path': path,
        'body': body.decode('utf-8', errors='replace'),
    }


def parse_form(body: str) -> dict:
    """Разбор данных из формы в словарь"""
    return {name: values[0] for name, values in parse_qs(body, keep_blank_values=True).items()}


def parse_grade(raw: str) -> int | None:
    """Оценка из формы: целое число 1..5, иначе None (значит, запрос некорректный)."""
    if not raw.isdigit():
        return None
    grade = int(raw)
    return grade if 1 <= grade <= 5 else None


# маршрутизация

def route(request: dict) -> bytes:
    """Готовый HTTP-ответ на запрос: GET / — страница, POST /submit — новая оценка."""
    method, path, body = request['method'], request['path'], request['body']

    # GET / — отдаём страницу со списком оценок
    if method == 'GET' and path == '/':
        return build_response(body=render_page())

    # POST /submit — принимаем дисциплину и оценку из формы
    if method == 'POST' and path == '/submit':
        form = parse_form(body)
        subject = form.get('subject', '').strip()
        grade = parse_grade(form.get('grade', '').strip())

        # Валидация: сначала проверяем поля, потом меняем журнал
        if not subject:
            return error_response('400 Bad Request', 'Дисциплина не может быть пустой')
        if grade is None:
            return error_response('400 Bad Request', 'Оценка должна быть целым числом от 1 до 5')

        # setdefault: создаём список оценок, если такой дисциплины ещё не было
        journal.setdefault(subject, []).append(grade)
        print(f'  добавлено: "{subject}" = {grade}')

        # PRG: после POST отвечаем редиректом на GET /, иначе F5 повторит отправку формы
        return build_response('303 See Other', location='/')

    return error_response('404 Not Found', 'Такой страницы нет')


def handle_client(conn, addr):
    """Прочитать один запрос и отправить на него ответ."""
    # таймаут: однопоточный сервер не должен зависать на «молчащем» клиенте (например, сканере порта)
    conn.settimeout(10)
    try:
        request = read_request(conn)
        if request is None:
            return  # соединение закрыто
        print(f'{addr} -> {request["method"]} {request["path"]}')
        conn.sendall(route(request))

    except Exception as e:
        print(f'[!] Ошибка при обработке {addr}: {e}')
        try:
            conn.sendall(error_response('500 Internal Server Error', 'Внутренняя ошибка сервера'))
        except OSError:
            pass

    finally:
        conn.close()


def main():
    # слушающий сокет: AF_INET — IPv4, SOCK_STREAM — TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # перезапуск без залипания порта
        server.bind((host, port))
        server.listen()
        print(f'Сервер запущен: http://{host}:{port}')

        try:
            while True:
                conn, addr = server.accept()  # блокируем, пока кто-то не подключится
                handle_client(conn, addr)
        except KeyboardInterrupt:
            print('\nОстановка сервера...')


if __name__ == '__main__':
    main()
