import socket
import os
import threading

# Конфигурация
HOST = '0.0.0.0'  # Все интерфейсы
PORT = 8888
PASS_FILE = 'pass'
MESSAGES_DIR = 'messages'

# Создаем каталог для сообщений
if not os.path.exists(MESSAGES_DIR):
    os.makedirs(MESSAGES_DIR)

# Загрузка пользователей
def load_users():
    users = {}
    if os.path.exists(PASS_FILE):
        with open(PASS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        users[parts[0]] = parts[1]
    return users

users = load_users()

# Словарь активных пользователей {сокет: username}
active_users = {}

def handle_client(conn, addr):
    print(f"Новое соединение: {addr}")
    current_user = None
    user_dir = None
    
    try:
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            
            parts = data.split(maxsplit=2)
            command = parts[0].lower() if parts else ""
            
            # auth user pass
            if command == "auth":
                if len(parts) != 3:
                    conn.send(b"Ошибка: Используйте: auth user pass\n")
                    continue
                
                username = parts[1]
                password = parts[2]
                
                if username in users and users[username] == password:
                    current_user = username
                    user_dir = os.path.join(MESSAGES_DIR, username)
                    if not os.path.exists(user_dir):
                        os.makedirs(user_dir)
                    active_users[conn] = username
                    conn.send(b"OK: Авторизация успешна\n")
                else:
                    conn.send(b"Ошибка: Неверный логин или пароль\n")
            
            # list
            elif command == "list":
                if current_user is None:
                    conn.send(b"Ошибка: Сначала авторизуйтесь\n")
                    continue
                
                files = os.listdir(user_dir)
                if not files:
                    conn.send(b"Сообщений нет\n")
                else:
                    result = "Список сообщений:\n"
                    for i, filename in enumerate(sorted(files), 1):
                        with open(os.path.join(user_dir, filename), 'r', encoding='utf-8') as f:
                            subject = f.readline().strip()
                        result += f"{i}. {subject}\n"
                    conn.send(result.encode())
            
            # read msg
            elif command == "read":
                if current_user is None:
                    conn.send(b"Ошибка: Сначала авторизуйтесь\n")
                    continue
                
                if len(parts) != 2:
                    conn.send(b"Ошибка: Используйте: read номер_сообщения\n")
                    continue
                
                try:
                    msg_num = int(parts[1])
                    files = sorted(os.listdir(user_dir))
                    if 1 <= msg_num <= len(files):
                        filename = files[msg_num - 1]
                        with open(os.path.join(user_dir, filename), 'r', encoding='utf-8') as f:
                            content = f.read()
                        conn.send(content.encode())
                    else:
                        conn.send(f"Ошибка: Сообщение {msg_num} не найдено\n".encode())
                except ValueError:
                    conn.send(b"Ошибка: Неверный номер сообщения\n")
            
            # send user
            elif command == "send":
                if current_user is None:
                    conn.send(b"Ошибка: Сначала авторизуйтесь\n")
                    continue
                
                if len(parts) != 2:
                    conn.send(b"Ошибка: Используйте: send username\n")
                    continue
                
                recipient = parts[1]
                if recipient not in users:
                    conn.send(b"Ошибка: Пользователь не существует\n")
                    continue
                
                conn.send(b"Введите тему сообщения:\n")
                subject = conn.recv(1024).decode().strip()
                
                conn.send(b"Введите текст сообщения (окончание - точка на новой строке):\n")
                message_lines = []
                while True:
                    line = conn.recv(1024).decode().strip()
                    if line == ".":
                        break
                    message_lines.append(line)
                
                # Сохраняем сообщение
                recipient_dir = os.path.join(MESSAGES_DIR, recipient)
                if not os.path.exists(recipient_dir):
                    os.makedirs(recipient_dir)
                
                # Генерируем имя файла
                existing = len(os.listdir(recipient_dir))
                filename = f"msg_{existing + 1}.txt"
                
                with open(os.path.join(recipient_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(f"Тема: {subject}\n")
                    f.write(f"От: {current_user}\n")
                    f.write("\n")
                    f.write("\n".join(message_lines))
                
                conn.send(f"OK: Сообщение отправлено {recipient}\n".encode())
            
            # help
            elif command == "help":
                help_text = """
Доступные команды:
auth user pass - авторизация
list - показать список сообщений
read номер - прочитать сообщение по номеру
send user - отправить сообщение пользователю
exit - выход
help - эта справка
"""
                conn.send(help_text.encode())
            
            # exit
            elif command == "exit":
                conn.send(b"До свидания!\n")
                break
            
            else:
                conn.send(b"Неизвестная команда. Используйте help для справки\n")
    
    except ConnectionError:
        print(f"Соединение с {addr} разорвано")
    finally:
        if conn in active_users:
            del active_users[conn]
        conn.close()
        print(f"Соединение с {addr} закрыто")

def main():
    # Создаем файл с пользователями, если его нет
    if not os.path.exists(PASS_FILE):
        with open(PASS_FILE, 'w') as f:
            f.write("user1 password1\n")
            f.write("user2 password2\n")
        print(f"Создан файл {PASS_FILE} с тестовыми пользователями")
    
    # Запускаем сервер
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Сервер запущен на {HOST}:{PORT}")
        print("Ожидание подключений...")
        
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()

if __name__ == "__main__":
    main()
