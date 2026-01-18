#!/usr/bin/env python3
import os
import socket
import mimetypes
import datetime
import sys
import threading
import time

class ProtocolServer:
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
    
    def auth(self, username, password):
        users = self.load_users()
        if username in users and users[username] == password:
            self.authenticated = True
            self.current_user = username
            return "Авторизация прошла. \nВведите 'help' для просмотра доступных команд."
        else:
            return "Неверное имя пользователя или пароль"
    
    def list(self):
        if not self.authenticated:
            return "Требуется авторизация"
        
        files = os.listdir(self.current_dir)
        result = []
        for file in files:
            if os.path.isfile(file):
                result.append(f"FILE: {file}")
            else:
                result.append(f"DIR:  {file}")
        return "\n".join(result) if result else "Каталог пуст"
    
    def info(self, filename):
        if not self.authenticated:
            return "Требуется авторизация"
        
        filepath = os.path.join(self.current_dir, filename)
        if not os.path.exists(filepath):
            return f"Файл '{filename}' не найден"
        
        try:
            stat = os.stat(filepath)
            mime_type, _ = mimetypes.guess_type(filepath)
            mime_type = mime_type or 'unknown'
            size = stat.st_size
            ctime = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            
            return f"File: {filename}\nMIME: {mime_type}\nSize: {size} bytes\nCreated: {ctime}"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def retr(self, filenames):
        if not self.authenticated:
            return "Функция не реализована"
        
           
    def help(self):
        help_text = """
Доступные команды:
  auth (user) (pass)   - Авторизация
  list                 - Список файлов в каталоге
  info (file)          - Информация о файле
  retr (file1) (file2) - Получить файлы
  exit                 - Выход
  help                 - Эта справка
"""
        return help_text
    
    def command(self, command):
        parts = command.strip().split()
        if not parts:
            return "Пустая команда"
        
        cmd = parts[0].lower()
        
        if cmd == 'auth':
            if len(parts) != 3:
                return "Ввод формата: auth (user) (pass)"
            return self.auth(parts[1], parts[2])
        
        elif cmd == 'list':
            return self.list()
        
        elif cmd == 'info':
            if len(parts) != 2:
                return "Ввод формата: info (file)"
            return self.info(parts[1])
        
        elif cmd == 'retr':
            if len(parts) < 2:
                return "Ввод фрмата: retr (file1) (file2) ..."
            return self.retr(parts[1:])
        
        elif cmd == 'exit':
            self.authenticated = False
            self.current_user = None
            return "Работа завершена"
        
        elif cmd == 'help':
            return self.help()
        
        else:
            return f"Неизвестная команда"
    
    def client(self, client_socket, address):
        print(f"Подключен клиент: {address}")
        
        try:
            welcome = "Для начала работы авторизуйтесь командой 'auth (user) (pass)'"
            client_socket.send(welcome.encode('utf-8'))
            
            while True:
                data = client_socket.recv(4096).decode('utf-8').strip()
                if not data:
                    break
                
                print(f"[{address}] Команда: {data}")
               
                response = self.command(data)
                
             
                client_socket.send(response.encode('utf-8'))
                
                if data.lower().startswith('exit'):
                    break
                    
        except Exception as e:
            print(f"Ошибка с клиентом {address}: {e}")
        finally:
            client_socket.close()
            print(f"Клиент {address} отключен")
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Сервер запущен на {self.host}:{self.port}")
            print(f"Текущий каталог: {self.current_dir}")
            print(f"Файл паролей: {self.pass_file}")
                        
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    
                    
                    client_thread = threading.Thread(
                        target=self.client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except KeyboardInterrupt:
                    print("\nОстановка сервера")
                    break
                except Exception as e:
                    print(f"Ошибка: {e}")
                    continue
                    
        except Exception as e:
            print(f"Ошибка запуска сервера: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()

def main():
    server = ProtocolServer()
    server.start()

if __name__ == '__main__':
    main()
