#!/usr/bin/env python3
import os
import socket
import mimetypes
import datetime
import sys
import threading
import time

class SimpleProtocolServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.pass_file = 'pass.txt'
        self.current_dir = os.getcwd()
        self.authenticated = False
        self.current_user = None
        self.server_socket = None
        self.running = True
        
    def load_users(self):
        """Загрузка пользователей из файла"""
        users = {}
        if os.path.exists(self.pass_file):
            with open(self.pass_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            users[parts[0]] = parts[1]
        return users
    
    def handle_auth(self, username, password):
        """Обработка авторизации"""
        users = self.load_users()
        if username in users and users[username] == password:
            self.authenticated = True
            self.current_user = username
            return "OK: Авторизация успешна"
        else:
            return "ERROR: Неверное имя пользователя или пароль"
    
    def handle_list(self):
        """Получение списка файлов"""
        if not self.authenticated:
            return "ERROR: Требуется авторизация"
        
        files = os.listdir(self.current_dir)
        result = []
        for file in files:
            if os.path.isfile(file):
                result.append(f"FILE: {file}")
            else:
                result.append(f"DIR:  {file}")
        return "\n".join(result) if result else "Каталог пуст"
    
    def handle_info(self, filename):
        """Получение информации о файле"""
        if not self.authenticated:
            return "ERROR: Требуется авторизация"
        
        filepath = os.path.join(self.current_dir, filename)
        if not os.path.exists(filepath):
            return f"ERROR: Файл '{filename}' не найден"
        
        try:
            stat = os.stat(filepath)
            mime_type, _ = mimetypes.guess_type(filepath)
            mime_type = mime_type or 'unknown'
            size = stat.st_size
            ctime = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            
            return f"File: {filename}\nMIME: {mime_type}\nSize: {size} bytes\nCreated: {ctime}"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def handle_retr(self, filenames):
        """Подготовка файлов к передаче"""
        if not self.authenticated:
            return "ERROR: Требуется авторизация"
        
        files_data = []
        for filename in filenames:
            filepath = os.path.join(self.current_dir, filename)
            if not os.path.exists(filepath):
                files_data.append(f"ERROR: Файл '{filename}' не найден")
                continue
            
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                    # Кодируем в base64 для передачи по текстовому протоколу
                    import base64
                    encoded = base64.b64encode(content).decode('utf-8')
                    files_data.append(f"FILE:{filename}:{len(content)}:{encoded}")
            except Exception as e:
                files_data.append(f"ERROR: Ошибка чтения '{filename}': {str(e)}")
        
        return "\n".join(files_data)
    
    def handle_help(self):
        """Вывод справки"""
        help_text = """
Доступные команды:
  auth <user> <pass>   - Авторизация
  list                 - Список файлов в каталоге
  info <file>          - Информация о файле
  retr <file1> [file2] - Получить файлы
  exit                 - Выход
  help                 - Эта справка
"""
        return help_text
    
    def handle_command(self, command):
        """Обработка команд"""
        parts = command.strip().split()
        if not parts:
            return "ERROR: Пустая команда"
        
        cmd = parts[0].lower()
        
        if cmd == 'auth':
            if len(parts) != 3:
                return "ERROR: Использование: auth <user> <pass>"
            return self.handle_auth(parts[1], parts[2])
        
        elif cmd == 'list':
            return self.handle_list()
        
        elif cmd == 'info':
            if len(parts) != 2:
                return "ERROR: Использование: info <file>"
            return self.handle_info(parts[1])
        
        elif cmd == 'retr':
            if len(parts) < 2:
                return "ERROR: Использование: retr <file1> [file2] ..."
            return self.handle_retr(parts[1:])
        
        elif cmd == 'exit':
            self.authenticated = False
            self.current_user = None
            return "BYE: До свидания!"
        
        elif cmd == 'help':
            return self.handle_help()
        
        else:
            return f"ERROR: Неизвестная команда: {cmd}"
    
    def handle_client(self, client_socket, address):
        """Обработка клиентского соединения"""
        print(f"[+] Подключен клиент: {address}")
        
        try:
            # Отправляем приветственное сообщение
            welcome = "Добро пожаловать! Для начала работы используйте команду 'auth <user> <pass>'"
            client_socket.send(welcome.encode('utf-8'))
            
            while True:
                # Получаем команду от клиента
                data = client_socket.recv(4096).decode('utf-8').strip()
                if not data:
                    break
                
                print(f"[{address}] Команда: {data}")
                
                # Обрабатываем команду
                response = self.handle_command(data)
                
                # Отправляем ответ
                client_socket.send(response.encode('utf-8'))
                
                # Если команда exit, разрываем соединение
                if data.lower().startswith('exit'):
                    break
                    
        except Exception as e:
            print(f"[-] Ошибка с клиентом {address}: {e}")
        finally:
            client_socket.close()
            print(f"[-] Отключен клиент: {address}")
    
    def start(self):
        """Запуск сервера"""
        # Создаем сокет
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            # Привязываем сокет к адресу
            self.server_socket.bind((self.host, self.port))
            # Начинаем слушать соединения
            self.server_socket.listen(5)
            print(f"[*] Сервер запущен на {self.host}:{self.port}")
            print(f"[*] Текущий каталог: {self.current_dir}")
            print(f"[*] Файл паролей: {self.pass_file}")
            print("[*] Ожидание подключений...")
            
            while self.running:
                try:
                    # Принимаем соединение
                    client_socket, address = self.server_socket.accept()
                    
                    # Создаем поток для обработки клиента
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except KeyboardInterrupt:
                    print("\n[*] Остановка сервера...")
                    break
                except Exception as e:
                    print(f"[-] Ошибка: {e}")
                    continue
                    
        except Exception as e:
            print(f"[-] Ошибка запуска сервера: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def stop(self):
        """Остановка сервера"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

def main():
    server = SimpleProtocolServer()
    server.start()

if __name__ == '__main__':
    main()
