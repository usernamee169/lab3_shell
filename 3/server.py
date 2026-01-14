import socket
import threading
import math

class AuthSystem:
    """Простая система аутентификации (для демонстрации)"""
    def __init__(self):
        # В реальном приложении храните хэши паролей
        self.users = {
            "admin": "admin123",
            "user": "password123",
            "test": "test123"
        }
        self.active_sessions = {}
    
    def login(self, client_id, username, password):
        """Аутентификация пользователя"""
        if username in self.users and self.users[username] == password:
            self.active_sessions[client_id] = username
            return True
        return False
    
    def is_authenticated(self, client_id):
        """Проверка аутентификации"""
        return client_id in self.active_sessions
    
    def logout(self, client_id):
        """Выход из системы"""
        if client_id in self.active_sessions:
            del self.active_sessions[client_id]

class QuadraticEquationServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.auth = AuthSystem()
        self.client_data = {}  # Хранение коэффициентов для каждого клиента
        
    def solve_quadratic(self, a, b, c):
        """Решение квадратного уравнения ax² + bx + c = 0"""
        try:
            a = float(a)
            b = float(b)
            c = float(c)
        except ValueError:
            return "3"  # Синтаксическая ошибка
            
        # Проверка на ноль
        if a == 0:
            if b == 0:
                if c == 0:
                    return "0 INF"  # Бесконечное количество решений
                else:
                    return "0 NO_ROOTS"  # Нет решений
            else:
                x = -c / b
                return f"0 ONE_ROOT {x}"
        
        # Вычисление дискриминанта
        discriminant = b*b - 4*a*c
        
        if discriminant > 0:
            sqrt_disc = math.sqrt(discriminant)
            x1 = (-b + sqrt_disc) / (2*a)
            x2 = (-b - sqrt_disc) / (2*a)
            return f"0 TWO_ROOTS {x1} {x2}"
        elif discriminant == 0:
            x = -b / (2*a)
            return f"0 ONE_ROOT {x}"
        else:
            return "0 NO_REAL_ROOTS"
    
    def handle_client(self, client_socket, client_address):
        """Обработка клиентского соединения"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        print(f"[+] Новое подключение: {client_id}")
        
        try:
            while True:
                # Получение данных от клиента
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break
                
                print(f"[{client_id}] Получено: {data}")
                
                # Разбор команды
                parts = data.split()
                command = parts[0].upper() if parts else ""
                
                # Обработка команды LOGIN
                if command == "LOGIN":
                    if len(parts) != 3:
                        response = "3"  # Синтаксическая ошибка
                    else:
                        username = parts[1]
                        password = parts[2]
                        if self.auth.login(client_id, username, password):
                            response = "0 LOGIN_SUCCESS"
                        else:
                            response = "1"  # Ошибка авторизации
                
                # Обработка команды STORE
                elif command == "STORE":
                    if not self.auth.is_authenticated(client_id):
                        response = "1"  # Ошибка авторизации
                    elif len(parts) != 4:
                        response = "3"  # Синтаксическая ошибка
                    else:
                        try:
                            a, b, c = map(float, parts[1:4])
                            self.client_data[client_id] = (a, b, c)
                            response = "0 STORED"
                        except ValueError:
                            response = "3"  # Синтаксическая ошибка
                
                # Обработка команды SOLVE (с коэффициентами)
                elif command == "SOLVE":
                    if not self.auth.is_authenticated(client_id):
                        response = "1"  # Ошибка авторизации
                    else:
                        # Если указаны коэффициенты
                        if len(parts) == 4:
                            response = self.solve_quadratic(parts[1], parts[2], parts[3])
                        # Если коэффициенты не указаны, используем сохраненные
                        elif len(parts) == 1:
                            if client_id in self.client_data:
                                a, b, c = self.client_data[client_id]
                                response = self.solve_quadratic(a, b, c)
                            else:
                                response = "2"  # Коэффициенты не указаны
                        else:
                            response = "3"  # Синтаксическая ошибка
                
                # Обработка неизвестной команды
                else:
                    response = "3"  # Синтаксическая ошибка
                
                # Отправка ответа клиенту
                client_socket.send(response.encode('utf-8'))
                print(f"[{client_id}] Отправлено: {response}")
        
        except Exception as e:
            print(f"[!] Ошибка с клиентом {client_id}: {e}")
        finally:
            # Очистка при отключении
            self.auth.logout(client_id)
            if client_id in self.client_data:
                del self.client_data[client_id]
            client_socket.close()
            print(f"[-] Отключение: {client_id}")
    
    def start(self):
        """Запуск сервера"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"[*] Сервер запущен на {self.host}:{self.port}")
            print("[*] Ожидание подключений...")
            
            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
        
        except KeyboardInterrupt:
            print("\n[*] Остановка сервера...")
        except Exception as e:
            print(f"[!] Ошибка сервера: {e}")
        finally:
            server_socket.close()

# Простой клиент для тестирования
class TestClient:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
    
    def send_command(self, command):
        """Отправка команды на сервер"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.send(command.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            return response
        except Exception as e:
            return f"Ошибка: {e}"
    
    def run_test(self):
        """Запуск тестовых команд"""
        print("=== Тестирование сервера ===")
        
        # Тест 1: Попытка решения без авторизации
        print("1. SOLVE без авторизации:")
        print(f"   Ответ: {self.send_command('SOLVE 1 2 1')}")
        
        # Тест 2: Авторизация
        print("\n2. Авторизация (правильная):")
        print(f"   Ответ: {self.send_command('LOGIN admin admin123')}")
        
        # Тест 3: Решение уравнения с коэффициентами
        print("\n3. Решение x² - 5x + 6 = 0:")
        print(f"   Ответ: {self.send_command('SOLVE 1 -5 6')}")
        
        # Тест 4: Сохранение коэффициентов
        print("\n4. Сохранение коэффициентов:")
        print(f"   Ответ: {self.send_command('STORE 1 0 -4')}")
        
        # Тест 5: Решение с сохраненными коэффициентами
        print("\n5. Решение с сохраненными коэффициентами:")
        print(f"   Ответ: {self.send_command('SOLVE')}")
        
        # Тест 6: Неправильная команда
        print("\n6. Неправильная команда:")
        print(f"   Ответ: {self.send_command('HELLO')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Запуск тестового клиента
        client = TestClient()
        client.run_test()
    else:
        # Запуск сервера
        server = QuadraticEquationServer()
        server.start()
