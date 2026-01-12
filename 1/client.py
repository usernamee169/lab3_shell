import socket

class SimpleClient:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
    
    def connect(self):
        """Подключение и интерактивный режим"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            sock.connect((self.host, self.port))
            print(f"[+] Подключено к {self.host}:{self.port}")
            
            # Получаем приветствие
            welcome = sock.recv(1024).decode()
            print(welcome)
            
            # Цикл команд
            while True:
                cmd = input("> ").strip()
                if not cmd:
                    continue
                
                sock.send(cmd.encode())
                
                if cmd.lower() == 'exit':
                    response = sock.recv(1024).decode()
                    print(response)
                    break
                
                # Получаем ответ
                response = sock.recv(4096).decode()
                print(response)
                
        except ConnectionRefusedError:
            print("[-] Не удалось подключиться к серверу")
        except Exception as e:
            print(f"[-] Ошибка: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    client = SimpleClient()
    client.connect()
