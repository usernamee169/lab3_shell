#!/usr/bin/env python3
"""
Скрипт для быстрого тестирования сервера
"""
import socket
import time

def test_commands():
    """Тестирование основных команд"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8888))
    
    # Получаем приветствие
    print(sock.recv(1024).decode())
    
    # Тестовая сессия
    commands = [
        "help",
        "auth test test123",
        "list",
        "send test",
        "Тестовое сообщение",
        "Первая строка",
        "Вторая строка",
        ".",
        "list",
        "read 1",
        "exit"
    ]
    
    for cmd in commands:
        # Ждем приглашение от сервера
        time.sleep(0.1)
        data = sock.recv(1024).decode()
        if data:
            print(f"Сервер: {data}", end='')
        
        # Отправляем команду
        print(f"> {cmd}")
        sock.send((cmd + "\n").encode())
    
    sock.close()

if __name__ == "__main__":
    test_commands()
