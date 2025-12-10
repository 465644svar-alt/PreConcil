@echo off
echo Установка менеджера нейросетей v5.0
echo Поддержка БЕСПЛАТНЫХ нейросетей: Groq, OpenRouter, Hugging Face
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не установлен
    echo Скачайте с: https://python.org
    pause
    exit /b 1
)

REM Создание виртуального окружения
echo Создание виртуального окружения...
python -m venv venv

REM Активация
echo Активация окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo Установка зависимостей...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo =========================================
echo УСПЕШНАЯ УСТАНОВКА!
echo =========================================
echo.
echo ПОЛУЧИТЕ БЕСПЛАТНЫЕ КЛЮЧИ:
echo 1. Groq: https://console.groq.com/keys
echo 2. OpenRouter: https://openrouter.ai/keys
echo 3. Hugging Face: https://huggingface.co/settings/tokens
echo.
echo ЗАПУСК ПРИЛОЖЕНИЯ:
echo 1. Активируйте окружение: venv\Scripts\activate
echo 2. Запустите: python main_app.py
echo ИЛИ просто запустите run.bat
echo.
pause