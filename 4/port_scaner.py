#!/usr/bin/env python3
"""
Запуск: sudo python3 port_scaner.py <ip_адрес>
"""

import socket
import sys
import concurrent.futures
from datetime import datetime

# Словарь известных портов и их протоколов
KNOWN_PORTS = {
    # Системные порты
    20: "FTP (Data Transfer)",
    21: "FTP (Control)",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP Server",
    68: "DHCP Client",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    111: "RPC",
    123: "NTP",
    135: "MS RPC",
    137: "NetBIOS Name Service",
    138: "NetBIOS Datagram Service",
    139: "NetBIOS Session Service",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP Trap",
    179: "BGP",
    194: "IRC",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    514: "Syslog",
    515: "LPD/LPR",
    587: "SMTP Submission",
    631: "IPP",
    636: "LDAPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS Proxy",
    1433: "MS SQL Server",
    1521: "Oracle DB",
    1723: "PPTP",
    1900: "UPnP",
    2049: "NFS",
    2082: "cPanel",
    2083: "cPanel SSL",
    2086: "WHM",
    2087: "WHM SSL",
    2095: "Webmail",
    2096: "Webmail SSL",
    2181: "ZooKeeper",
    2375: "Docker",
    2376: "Docker SSL",
    3000: "Node.js",
    3306: "MySQL",
    3389: "RDP",
    3690: "SVN",
    4333: "mSQL",
    4443: "HTTPS Alternative",
    4505: "SaltStack",
    4506: "SaltStack",
    4848: "GlassFish",
    5000: "UPnP",
    5432: "PostgreSQL",
    5601: "Kibana",
    5672: "RabbitMQ",
    5900: "VNC",
    5938: "TeamViewer",
    5984: "CouchDB",
    6379: "Redis",
    6667: "IRC",
    7001: "WebLogic",
    7002: "WebLogic SSL",
    8000: "HTTP Alternative",
    8008: "HTTP Alternative",
    8080: "HTTP Proxy",
    8081: "HTTP Proxy",
    8443: "HTTPS Alternative",
    8888: "HTTP Alternative",
    9000: "SonarQube",
    9092: "Apache Kafka",
    9100: "JetDirect",
    9200: "Elasticsearch",
    9300: "Elasticsearch",
    10000: "Webmin",
    11211: "Memcached",
    15672: "RabbitMQ Management",
    25565: "Minecraft",
    27017: "MongoDB",
    28017: "MongoDB HTTP",
    50000: "SAP",
    50070: "Hadoop NameNode",
    61616: "ActiveMQ"
}



def save_results(ip, open_ports, filename="scan_results.txt"):
    with open(filename, 'w') as f:
        f.write(f"Результаты сканирования {ip}\n")
        f.write(f"Время: {datetime.now()}\n")
        f.write("-" * 50 + "\n")
        for port, service, banner in open_ports:
            f.write(f"Порт {port}: {service}\n")
            if banner:
                f.write(f"  Баннер: {banner[:200]}\n")

def scan_port(ip, port, timeout=1):
    """Сканирование одного порта"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            # Пробуем получить баннер
            try:
                sock.send(b"GET / HTTP/1.0\r\n\r\n")
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                if banner:
                    return port, True, banner[:100]
            except:
                banner = None
            
            return port, True, banner
        sock.close()
    except:
        pass
    return port, False, None

def identify_service(port, banner=None):
    """Определение сервиса на порту"""
    if port in KNOWN_PORTS:
        return KNOWN_PORTS[port]
    
    # Попытка определить по баннеру
    if banner:
        banner_lower = banner.lower()
        if 'apache' in banner_lower or 'httpd' in banner_lower:
            return "Apache HTTP Server"
        elif 'nginx' in banner_lower:
            return "Nginx"
        elif 'iis' in banner_lower or 'microsoft' in banner_lower:
            return "Microsoft IIS"
        elif 'openssh' in banner_lower:
            return "OpenSSH"
        elif 'mysql' in banner_lower:
            return "MySQL"
        elif 'postgresql' in banner_lower:
            return "PostgreSQL"
    
    return "Unknown Service"

def scan_ports(ip, start_port=1, end_port=1024, max_threads=100):
    """Многопоточное сканирование портов"""
    open_ports = []
    
    print(f"\n[+] Начинаем сканирование {ip}")
    print(f"[+] Диапазон портов: {start_port}-{end_port}")
    print(f"[+] Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_port, ip, port): port 
                   for port in range(start_port, end_port + 1)}
        
        for future in concurrent.futures.as_completed(futures):
            port, is_open, banner = future.result()
            if is_open:
                service = identify_service(port, banner)
                open_ports.append((port, service, banner))
                status = "OPEN"
                print(f"[{status:^7}] Порт {port:5} - {service}")
                if banner:
                    print(f"       Баннер: {banner}")
    
    return open_ports

def main():
    if len(sys.argv) < 2:
        print("Использование: sudo python3 port_scanner.py <IP-адрес>")
        print("Пример: sudo python3 port_scanner.py 192.168.1.1")
        print("\nОпции:")
        print("  <IP-адрес>         IP-адрес для сканирования")
        print("  -p <порт>          Сканировать определенный порт")
        print("  -r <начало-конец>  Диапазон портов (по умолчанию: 1-1024)")
        print("  -t <потоки>        Количество потоков (по умолчанию: 100)")
        print("\nПримеры:")
        print("  sudo python3 port_scanner.py 192.168.1.1 -p 80")
        print("  sudo python3 port_scanner.py 192.168.1.1 -r 20-1000")
        sys.exit(1)
    
    ip = sys.argv[1]
    start_port = 1
    end_port = 1024
    max_threads = 100
    
    # Парсинг аргументов
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "-p" and i + 1 < len(sys.argv):
            start_port = end_port = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "-r" and i + 1 < len(sys.argv):
            port_range = sys.argv[i + 1].split("-")
            start_port = int(port_range[0])
            end_port = int(port_range[1]) if len(port_range) > 1 else start_port
            i += 2
        elif sys.argv[i] == "-t" and i + 1 < len(sys.argv):
            max_threads = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1
    
    try:
        open_ports = scan_ports(ip, start_port, end_port, max_threads)
        
        print("-" * 60)
        print(f"\n[+] Сканирование завершено в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[+] Найдено открытых портов: {len(open_ports)}")
        
        if open_ports:
            print("\nОтчет:")
            for port, service, banner in open_ports:
                print(f"  Порт {port}: {service}")
        
    except KeyboardInterrupt:
        print("\n[!] Сканирование прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
