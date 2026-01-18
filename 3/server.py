import socket
import threading
import math

class AuthSystem:
    
    def __init__(self):
        
        self.users = {
            "user1": "pass1",
            "user2": "pass2",
            "user3": "pass3"
        }
        self.active_sessions = {}
    
    def login(self, client_id, username, password):
        
        if username in self.users and self.users[username] == password:
            self.active_sessions[client_id] = username
            return True
        return False
    
    def is_authenticated(self, client_id):
        
        return client_id in self.active_sessions
    
    def logout(self, client_id):
        
        if client_id in self.active_sessions:
            del self.active_sessions[client_id]

class QuadraticEquationServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.auth = AuthSystem()
        self.client_data = {}
        
    def solve_quadratic(self, a, b, c):
        """ ax^2 + bx + c = 0"""
        try:
            a = float(a)
            b = float(b)
            c = float(c)
        except ValueError:
            return "Синтаксическая ошибка"  
            
       
        if a == 0:
            if b == 0:
                if c == 0:
                    return "Бесконечное количество решений"  
                else:
                    return "Нет решений"
            else:
                x = -c / b
                return f"Одно решение - {x}"
        
        
        discriminant = b*b - 4*a*c
        
        if discriminant > 0:
            sqrt_disc = math.sqrt(discriminant)
            x1 = (-b + sqrt_disc) / (2*a)
            x2 = (-b - sqrt_disc) / (2*a)
            return f"Два решения - {x1} и {x2}"
        elif discriminant == 0:
            x = -b / (2*a)
            return f"Одно решение - {x}"
        else:
            return "Нет действительных решений"
    
    def handle_client(self, client_socket, client_address):
        
        client_id = f"{client_address[0]}:{client_address[1]}"
        print(f"Новое подключение: {client_id}")
        
        try:
            while True:
                
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break
                
                print(f"[{client_id}] Получено: {data}")
                
                
                parts = data.split()
                command = parts[0].upper() if parts else ""
                
                
                if command == "LOGIN":
                    if len(parts) != 3:
                        response = "Синтаксическая ошибка"  
                    else:
                        username = parts[1]
                        password = parts[2]
                        if self.auth.login(client_id, username, password):
                            response = "Авторизация успешна"
                        else:
                            response = "Сначала авторизуйтесь"  
                
                
                elif command == "STORE":
                    if not self.auth.is_authenticated(client_id):
                        response = "Сначала авторизуйтесь"  
                    elif len(parts) != 4:
                        response = "Синтаксическая ошибка"  
                    else:
                        try:
                            a, b, c = map(float, parts[1:4])
                            self.client_data[client_id] = (a, b, c)
                            response =f"Данные записаны:{a,b,c}"
                        except ValueError:
                            response = "Синтаксическая ошибка"  
                
                
                elif command == "SOLVE":
                    if not self.auth.is_authenticated(client_id):
                        response = "Сначала авторизуйтесь"
                    else:
                        
                        if len(parts) == 4:
                            response = self.solve_quadratic(parts[1], parts[2], parts[3])
                        
                        elif len(parts) == 1:
                            if client_id in self.client_data:
                                a, b, c = self.client_data[client_id]
                                response = self.solve_quadratic(a, b, c)
                            else:
                                response = "Коэффициенты не указаны"  
                        else:
                            response = "Синтаксическая ошибка"  
                
                
                else:
                    response = "Синтаксическая ошибка"  
                
                
                client_socket.send(response.encode('utf-8'))
                print(f"[{client_id}] Отправлено: {response}")
        
        except Exception as e:
            print(f"Ошибка с клиентом {client_id}: {e}")
        finally:
            
            self.auth.logout(client_id)
            if client_id in self.client_data:
                del self.client_data[client_id]
            client_socket.close()
            print(f"Отключение: {client_id}")
    
    def start(self):
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Сервер запущен на {self.host}:{self.port}")
            print("Ожидание подключений")
            
            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
        
        except KeyboardInterrupt:
            print("\nОстановка сервера")
        except Exception as e:
            print(f"Ошибка сервера: {e}")
        finally:
            server_socket.close()


class TestClient:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
    
    def send_command(self, command):
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            sock.send(command.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            return response
        except Exception as e:
            return f"Ошибка: {e}"

if __name__ == "__main__":
    server = QuadraticEquationServer()
    server.start()
