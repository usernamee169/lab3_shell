#!/bin/bash
# Простой тестовый клиент

echo "Тестирование сервера квадратных уравнений"
echo "=========================================="

# Функция для отправки команды
send_cmd() {
    echo "$1" | nc -N localhost 12345
}

echo "1. Попытка входа с неверными данными:"
send_cmd "LOGIN wrong wrong"

echo -e "\n2. Вход с правильными данными:"
send_cmd "LOGIN admin password123"

echo -e "\n3. Сохраняем коэффициенты:"
send_cmd "STORE 1 -5 6"

echo -e "\n4. Решаем с сохраненными коэффициентами:"
send_cmd "SOLVE"

echo -e "\n5. Решаем с новыми коэффициентами:"
send_cmd "SOLVE 1 0 -4"

echo -e "\n6. Ошибка синтаксиса:"
send_cmd "WRONG COMMAND"
