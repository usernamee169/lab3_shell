import socket
import os
import threading

# Конфигурация
HOST = '0.0.0.0'
PORT = 8888
PASS_FILE = 'pass'
MESSAGES_DIR = 'messages'

# Создаем каталог для сообщений
if not os.path.exists(MESSAGES_DIR):
    os.makedirs(MESSAGES_DIR)

def load_users():
    """Загрузка пользователей из файла"""
    users = {}
    if os.path.exists(PASS_FILE):
        try:
            with open(PASS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            users[parts[0]] = parts[1]
        except Exception as e:
            print(f"Ошибка загрузки файла паролей: {e}")
    return users

users = load_users()
active_users = {}

def send_utf8(conn, message):
    """Отправка сообщения в UTF-8"""
    conn.send(message.encode('utf-8'))

def handle_client(conn, addr):
    print(f"Новое соединение: {addr}")
    current_user = None
    user_dir = None
    
    try:
        while True:
            # Получаем данные в UTF-8
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break
            
            parts = data.split(maxsplit=2)
            command = parts[0].lower() if parts else ""
            
            # auth user pass
            if command == "auth":
                if len(parts) != 3:
                    send_utf8(conn, "Ошибка: Используйте: auth user pass\n")
                    continue
                
                username = parts[1]
                password = parts[2]
                
                if username in users and users[username] == password:
                    current_user = username
                    user_dir = os.path.join(MESSAGES_DIR, username)
                    if not os.path.exists(user_dir):
                        os.makedirs(user_dir)
                    active_users[conn] = username
                    send_utf8(conn, "OK: Авторизация успешна\n")
                else:
                    send_utf8(conn, "Ошибка: Неверный логин или пароль\n")
            
            # list
            elif command == "list":
                if current_user is None:
                    send_utf8(conn, "Ошибка: Сначала авторизуйтесь\n")
                    continue
                
                files = os.listdir(user_dir)
                if not files:
                    send_utf8(conn, "Сообщений нет\n")
                else:
                    result = "Список сообщений:\n"
                    for i, filename in enumerate(sorted(files), 1):
                        try:
                            with open(os.path.join(user_dir, filename), 'r', encoding='utf-8') as f:
                                subject = f.readline().strip()
                            result += f"{i}. {subject}\n"
                        except:
                            result += f"{i}. Ошибка чтения сообщения\n"
                    send_utf8(conn, result)
            
            # read msg
            elif command == "read":
                if current_user is None:
                    send_utf8(conn, "Ошибка: Сначала авторизуйтесь\n")
                    continue
                
                if len(parts) != 2:
                    send_utf8(conn, "Ошибка: Используйте: read номер_сообщения\n")
                    continue
                
                try:
                    msg_num = int(parts[1])
                    files = sorted(os.listdir(user_dir))
                    if 1 <= msg_num <= len(files):
                        filename = files[msg_num - 1]
                        with open(os.path.join(user_dir, filename), 'r', encoding='utf-8') as f:
                            content = f.read()
                        send_utf8(conn, content)
                    else:
                        send_utf8(conn, f"Ошибка: Сообщение {msg_num} не найдено\n")
                except ValueError:
                    send_utf8(conn, "Ошибка: Неверный номер сообщения\n")
                except Exception as e:
                    send_utf8(conn, f"Ошибка: {str(e)}\n")
            
            # send user
            elif command == "send":
                if current_user is None:
                    send_utf8(conn, "Ошибка: Сначала авторизуйтесь\n")
                    continue
                
                if len(parts) != 2:
                    send_utf8(conn, "Ошибка: Используйте: send username\n")
                    continue
                
                recipient = parts[1]
                if recipient not in users:
                    send_utf8(conn, "Ошибка: Пользователь не существует\n")
                    continue
                
                send_utf8(conn, "Введите тему сообщения:\n")
                subject = conn.recv(1024).decode('utf-8').strip()
                
                send_utf8(conn, "Введите текст сообщения (окончание - точка на новой строке):\n")
                message_lines = []
                while True:
                    line = conn.recv(1024).decode('utf-8').strip()
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
                
                send_utf8(conn, f"OK: Сообщение отправлено {recipient}\n")
            
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
                send_utf8(conn, help_text)
            
            # exit
            elif command == "exit":
                send_utf8(conn, "До свидания!\n")
                break
            
            else:
                send_utf8(conn, "Неизвестная команда. Используйте help для справки\n")
    
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
        with open(PASS_FILE, 'w', encoding='utf-8') as f:
            f.write("user1 password1\n")
            f.write("user2 password2\n")
            f.write("админ пароль123\n")  # Русские имена тоже можно
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
