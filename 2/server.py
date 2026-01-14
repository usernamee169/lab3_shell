#!/usr/bin/env python3
import socket
import threading
import os
import hashlib

class MessageServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SOCK_REUSEADDR, 1)
        self.clients = {}
        self.load_passwords()
        
    def load_passwords(self):
        """Загрузка паролей из файла pass"""
        self.passwords = {}
        if os.path.exists('pass'):
            with open('pass', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            user = parts[0]
                            pass_hash = parts[1]
                            self.passwords[user] = pass_hash
    
    def authenticate(self, username, password):
        """Аутентификация пользователя"""
        if username in self.passwords:
            # Простая проверка - в реальной системе используйте безопасное хеширование
            return self.passwords[username] == hashlib.md5(password.encode()).hexdigest()
        return False
    
    def get_user_messages_dir(self, username):
        """Получение пути к каталогу сообщений пользователя"""
        dir_path = f"messages/{username}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        return dir_path
    
    def list_messages(self, username):
        """Получение списка сообщений пользователя"""
        messages = []
        messages_dir = self.get_user_messages_dir(username)
        
        for filename in os.listdir(messages_dir):
            if filename.endswith('.msg'):
                msg_num = filename[:-4]
                filepath = os.path.join(messages_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        subject = f.readline().strip()
                    messages.append((msg_num, subject))
                except:
                    pass
        
        return messages
    
    def read_message(self, username, msg_num):
        """Чтение конкретного сообщения"""
        messages_dir = self.get_user_messages_dir(username)
        filepath = os.path.join(messages_dir, f"{msg_num}.msg")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                return content
            except:
                return "Ошибка чтения сообщения"
        else:
            return "Сообщение не найдено"
    
    def send_message(self, from_user, to_user, subject, body):
        """Отправка сообщения пользователю"""
        # Проверяем, существует ли пользователь
        if to_user not in self.passwords:
            return False, f"Пользователь {to_user} не существует"
        
        # Получаем следующий номер сообщения для получателя
        messages_dir = self.get_user_messages_dir(to_user)
        existing_msgs = [f for f in os.listdir(messages_dir) if f.endswith('.msg')]
        
        if existing_msgs:
            msg_nums = [int(f[:-4]) for f in existing_msgs if f[:-4].isdigit()]
            next_num = max(msg_nums) + 1 if msg_nums else 1
        else:
            next_num = 1
        
        # Формируем полное сообщение
        full_message = f"От: {from_user}\nТема: {subject}\n\n{body}"
        
        # Сохраняем сообщение
        filepath = os.path.join(messages_dir, f"{next_num}.msg")
        try:
            with open(filepath, 'w') as f:
                f.write(full_message)
            return True, f"Сообщение отправлено {to_user}, номер: {next_num}"
        except Exception as e:
            return False, f"Ошибка отправки: {str(e)}"
    
    def handle_client(self, client_socket, address):
        """Обработка клиентского соединения"""
        print(f"[+] Подключен клиент {address}")
        current_user = None
        
        try:
            client_socket.sendall(b"Добро пожаловать в систему сообщений!\n")
            client_socket.sendall(b"Для справки введите help\n")
            
            while True:
                # Отправляем приглашение для ввода
                if current_user:
                    prompt = f"{current_user}> "
                else:
                    prompt = "> "
                
                client_socket.sendall(prompt.encode())
                
                # Получаем команду
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break
                
                parts = data.split()
                command = parts[0].lower() if parts else ""
                
                # Обработка команд
                if command == "auth" and len(parts) == 3:
                    username = parts[1]
                    password = parts[2]
                    
                    if self.authenticate(username, password):
                        current_user = username
                        response = f"Успешная авторизация как {username}\n"
                    else:
                        response = "Ошибка авторизации. Неверное имя пользователя или пароль\n"
                
                elif command == "list":
                    if not current_user:
                        response = "Сначала выполните авторизацию (auth user pass)\n"
                    else:
                        messages = self.list_messages(current_user)
                        if messages:
                            response = "Ваши сообщения:\n"
                            for msg_num, subject in messages:
                                response += f"  {msg_num}: {subject}\n"
                        else:
                            response = "Сообщений нет\n"
                
                elif command == "read" and len(parts) == 2:
                    if not current_user:
                        response = "Сначала выполните авторизацию (auth user pass)\n"
                    else:
                        msg_num = parts[1]
                        message_content = self.read_message(current_user, msg_num)
                        response = message_content + "\n"
                
                elif command == "send" and len(parts) == 2:
                    if not current_user:
                        response = "Сначала выполните авторизацию (auth user pass)\n"
                    else:
                        to_user = parts[1]
                        client_socket.sendall(b"Введите тему сообщения: ")
                        subject = client_socket.recv(1024).decode().strip()
                        
                        client_socket.sendall(b"Введите текст сообщения (завершите точкой на отдельной строке):\n")
                        body_lines = []
                        while True:
                            line = client_socket.recv(1024).decode()
                            if line.strip() == ".":
                                break
                            body_lines.append(line)
                        
                        body = "".join(body_lines)
                        success, result = self.send_message(current_user, to_user, subject, body)
                        response = result + "\n"
                
                elif command == "exit":
                    response = "До свидания!\n"
                    client_socket.sendall(response.encode())
                    break
                
                elif command == "help":
                    response = """Доступные команды:
  auth <user> <pass> - авторизация
  list - показать список сообщений
  read <msg_num> - прочитать сообщение
  send <user> - отправить сообщение пользователю
  exit - выход
  help - эта справка\n"""
                
                else:
                    response = f"Неизвестная команда или неверные параметры: {data}\nИспользуйте help для справки\n"
                
                client_socket.sendall(response.encode())
        
        except ConnectionResetError:
            print(f"[-] Клиент {address} отключился")
        except Exception as e:
            print(f"Ошибка при обработке клиента {address}: {e}")
        finally:
            client_socket.close()
            print(f"[-] Отключен клиент {address}")
    
    def start(self):
        """Запуск сервера"""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Сервер запущен на {self.host}:{self.port}")
            print("Ожидание подключений...")
            
            while True:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nСервер остановлен")
        except Exception as e:
            print(f"Ошибка сервера: {e}")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = MessageServer()
    server.start()
