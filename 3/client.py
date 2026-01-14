import socket
import sys

class QuadraticClient:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """Подключение к серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Подключено к {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def send_command(self, command):
        """Отправка команды серверу"""
        try:
            self.socket.send(command.encode('utf-8'))
            response = self.socket.recv(1024).decode('utf-8')
            return response
        except Exception as e:
            return f"Ошибка: {e}"
    
    def interactive_mode(self):
        """Интерактивный режим"""
        print("\n=== Клиент для решения квадратных уравнений ===")
        print("Команды:")
        print("  LOGIN имя пароль    - авторизация")
        print("  STORE A B C         - сохранение коэффициентов")
        print("  SOLVE               - решение с сохраненными коэффициентами")
        print("  SOLVE A B C         - решение с указанными коэффициентами")
        print("  QUIT                - выход")
        print("  HELP                - помощь")
        print("=" * 50)
        
        while True:
            try:
                command = input("\n> ").strip()
                if not command:
                    continue
                
                if command.upper() == "QUIT":
                    print("Выход...")
                    break
                elif command.upper() == "HELP":
                    print("Примеры использования:")
                    print("  LOGIN admin admin123")
                    print("  STORE 1 -3 2")
                    print("  SOLVE")
                    print("  SOLVE 1 0 -4")
                    continue
                
                response = self.send_command(command)
                print(f"Ответ: {response}")
                
            except KeyboardInterrupt:
                print("\nВыход...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
    
    def close(self):
        """Закрытие соединения"""
        if self.socket:
            self.socket.close()

if __name__ == "__main__":
    # Определение хоста и порта
    host = '127.0.0.1'
    port = 8888
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # Запуск клиента
    client = QuadraticClient(host, port)
    if client.connect():
        client.interactive_mode()
        client.close()
