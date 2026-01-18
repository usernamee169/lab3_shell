import socket
import sys

HOST = '127.0.0.1'
PORT = 8888

def send_utf8(sock, message):
    """Отправка сообщения в UTF-8"""
    sock.send(message.encode('utf-8'))

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
                
                send_utf8(s, command)
                
                if command.startswith("send "):
                    # Обработка команды send
                    response = s.recv(1024).decode('utf-8')
                    print(response, end='')
                    if "Введите тему" in response:
                        subject = input()
                        send_utf8(s, subject)
                    
                    response = s.recv(1024).decode('utf-8')
                    print(response, end='')
                    if "Введите текст" in response:
                        while True:
                            line = input()
                            send_utf8(s, line)
                            if line == ".":
                                break
                
                # Получаем ответ от сервера
                response = s.recv(4096).decode('utf-8')
                print(response, end='')
                
                if command == "exit":
                    break
                    
        except KeyboardInterrupt:
            print("\nВыход...")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
