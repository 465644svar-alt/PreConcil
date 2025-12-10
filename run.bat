@echo off
echo Запуск менеджера нейросетей v5.0
echo БЕСПЛАТНЫЕ нейросети: Groq, OpenRouter, Hugging Face
echo.

REM Активация окружения
call venv\Scripts\activate.bat

REM Запуск приложения
python main_app.py

pause