#!/usr/bin/env python3
import socket

def send_command(sock, command):
    sock.send(command.encode('utf-8'))
    response = sock.recv(1024).decode('utf-8')
    print(f"Ответ: {response}")
    return response

def main():
    host = "localhost"
    port = 12345
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((host, port))
        print("Подключено к серверу")
        
        # Тестовые команды
        commands = [
            "LOGIN admin password123",  # Успешный вход
            "STORE 1 -3 2",             # Сохраняем коэффициенты
            "SOLVE",                     # Решаем с сохраненными
            "SOLVE 1 -5 6",              # Решаем с новыми
            "SOLVE 0 0 0",               # Нет коэффициентов (линейное)
            "SOLVE",                     # Решаем снова
        ]
        
        for cmd in commands:
            print(f"\nОтправка: {cmd}")
            response = send_command(sock, cmd)
            
            # Можно добавить обработку ошибок
            if response.startswith("1"):
                print("Ошибка авторизации!")
            elif response.startswith("2"):
                print("Коэффициенты не указаны!")
            elif response.startswith("3"):
                print("Синтаксическая ошибка!")
                
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
