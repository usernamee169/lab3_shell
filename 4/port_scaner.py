#!/usr/bin/env python3
"""
Упрощенный сканер портов
"""

import socket
import sys

# Основные порты для проверки
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP Proxy"
}

def scan_port(host, port):
    """Проверка одного порта"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    
    result = sock.connect_ex((host, port))
    sock.close()
    
    return result == 0

def simple_scanner():
    if len(sys.argv) != 2:
        print("Использование: python3 simple_scanner.py <хост>")
        print("Пример: python3 simple_scanner.py localhost")
        sys.exit(1)
    
    host = sys.argv[1]
    
    print(f"Сканирование хоста: {host}")
    print("-" * 40)
    
    for port, service in common_ports.items():
        if scan_port(host, port):
            print(f"✓ Порт {port:5} ({service}) - ОТКРЫТ")
        else:
            print(f"✗ Порт {port:5} ({service}) - ЗАКРЫТ")

if __name__ == "__main__":
    simple_scanner()
