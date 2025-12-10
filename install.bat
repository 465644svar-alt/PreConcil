@echo off
echo Установка приложения менеджера нейросетей v3.0
echo.
echo Поддерживаемые нейросети:
echo - OpenAI GPT
echo - Anthropic Claude
echo - DeepSeek
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
echo Для запуска приложения выполните:
echo 1. Активируйте виртуальное окружение: venv\Scripts\activate
echo 2. Запустите приложение: python main_app.py
echo.
echo Или запустите run.bat
echo.
pause