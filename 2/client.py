#!/usr/bin/env python3
import socket
import sys

class MessageClient:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """Подключение к серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print("Подключение к серверу установлено")
            
            # Получаем приветственное сообщение
            data = self.socket.recv(1024).decode()
            print(data, end='')
            
            self.interactive_mode()
            
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if self.socket:
                self.socket.close()
    
    def interactive_mode(self):
        """Интерактивный режим работы с сервером"""
        buffer = ""
        
        while True:
            # Ждем данные от сервера (включая приглашение)
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                
                # Если в буфере есть полная строка с приглашением, показываем ее
                if '>' in buffer or '\n' in buffer:
                    print(buffer, end='')
                    
                    # Если это приглашение для ввода (заканчивается на '>')
                    if buffer.strip().endswith('>'):
                        # Получаем ввод от пользователя
                        user_input = input()
                        self.socket.sendall((user_input + '\n').encode())
                    
                    buffer = ""
            
            except KeyboardInterrupt:
                print("\nОтключение от сервера...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
                break

if __name__ == "__main__":
    client = MessageClient()
    client.connect()
