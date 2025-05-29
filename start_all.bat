@echo off
cd /d %~dp0
echo [*] Активация виртуального окружения...
call venv\Scripts\activate.bat

echo [*] Запуск main.py в новом окне...
start "Main Script" cmd /k python cli_app.py

echo [*] Запуск FastAPI сервера...
start http://127.0.0.1:8000/docs
python -m uvicorn api_server:app --reload

pause
