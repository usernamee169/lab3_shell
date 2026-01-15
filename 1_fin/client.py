#!/usr/bin/env python3
import socket
import sys
import base64

class ProtocolClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            
            welcome = self.socket.recv(4096).decode('utf-8')
            print(f"Сервер: {welcome}")
            
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def send_command(self, command):
        try:
            self.socket.send(command.encode('utf-8'))
            response = self.socket.recv(65536).decode('utf-8')
            return response
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def interactive_mode(self):
        if not self.connect():
            return
        
        try:
            while True:
                command = input("> ").strip()
                if not command:
                    continue
                
                response = self.send_command(command)
                print(f"\n{response}")
                
                
                if command.lower().startswith('retr'):
                    self.save_files_from_response(response)
                
                if command.lower() == 'exit':
                    break
                    
        except KeyboardInterrupt:
            print("\nВыход")
        finally:
            self.socket.close()
    
    def save_files_from_response(self, response):
        
        lines = response.split('\n')
        for line in lines:
            if line.startswith('FILE:'):
                parts = line.split(':', 3)
                if len(parts) == 4:
                    filename = parts[1]
                    size = parts[2]
                    encoded_data = parts[3]
                    
                    try:
                        decoded_data = base64.b64decode(encoded_data)
                        with open(f"downloaded_{filename}", 'wb') as f:
                            f.write(decoded_data)
                        print(f"Файл сохранен: downloaded_{filename}")
                    except Exception as e:
                        print(f"Ошибка сохранения файла {filename}: {e}")

def main():
    if len(sys.argv) > 1:
        client = ProtocolClient()
        if client.connect():
            response = client.send_command(' '.join(sys.argv[1:]))
            print(response)
            client.socket.close()
    else:
        client = ProtocolClient()
        client.interactive_mode()

if __name__ == '__main__':
    main()
