#!/usr/bin/env python3
import socket
import sys

def main():
    if len(sys.argv) != 3:
        print("Использование: python client.py хост порт")
        return
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((host, port))
        
        # Получаем приветствие
        print(sock.recv(1024).decode(), end='')
        
        while True:
            # Показываем ответ сервера
            try:
                data = sock.recv(1024).decode()
                if not data:
                    break
                print(data, end='')
                
                # Если сервер ждет ввод (символ > или :)
                if data.endswith('> ') or ':' in data or '\n' not in data:
                    user_input = input()
                    sock.send((user_input + "\n").encode())
            except:
                break
                
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
