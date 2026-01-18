import socket
import sys

HOST = '127.0.0.1'  # Для тестирования на той же машине
PORT = 8888

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Подключено к серверу")
        print("Введите команды:")
        
        try:
            while True:
                command = input("> ").strip()
                if not command:
                    continue
                
                s.sendall(command.encode())
                
                if command.startswith("send "):
                    # Обработка команды send
                    print(s.recv(1024).decode(), end='')
                    subject = input()
                    s.sendall(subject.encode())
                    
                    print(s.recv(1024).decode(), end='')
                    while True:
                        line = input()
                        s.sendall(line.encode())
                        if line == ".":
                            break
                
                # Получаем ответ от сервера
                response = s.recv(4096).decode()
                print(response, end='')
                
                if command == "exit":
                    break
                    
        except KeyboardInterrupt:
            print("\nВыход...")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
