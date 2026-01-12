#!/usr/bin/env python3
import socket
import os
import threading

class SimpleMessageServer:
    def __init__(self, port=8888):
        self.port = port
        self.users = {}
        self.load_users()
    
    def load_users(self):
        """Загрузка пользователей из файла pass"""
        if os.path.exists("pass"):
            with open("pass", "r") as f:
                for line in f:
                    if line.strip() and " " in line:
                        user, pwd = line.strip().split(" ", 1)
                        self.users[user] = pwd
    
    def save_user(self, user, pwd):
        """Сохранение нового пользователя"""
        with open("pass", "a") as f:
            f.write(f"{user} {pwd}\n")
        self.users[user] = pwd
    
    def check_auth(self, user, pwd):
        """Проверка авторизации"""
        return user in self.users and self.users[user] == pwd
    
    def handle_client(self, conn, addr):
        """Обработка одного клиента"""
        print(f"Новое подключение: {addr}")
        user = None
        
        conn.send(b"Сервер сообщений. Команда: help\n")
        
        while True:
            conn.send(b"> ")
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            
            parts = data.split()
            if not parts:
                continue
            
            cmd = parts[0].lower()
            
            # Команда help
            if cmd == "help":
                help_msg = """
Доступные команды:
auth user pass - Авторизация
list - Список сообщений
read N - Прочитать сообщение N
send user - Отправить сообщение
exit - Выход
help - Справка
"""
                conn.send(help_msg.encode())
            
            # Команда auth
            elif cmd == "auth":
                if len(parts) == 3:
                    user, pwd = parts[1], parts[2]
                    if self.check_auth(user, pwd):
                        conn.send(b"OK\n")
                        # Создаем директорию для сообщений
                        os.makedirs(f"messages/{user}", exist_ok=True)
                    else:
                        conn.send(b"ERROR: Неверный логин/пароль\n")
                        user = None
                else:
                    conn.send(b"ERROR: Используйте auth user pass\n")
            
            # Команда exit
            elif cmd == "exit":
                conn.send(b"До свидания\n")
                break
            
            # Проверка авторизации для остальных команд
            elif not user:
                conn.send(b"ERROR: Сначала авторизуйтесь\n")
            
            # Команда list
            elif cmd == "list":
                files = os.listdir(f"messages/{user}")
                msgs = []
                for f in files:
                    if f.endswith(".txt"):
                        try:
                            num = int(f[:-4])
                            with open(f"messages/{user}/{f}", "r") as msg_file:
                                subject = msg_file.readline().strip()
                            msgs.append((num, subject))
                        except:
                            continue
                
                msgs.sort()
                if msgs:
                    response = "\n".join([f"{num}: {subj}" for num, subj in msgs])
                    conn.send((response + "\n").encode())
                else:
                    conn.send(b"Нет сообщений\n")
            
            # Команда read
            elif cmd == "read" and len(parts) == 2:
                try:
                    num = parts[1]
                    with open(f"messages/{user}/{num}.txt", "r") as f:
                        content = f.read()
                    conn.send((content + "\n").encode())
                except:
                    conn.send(b"ERROR: Сообщение не найдено\n")
            
            # Команда send
            elif cmd == "send" and len(parts) == 2:
                to_user = parts[1]
                if to_user not in self.users:
                    conn.send(f"ERROR: Пользователь {to_user} не найден\n".encode())
                    continue
                
                conn.send(b"Тема: ")
                subject = conn.recv(1024).decode().strip()
                
                conn.send(b"Текст (окончание - точка на новой строке):\n")
                
                lines = []
                while True:
                    line = conn.recv(1024).decode().strip()
                    if line == ".":
                        break
                    lines.append(line)
                
                # Находим следующий номер
                os.makedirs(f"messages/{to_user}", exist_ok=True)
                files = os.listdir(f"messages/{to_user}")
                nums = [int(f[:-4]) for f in files if f.endswith(".txt")]
                next_num = max(nums) + 1 if nums else 1
                
                # Сохраняем сообщение
                with open(f"messages/{to_user}/{next_num}.txt", "w") as f:
                    f.write(subject + "\n")
                    f.write(f"От: {user}\n")
                    f.write("\n" + "\n".join(lines) + "\n")
                
                conn.send(f"Сообщение #{next_num} отправлено\n".encode())
            
            else:
                conn.send(b"ERROR: Неизвестная команда\n")
        
        conn.close()
        print(f"Отключение: {addr}")
    
    def start(self):
        """Запуск сервера"""
        # Создаем тестового пользователя, если нужно
        if not os.path.exists("pass"):
            self.save_user("test", "test123")
            print("Создан тестовый пользователь: test/test123")
        
        # Создаем директорию для сообщений
        os.makedirs("messages", exist_ok=True)
        
        # Запускаем сервер
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        
        print(f"Сервер запущен на порту {self.port}")
        print("Ожидание подключений...")
        
        try:
            while True:
                conn, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("\nСервер остановлен")
        finally:
            server.close()

# Запуск
if __name__ == "__main__":
    SimpleMessageServer(8888).start()
