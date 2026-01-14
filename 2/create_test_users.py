#!/usr/bin/env python3
import hashlib
import os

def create_test_users():
    """Создание тестовых пользователей и структуры каталогов"""
    
    # Создаем каталоги
    os.makedirs("messages/user1", exist_ok=True)
    os.makedirs("messages/user2", exist_ok=True)
    
    # Создаем файл с паролями
    with open("pass", "w") as f:
        # Пароли хешируются MD5 (для тестовых целей)
        f.write(f"user1 {hashlib.md5('password1'.encode()).hexdigest()}\n")
        f.write(f"user2 {hashlib.md5('password2'.encode()).hexdigest()}\n")
        f.write(f"admin {hashlib.md5('admin123'.encode()).hexdigest()}\n")
    
    # Создаем тестовые сообщения
    with open("messages/user1/1.msg", "w") as f:
        f.write("Тестовое сообщение 1\n")
        f.write("Это первое тестовое сообщение для user1.\n")
    
    with open("messages/user1/2.msg", "w") as f:
        f.write("Второе сообщение\n")
        f.write("Это второе тестовое сообщение.\n")
    
    print("Тестовые пользователи созданы:")
    print("  user1:password1")
    print("  user2:password2")
    print("  admin:admin123")
    print("\nСтруктура каталогов создана в messages/")

if __name__ == "__main__":
    create_test_users()
