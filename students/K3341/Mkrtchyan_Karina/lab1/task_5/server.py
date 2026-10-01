import socket
import urllib.parse


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 8080

server_socket.bind((host, port))
server_socket.listen()
print(f"Сервер запущен на: http://{host}:{port}/")

journal = {}

form = """HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>
<head><title>Форма ввода</title></head>
<body>
    <h1>Журнал оценок</h1>
    {marks_list}
    
    <h2>Добавить оценку:</h2>
    
    <form method="POST" action="/">
    
        <label>Предмет:
        <input type="text" name="subject" list="subjects" placeholder="Предмет" required>
    
        <datalist id="subjects">
            <option value="математика">
            <option value="русский язык">
            <option value="физика">
            <option value="литература">
            <option value="английский язык">
        </datalist>
    </label>
    
        <label>Оценка:
            <select name="mark">
                <option>5</option>
                <option>4</option>
                <option>3</option>
                <option>2</option>
            </select>
        </label>
        <button type="submit">Отправить</button>
    </form>
</body>
</html>
"""

result = """HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>
<head><title>Результат</title></head>
<body>
    <h2>По предмету {subject} выставлена оценка {mark}</h2>
    <p>Данные успешно получены</p>
    <a href="/">Назад к форме</a>
</body>
</html>
"""

try:
    while True:
        # ожидаем подключения клиента
        client_socket, client_address = server_socket.accept()

        # читаем данные от клиента (запрос)

        request_data = b""
        while b"\r\n\r\n" not in request_data:
            part = client_socket.recv(1024)
            if not part:
                break
            request_data += part

        headers, body = request_data.split(b"\r\n\r\n")  # тело запроса идет после двойного переноса строки, поэтому мы разделаем данные через '\r\n\r\n'
        headers = headers.decode("utf-8").split('\r\n')
        method, path, version = headers[0].split()
        print(f"Получен запрос от {client_address}:")

        print()  # выводим заголовок

        if method == "POST":
            content_length = int([s for s in headers if s.startswith("Content-Length: ")][0].split()[1])
            while len(body) < content_length:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                body += chunk
            if body:
                body = body.decode("utf-8")
                parsed_body = urllib.parse.parse_qs(body)
                # Извлекаем значение поля 'subject' и 'mark'
                subject = parsed_body.get('subject', ['None'])[0]
                mark = parsed_body.get('mark', ['None'])[0]
                if subject in journal:
                    journal[subject].append(mark)
                else:
                    journal[subject] = [mark]

            else:
                subject = "None"
                mark = "-"

            response = result.format(subject=subject, mark=mark).encode('utf-8')

        elif method == "GET":

            marks_list = "<ul>\n"
            for key, value in journal.items():
                marks_list += f"  <li><b>{key}:</b> {', '.join(value)}</li>\n"
            marks_list += "</ul>"

            response = form.format(marks_list=marks_list).encode('utf-8')

        else:
            response = form.format("<h1>Ошибка!</h1>").encode('utf-8')

        client_socket.sendall(response)
        client_socket.close()
finally:
    server_socket.close()