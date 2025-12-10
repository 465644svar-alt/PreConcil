@echo off
echo Запуск приложения менеджера нейросетей
echo.

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Запуск приложения
python main_app.py

pause