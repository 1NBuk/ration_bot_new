#!/bin/bash

echo "Установка зависимостей"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Ошибка при установке зависимостей"
    exit 1
fi

echo "Запуск тестов"
pytest test_bot.py

if [ $? -ne 0 ]; then
    echo "Тесты не пройдены. Остановка запуска."
    exit 1
fi

echo "Запуск бота"
python bot.py
