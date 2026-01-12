import socket
import os
import threading
from datetime import datetime

class SimpleServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.auth_file = 'pass.txt'
        self.load_auth_data()
    
    def load_auth_data(self):
        """Загрузка данных для авторизации"""
        self.users = {}
        try:
            with open(self.auth_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        user, pwd = line.split(':', 1)
                        self.users[user] = pwd
        except FileNotFoundError:
            # Создаем тестовых пользователей
            self.users = {'admin': '123', 'user': 'pass'}
    
    def handle_client(self, client_socket, addr):
        """Обработка одного клиента"""
        print(f"[+] Клиент подключен: {addr}")
        authenticated = False
        
        client_socket.send(b"Добро пожаловать! Используйте команды:\n"
                          b"auth <user> <pass>\n"
                          b"list\n"
                          b"info <file>\n"
                          b"retr <file>\n"
                          b"exit\n"
                          b"help\n")
        
        while True:
            try:
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break
                
                response = self.process_command(data, authenticated)
                client_socket.send(response.encode())
                
                if data.lower() == 'exit':
                    break
                    
                # После успешной авторизации
                if data.startswith('auth ') and "Успешная" in response:
                    authenticated = True
                    
            except Exception as e:
                print(f"Ошибка: {e}")
                break
        
        client_socket.close()
        print(f"[-] Клиент отключен: {addr}")
    
    def process_command(self, cmd, auth):
        """Обработка команд"""
        parts = cmd.split()
        if not parts:
            return "Ошибка: пустая команда\n"
        
        cmd_type = parts[0].lower()
        
        # Требуем авторизацию для всех команд кроме auth, help, exit
        if cmd_type not in ['auth', 'help', 'exit'] and not auth:
            return "Ошибка: требуется авторизация (auth user pass)\n"
        
        if cmd_type == 'auth':
            return self.cmd_auth(parts[1:])
        elif cmd_type == 'list':
            return self.cmd_list()
        elif cmd_type == 'info':
            return self.cmd_info(parts[1:])
        elif cmd_type == 'retr':
            return self.cmd_retr(parts[1:])
        elif cmd_type == 'help':
            return self.cmd_help()
        elif cmd_type == 'exit':
            return "До свидания!\n"
        else:
            return f"Неизвестная команда: {cmd_type}\n"
    
    def cmd_auth(self, args):
        """Команда auth"""
        if len(args) != 2:
            return "Использование: auth <user> <pass>\n"
        
        user, pwd = args
        if user in self.users and self.users[user] == pwd:
            return f"Успешная авторизация! Добро пожаловать, {user}!\n"
        return "Ошибка: неверный логин или пароль\n"
    
    def cmd_list(self):
        """Команда list"""
        try:
            files = os.listdir('.')
            result = "Файлы в каталоге:\n"
            for f in files:
                if os.path.isfile(f):
                    size = os.path.getsize(f)
                    result += f"  {f} ({size} байт)\n"
            return result if result else "Каталог пуст\n"
        except Exception as e:
            return f"Ошибка: {e}\n"
    
    def cmd_info(self, args):
        """Команда info"""
        if len(args) != 1:
            return "Использование: info <имя_файла>\n"
        
        filename = args[0]
        if not os.path.exists(filename):
            return f"Файл {filename} не найден\n"
        
        try:
            stat = os.stat(filename)
            import mimetypes
            mime_type = mimetypes.guess_type(filename)[0] or 'неизвестно'
            created = datetime.fromtimestamp(stat.st_ctime)
            
            info = (f"Информация о файле {filename}:\n"
                   f"  MIME тип: {mime_type}\n"
                   f"  Размер: {stat.st_size} байт\n"
                   f"  Создан: {created}\n")
            return info
        except Exception as e:
            return f"Ошибка: {e}\n"
    
    def cmd_retr(self, args):
        """Команда retr"""
        if not args:
            return "Использование: retr <file1> [file2 ...]\n"
        
        result = ""
        for filename in args:
            if not os.path.exists(filename):
                result += f"Файл {filename} не найден\n"
                continue
            
            try:
                result += f"Начинаю передачу {filename}\n"
                # В реальной реализации здесь была бы передача файла
                # Для простоты просто сообщаем о готовности
                result += f"Файл {filename} готов к передаче\n"
            except Exception as e:
                result += f"Ошибка передачи {filename}: {e}\n"
        
        return result
    
    def cmd_help(self):
        """Команда help"""
        help_text = """Справка по командам:
  auth <user> <pass> - Авторизация
  list               - Список файлов
  info <file>        - Информация о файле
  retr <file>        - Получить файл
  exit               - Выход
  help               - Эта справка
"""
        return help_text
    
    def start(self):
        """Запуск сервера"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"[*] Сервер запущен на {self.host}:{self.port}")
        print("[*] Ожидание подключений...")
        
        while True:
            try:
                client, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client, addr))
                thread.start()
            except KeyboardInterrupt:
                print("\n[*] Сервер остановлен")
                break

if __name__ == "__main__":
    # Создаем тестовые файлы
    test_files = ['test1.txt', 'test2.txt', 'data.json']
    for f in test_files:
        if not os.path.exists(f):
            with open(f, 'w') as file:
                file.write(f"Тестовое содержимое файла {f}\n" * 3)
    
    # Создаем файл с паролями если его нет
    if not os.path.exists('pass.txt'):
        with open('pass.txt', 'w') as f:
            f.write("admin:123\n")
            f.write("user:pass\n")
    
    # Запускаем сервер
    server = SimpleServer()
    server.start()
