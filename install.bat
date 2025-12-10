@echo off
echo Установка приложения менеджера нейросетей v1.2
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не установлен или не добавлен в PATH
    echo Установите Python с официального сайта: https://python.org
    pause
    exit /b 1
)

REM Создание виртуального окружения
echo Создание виртуального окружения...
python -m venv venv

REM Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo Установка зависимостей...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Установка завершена!
echo.
echo Новые возможности:
echo 1. Проверка соединения с нейросетями перед отправкой
echo 2. Уведомления при ошибках подключения
echo 3. Уникальные имена файлов с суффиксами (1), (2) и т.д.
echo 4. Вкладка со статусом соединения
echo.
echo Для запуска приложения выполните:
echo 1. Активируйте виртуальное окружение: venv\Scripts\activate
echo 2. Запустите приложение: python main_app.py
echo.
pause