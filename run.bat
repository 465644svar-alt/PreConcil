@echo off
echo Запуск приложения менеджера нейросетей v3.0
echo Поддержка: OpenAI GPT, Anthropic Claude, DeepSeek
echo.

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Запуск приложения
python main_app.py

pause