#!/usr/bin/env python3
import socket
import threading
import math

# Простая база пользователей (логин: пароль)
users = {
    "admin": "password123",
    "user1": "pass123",
    "test": "test"
}

# Словарь для хранения коэффициентов для каждого клиента
client_data = {}

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, address):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.username = None
        self.logged_in = False
        self.coefficients = None
        
    def run(self):
        print(f"Новое подключение: {self.address}")
        
        try:
            while True:
                data = self.client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break
                    
                print(f"Получено от {self.address}: {data}")
                response = self.process_command(data)
                self.client_socket.send(response.encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка с клиентом {self.address}: {e}")
        finally:
            print(f"Соединение с {self.address} закрыто")
            self.client_socket.close()
            
    def process_command(self, command):
        parts = command.strip().split()
        
        if not parts:
            return "3"
            
        cmd = parts[0].upper()
        
        # Команда LOGIN
        if cmd == "LOGIN" and len(parts) >= 3:
            username = parts[1]
            password = parts[2]
            
            if username in users and users[username] == password:
                self.username = username
                self.logged_in = True
                print(f"Пользователь {username} вошел в систему")
                return "0"
            else:
                return "1"
                
        # Команда STORE
        elif cmd == "STORE" and len(parts) == 4:
            if not self.logged_in:
                return "1"
            
            try:
                a = float(parts[1])
                b = float(parts[2])
                c = float(parts[3])
                self.coefficients = (a, b, c)
                return "0"
            except ValueError:
                return "3"
                
        # Команда SOLVE с параметрами
        elif cmd == "SOLVE" and len(parts) == 4:
            if not self.logged_in:
                return "1"
            
            try:
                a = float(parts[1])
                b = float(parts[2])
                c = float(parts[3])
                return self.solve_equation(a, b, c)
            except ValueError:
                return "3"
                
        # Команда SOLVE без параметров (используем сохраненные)
        elif cmd == "SOLVE" and len(parts) == 1:
            if not self.logged_in:
                return "1"
            
            if self.coefficients is None:
                return "2"
            
            a, b, c = self.coefficients
            return self.solve_equation(a, b, c)
            
        else:
            return "3"
    
    def solve_equation(self, a, b, c):
        if a == 0:
            return "0 Линейное уравнение: x = " + str(-c/b)
        
        discriminant = b**2 - 4*a*c
        
        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            return f"0 Два корня: x1 = {x1:.3f}, x2 = {x2:.3f}"
        elif discriminant == 0:
            x = -b / (2*a)
            return f"0 Один корень: x = {x:.3f}"
        else:
            real_part = -b / (2*a)
            imaginary_part = math.sqrt(-discriminant) / (2*a)
            return f"0 Комплексные корни: x1 = {real_part:.3f} + {imaginary_part:.3f}i, x2 = {real_part:.3f} - {imaginary_part:.3f}i"

def main():
    host = "0.0.0.0"
    port = 12345
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Сервер запущен на {host}:{port}")
        print("Ожидание подключений...")
        
        while True:
            client_socket, address = server_socket.accept()
            handler = ClientHandler(client_socket, address)
            handler.start()
            
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
